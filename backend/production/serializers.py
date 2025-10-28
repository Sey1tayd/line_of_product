from rest_framework import serializers
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


class MachineDashboardSerializer(serializers.Serializer):
    machine_id = serializers.IntegerField()
    machine_name = serializers.CharField()
    machine_short_name = serializers.CharField()
    last_counter = serializers.IntegerField(allow_null=True)
    last_change_teams = serializers.CharField(allow_blank=True)
    last_change_time = serializers.DateTimeField(allow_null=True)
    last_change_user = serializers.CharField(allow_blank=True)
    today_total = serializers.IntegerField(allow_null=True)
    last_session_user = serializers.CharField(allow_blank=True)
    last_session_range = serializers.CharField(allow_blank=True)


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = [
            "id",
            "name",
            "short_name",
            "order_in_line",
            "location",
            "is_active",
        ]


class ToolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolType
        fields = ["id", "machine", "name", "is_active"]


class MachineWithToolTypesSerializer(serializers.ModelSerializer):
    tool_types = ToolTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Machine
        fields = [
            "id",
            "name",
            "short_name",
            "order_in_line",
            "location",
            "is_active",
            "tool_types",
        ]


class ToolChangeBatchItemSerializer(serializers.ModelSerializer):
    tool_type_name = serializers.CharField(source="tool_type.name", read_only=True)

    class Meta:
        model = ToolChangeBatchItem
        fields = ["id", "tool_type", "tool_type_name", "quantity", "extra_note"]


class ToolChangeBatchSerializer(serializers.ModelSerializer):
    items = ToolChangeBatchItemSerializer(many=True, read_only=True)
    changed_by_username = serializers.CharField(source="changed_by.username", read_only=True)

    class Meta:
        model = ToolChangeBatch
        fields = [
            "id",
            "machine",
            "changed_by",
            "changed_by_username",
            "timestamp",
            "current_counter",
            "note",
            "items",
        ]
        read_only_fields = ["changed_by", "timestamp"]


class CreateToolChangeSerializer(serializers.Serializer):
    machine_id = serializers.IntegerField()
    tool_type_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    current_counter = serializers.IntegerField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)


class DailyProductionSerializer(serializers.ModelSerializer):
    recorded_by_username = serializers.CharField(source="recorded_by.username", read_only=True)
    class Meta:
        model = DailyProduction
        fields = ["id", "machine", "date", "total_count", "recorded_by", "recorded_by_username", "created_at"]
        read_only_fields = ["recorded_by", "created_at"]


class CreateDailyProductionSerializer(serializers.Serializer):
    machine_id = serializers.IntegerField()
    date = serializers.DateField(required=False)
    total_count = serializers.IntegerField()


class WorkSessionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    machine_short_name = serializers.CharField(source="machine.short_name", read_only=True)

    class Meta:
        model = WorkSession
        fields = [
            "id",
            "user",
            "user_username",
            "machine",
            "machine_short_name",
            "start_time",
            "end_time",
            "produced_count",
            "note",
        ]


class CreateWorkSessionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    machine_id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    produced_count = serializers.IntegerField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)


class MachineDetailSerializer(serializers.Serializer):
    machine = MachineSerializer()
    tool_types = ToolTypeSerializer(many=True)
    last_batches = ToolChangeBatchSerializer(many=True)
    today_total = serializers.IntegerField(allow_null=True)
    recent_daily = DailyProductionSerializer(many=True)
    recent_sessions = WorkSessionSerializer(many=True)


class ActivityLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    machine_short_name = serializers.CharField(source="machine.short_name", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "action",
            "user",
            "user_username",
            "machine",
            "machine_short_name",
            "details",
            "created_at",
        ]


class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ["id", "name", "code", "is_active"]


class MaterialEntrySerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source="material_type.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = MaterialEntry
        fields = ["id", "material_type", "material_type_name", "boxes_count", "units_per_box", "created_by", "created_by_username", "created_at"]
        read_only_fields = ["created_by", "created_at"]


class MaterialShipmentSerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source="material_type.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = MaterialShipment
        fields = ["id", "material_type", "material_type_name", "boxes_count", "units_per_box", "note", "created_by", "created_by_username", "created_at"]
        read_only_fields = ["created_by", "created_at"]


class CreateMaterialEntrySerializer(serializers.Serializer):
    material_type_id = serializers.IntegerField()
    boxes_count = serializers.IntegerField()
    units_per_box = serializers.IntegerField()  # ZORUNLU


class CreateMaterialShipmentSerializer(serializers.Serializer):
    material_type_id = serializers.IntegerField()
    boxes_count = serializers.IntegerField()
    units_per_box = serializers.IntegerField()  # ZORUNLU
    note = serializers.CharField(required=False, allow_blank=True)


class CreateMachineSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    short_name = serializers.CharField(max_length=50)
    order_in_line = serializers.IntegerField()
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False, default=True)


class CreateToolTypeAdminSerializer(serializers.Serializer):
    machine_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    is_active = serializers.BooleanField(required=False, default=True)
