from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import (
    Machine,
    ToolType,
    ToolChangeBatch,
    ToolChangeBatchItem,
    DailyProduction,
    WorkSession,
    ActivityLog,
    MaterialType,
    MaterialEntry,
    MaterialShipment,
)
from .serializers import (
    MachineDashboardSerializer,
    MachineDetailSerializer,
    MachineWithToolTypesSerializer,
    MachineSerializer,
    CreateToolChangeSerializer,
    ToolChangeBatchSerializer,
    CreateDailyProductionSerializer,
    DailyProductionSerializer,
    CreateWorkSessionSerializer,
    WorkSessionSerializer,
    CreateMachineSerializer,
    CreateToolTypeAdminSerializer,
    ToolTypeSerializer,
    MaterialTypeSerializer,
    MaterialEntrySerializer,
    MaterialShipmentSerializer,
    CreateMaterialEntrySerializer,
    CreateMaterialShipmentSerializer,
)


@api_view(["GET"])
def dashboard_data(request):
    today = timezone.localdate()

    machines = Machine.objects.filter(is_active=True).order_by("order_in_line")

    machine_cards = []

    # Prefetch to reduce queries
    batch_qs = (
        ToolChangeBatch.objects
        .filter(machine__in=machines)
        .order_by("-timestamp")
    )
    last_batch_map = {}
    for b in batch_qs.select_related("machine").prefetch_related("items", "items__tool_type"):
        if b.machine_id not in last_batch_map:
            last_batch_map[b.machine_id] = b

    dp_today_map = {dp.machine_id: dp for dp in DailyProduction.objects.filter(machine__in=machines, date=today)}
    last_sessions_map = {}
    for s in WorkSession.objects.filter(machine__in=machines).order_by("-end_time"):
        if s.machine_id not in last_sessions_map:
            last_sessions_map[s.machine_id] = s

    for m in machines:
        last_batch = last_batch_map.get(m.id)

        if last_batch:
            item_names = [item.tool_type.name for item in last_batch.items.all()]
            last_change_teams = " + ".join(item_names)
            last_counter = last_batch.current_counter
            last_change_time = last_batch.timestamp
            last_change_user = last_batch.changed_by.username if last_batch.changed_by else ""
        else:
            last_change_teams = ""
            last_counter = None
            last_change_time = None
            last_change_user = ""

        dp = dp_today_map.get(m.id)
        today_total = dp.total_count if dp else None

        last_session = last_sessions_map.get(m.id)
        if last_session:
            last_session_user = last_session.user.username
            last_session_range = f"{last_session.start_time.strftime('%H:%M')}–{last_session.end_time.strftime('%H:%M')}"
        else:
            last_session_user = ""
            last_session_range = ""

        machine_cards.append({
            "machine_id": m.id,
            "machine_name": m.name,
            "machine_short_name": m.short_name,
            "last_counter": last_counter,
            "last_change_teams": last_change_teams,
            "last_change_time": last_change_time,
            "last_change_user": last_change_user,
            "today_total": today_total,
            "last_session_user": last_session_user,
            "last_session_range": last_session_range,
        })

    serializer = MachineDashboardSerializer(machine_cards, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def whoami(request):
    user = request.user if request.user and request.user.is_authenticated else None
    if user:
        return Response({
            "is_authenticated": True,
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": bool(user.is_staff or user.is_superuser),
        })
    return Response({
        "is_authenticated": False,
        "id": None,
        "username": "anonymous",
        "first_name": "",
        "last_name": "",
        "is_admin": False,
    })


@csrf_exempt
@api_view(["POST"])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        ActivityLog.objects.create(user=user, action="login", details="Web login")
        return Response({"detail": "ok"})
    return Response({"detail": "Geçersiz kullanıcı adı veya şifre"}, status=401)


@api_view(["POST"])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return Response({"detail": "ok"})


@api_view(["GET"])
def machines_list(request):
    machines = Machine.objects.filter(is_active=True).order_by("order_in_line").prefetch_related("tool_types")
    return Response(MachineWithToolTypesSerializer(machines, many=True).data)

@api_view(["POST"])
def create_tool_change(request):
    serializer = CreateToolChangeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    machine = get_object_or_404(Machine, id=serializer.validated_data["machine_id"])
    tool_types = list(
        ToolType.objects.filter(id__in=serializer.validated_data["tool_type_ids"], machine=machine)
    )
    if not tool_types:
        return Response({"detail": "Geçerli takım seçilmedi."}, status=status.HTTP_400_BAD_REQUEST)

    batch = ToolChangeBatch.objects.create(
        machine=machine,
        changed_by=request.user if request.user and request.user.is_authenticated else None,
        current_counter=serializer.validated_data.get("current_counter"),
        note=serializer.validated_data.get("note", ""),
    )
    ToolChangeBatchItem.objects.bulk_create([
        ToolChangeBatchItem(batch=batch, tool_type=tt) for tt in tool_types
    ])

    # Log activity
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action="tool_change",
        machine=machine,
        details=f"tools={[tt.name for tt in tool_types]} counter={serializer.validated_data.get('current_counter')}"
    )

    return Response(ToolChangeBatchSerializer(batch).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def create_daily_production(request):
    serializer = CreateDailyProductionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    machine = get_object_or_404(Machine, id=serializer.validated_data["machine_id"])
    date = serializer.validated_data.get("date") or timezone.localdate()
    total_count = serializer.validated_data["total_count"]

    # Değişen davranış: her çağrıda yeni kayıt oluştur (kümülatif log)
    dp = DailyProduction.objects.create(
        machine=machine,
        date=date,
        total_count=total_count,
        recorded_by=request.user if request.user and request.user.is_authenticated else None,
    )
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action="daily_production",
        machine=machine,
        details=f"date={date} count={total_count} (incremental)"
    )
    return Response(DailyProductionSerializer(dp).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def create_work_session(request):
    serializer = CreateWorkSessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_object_or_404(User, id=serializer.validated_data["user_id"])
    machine = get_object_or_404(Machine, id=serializer.validated_data["machine_id"])

    ws = WorkSession.objects.create(
        user=user,
        machine=machine,
        start_time=serializer.validated_data["start_time"],
        end_time=serializer.validated_data["end_time"],
        produced_count=serializer.validated_data.get("produced_count"),
        note=serializer.validated_data.get("note", ""),
    )
    ActivityLog.objects.create(
        user=user,
        action="work_session",
        machine=machine,
        details=f"produced={serializer.validated_data.get('produced_count')}"
    )
    return Response(WorkSessionSerializer(ws).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def machine_detail(request, machine_id: int):
    machine = get_object_or_404(Machine, id=machine_id)
    today = timezone.localdate()

    last_batches = list(
        ToolChangeBatch.objects.filter(machine=machine).order_by("-timestamp").prefetch_related("items", "items__tool_type")[:10]
    )
    dp_today = DailyProduction.objects.filter(machine=machine, date=today).first()
    recent_daily = list(
        DailyProduction.objects.filter(machine=machine).order_by("-date")[:14]
    )
    recent_sessions = list(
        WorkSession.objects.filter(machine=machine).order_by("-end_time")[:10]
    )

    payload = {
        "machine": machine,
        "tool_types": list(machine.tool_types.filter(is_active=True)),
        "last_batches": last_batches,
        "today_total": dp_today.total_count if dp_today else None,
        "recent_daily": recent_daily,
        "recent_sessions": recent_sessions,
    }
    serializer = MachineDetailSerializer(payload)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_activity_logs(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    logs = ActivityLog.objects.all()[:200]
    from .serializers import ActivityLogSerializer
    return Response(ActivityLogSerializer(logs, many=True).data)


# Material endpoints
@api_view(["GET"])
def material_types(request):
    types = MaterialType.objects.filter(is_active=True).order_by("name")
    return Response(MaterialTypeSerializer(types, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def material_stock_summary(request):
    # compute boxes in - out per type
    data = []
    types = MaterialType.objects.filter(is_active=True)
    entries = MaterialEntry.objects.values("material_type").annotate(total=models.Sum("boxes_count"))
    shipments = MaterialShipment.objects.values("material_type").annotate(total=models.Sum("boxes_count"))
    entry_map = {e["material_type"]: e["total"] for e in entries}
    ship_map = {s["material_type"]: s["total"] for s in shipments}
    for t in types:
        data.append({
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "in_boxes": int(entry_map.get(t.id, 0) or 0),
            "out_boxes": int(ship_map.get(t.id, 0) or 0),
            "stock_boxes": int(entry_map.get(t.id, 0) or 0) - int(ship_map.get(t.id, 0) or 0),
        })
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_material_entry(request):
    serializer = CreateMaterialEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    mt = get_object_or_404(MaterialType, id=serializer.validated_data["material_type_id"]) 
    entry = MaterialEntry.objects.create(
        material_type=mt,
        boxes_count=serializer.validated_data["boxes_count"],
        units_per_box=serializer.validated_data.get("units_per_box"),
        created_by=request.user if request.user.is_authenticated else None,
    )
    ActivityLog.objects.create(user=request.user, action="work_session", machine=None, details=f"material_in {mt.name} +{entry.boxes_count} kutu")
    return Response(MaterialEntrySerializer(entry).data, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_material_shipment(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    serializer = CreateMaterialShipmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    mt = get_object_or_404(MaterialType, id=serializer.validated_data["material_type_id"]) 
    ship = MaterialShipment.objects.create(
        material_type=mt,
        boxes_count=serializer.validated_data["boxes_count"],
        note=serializer.validated_data.get("note", ""),
        created_by=request.user,
    )
    ActivityLog.objects.create(user=request.user, action="work_session", machine=None, details=f"material_out {mt.name} -{ship.boxes_count} kutu")
    return Response(MaterialShipmentSerializer(ship).data, status=201)


# Admin-only endpoints
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_create_machine(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    serializer = CreateMachineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    m = Machine.objects.create(
        name=data["name"],
        short_name=data["short_name"],
        order_in_line=data["order_in_line"],
        location=data.get("location", ""),
        is_active=data.get("is_active", True),
    )
    return Response(MachineSerializer(m).data, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_update_machine(request, machine_id: int):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    m = get_object_or_404(Machine, id=machine_id)
    serializer = CreateMachineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    for field in ["name", "short_name", "order_in_line", "location", "is_active"]:
        setattr(m, field, data.get(field, getattr(m, field)))
    m.save()
    return Response(MachineSerializer(m).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def admin_delete_machine(request, machine_id: int):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    m = get_object_or_404(Machine, id=machine_id)
    m.delete()
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_create_tooltype(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    serializer = CreateToolTypeAdminSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    machine = get_object_or_404(Machine, id=data["machine_id"]) 
    tt = ToolType.objects.create(machine=machine, name=data["name"], is_active=data.get("is_active", True))
    return Response(ToolTypeSerializer(tt).data, status=201)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def admin_delete_tooltype(request, tooltype_id: int):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({"detail": "Yetki yok"}, status=403)
    tt = get_object_or_404(ToolType, id=tooltype_id)
    tt.delete()
    return Response(status=204)
