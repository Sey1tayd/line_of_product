from django.contrib import admin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Machine, ToolType, ToolChangeBatch, ToolChangeBatchItem, DailyProduction, WorkSession, ActivityLog, MaterialType, MaterialEntry, MaterialShipment


# Admin Site Customization
admin.site.site_header = "AYD Robotic Yönetim Paneli"
admin.site.site_title = "AYD Robotic Admin"
admin.site.index_title = "Üretim Yönetim Sistemi"


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "short_name", "name", "location", "order_in_line", "active_status")
    list_display_links = ("id", "short_name", "name")
    list_filter = ("is_active",)
    list_editable = ("order_in_line",)
    search_fields = ("name", "short_name", "location")
    ordering = ("order_in_line",)
    readonly_fields = ("id",)
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("id", "name", "short_name")
        }),
        ("Konum ve Sıralama", {
            "fields": ("location", "order_in_line")
        }),
        ("Durum", {
            "fields": ("is_active",)
        }),
    )
    
    actions = ["activate_machines", "deactivate_machines"]
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Aktif</span>')
        return format_html('<span style="color: red;">✗ Pasif</span>')
    active_status.short_description = "Durum"
    
    def activate_machines(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} makine aktif edildi.")
    activate_machines.short_description = "Seçili makineleri aktif et"
    
    def deactivate_machines(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} makine pasif edildi.")
    deactivate_machines.short_description = "Seçili makineleri pasif et"


@admin.register(ToolType)
class ToolTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "machine", "active_status")
    list_display_links = ("id", "name")
    list_filter = ("is_active", "machine")
    search_fields = ("name", "machine__name", "machine__short_name")
    readonly_fields = ("id",)
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("id", "machine", "name")
        }),
        ("Durum", {
            "fields": ("is_active",)
        }),
    )
    
    actions = ["activate_tools", "deactivate_tools"]
    
    # Enable autocomplete for inline forms
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(name__icontains=search_term)
        return queryset, use_distinct
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Aktif</span>')
        return format_html('<span style="color: red;">✗ Pasif</span>')
    active_status.short_description = "Durum"
    
    def activate_tools(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} takım tipi aktif edildi.")
    activate_tools.short_description = "Seçili takım tiplerini aktif et"
    
    def deactivate_tools(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} takım tipi pasif edildi.")
    deactivate_tools.short_description = "Seçili takım tiplerini pasif et"


class ToolChangeBatchItemInline(admin.TabularInline):
    model = ToolChangeBatchItem
    extra = 1
    fields = ("tool_type", "quantity", "extra_note")
    autocomplete_fields = ["tool_type"]


@admin.register(ToolChangeBatch)
class ToolChangeBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "changed_by", "timestamp", "current_counter", "tools_changed")
    list_display_links = ("id", "machine")
    list_filter = ("machine", "changed_by", "timestamp")
    search_fields = ("machine__name", "changed_by__username", "note")
    date_hierarchy = "timestamp"
    readonly_fields = ("id", "timestamp")
    inlines = [ToolChangeBatchItemInline]
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("id", "machine", "changed_by", "timestamp")
        }),
        ("Detaylar", {
            "fields": ("current_counter", "note")
        }),
    )
    
    def tools_changed(self, obj):
        items = obj.items.all()
        if items:
            tool_list = ", ".join([item.tool_type.name for item in items])
            return format_html('<span title="{}">{}</span>', tool_list, f"{len(items)} takım")
        return "-"
    tools_changed.short_description = "Değiştirilen Takımlar"


@admin.register(DailyProduction)
class DailyProductionAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "date", "total_count", "recorded_by", "created_at")
    list_display_links = ("id", "machine")
    list_filter = ("machine", "date", "recorded_by")
    search_fields = ("machine__name", "recorded_by__username")
    date_hierarchy = "date"
    readonly_fields = ("id", "created_at")
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("id", "machine", "date")
        }),
        ("Üretim Verisi", {
            "fields": ("total_count",)
        }),
        ("Kayıt Bilgisi", {
            "fields": ("recorded_by", "created_at")
        }),
    )
    
    actions = ["export_to_csv"]
    
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="daily_production.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Makine', 'Tarih', 'Toplam Sayım', 'Kaydeden', 'Kayıt Zamanı'])
        
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.machine.name,
                obj.date,
                obj.total_count,
                obj.recorded_by.username if obj.recorded_by else '-',
                obj.created_at
            ])
        
        return response
    export_to_csv.short_description = "CSV olarak dışa aktar"


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "machine", "start_time", "end_time", "duration", "produced_count")
    list_display_links = ("id", "user")
    list_filter = ("machine", "user", "start_time")
    search_fields = ("user__username", "machine__name", "note")
    date_hierarchy = "start_time"
    readonly_fields = ("id", "duration")
    
    fieldsets = (
        ("Kullanıcı ve Makine", {
            "fields": ("id", "user", "machine")
        }),
        ("Zaman Bilgisi", {
            "fields": ("start_time", "end_time", "duration")
        }),
        ("Üretim", {
            "fields": ("produced_count", "note")
        }),
    )
    
    def duration(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            hours = delta.total_seconds() / 3600
            return f"{hours:.2f} saat"
        return "-"
    duration.short_description = "Süre"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action_display", "machine", "created_at", "details_short")
    list_display_links = ("id", "user")
    list_filter = ("action", "machine", "user", "created_at")
    search_fields = ("user__username", "machine__name", "details")
    date_hierarchy = "created_at"
    readonly_fields = ("id", "created_at")
    
    fieldsets = (
        ("Kullanıcı ve Aksiyon", {
            "fields": ("id", "user", "action", "machine")
        }),
        ("Detaylar", {
            "fields": ("details", "created_at")
        }),
    )
    
    def action_display(self, obj):
        colors = {
            "login": "blue",
            "tool_change": "orange",
            "daily_production": "green",
            "work_session": "purple"
        }
        color = colors.get(obj.action, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_display.short_description = "Aksiyon"
    
    def details_short(self, obj):
        if obj.details and len(obj.details) > 50:
            return obj.details[:50] + "..."
        return obj.details or "-"
    details_short.short_description = "Detaylar"
    
    # Read-only model (loglar silinmemeli)
    def has_delete_permission(self, request, obj=None):
        # Sadece superuser silebilir
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # Loglar değiştirilemez
        return False


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "active_status", "stock_summary")
    list_display_links = ("id", "name")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    readonly_fields = ("id", "stock_info")
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("id", "name", "code")
        }),
        ("Durum", {
            "fields": ("is_active",)
        }),
        ("Stok Bilgisi", {
            "fields": ("stock_info",),
            "classes": ("collapse",)
        }),
    )
    
    actions = ["activate_materials", "deactivate_materials"]
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Aktif</span>')
        return format_html('<span style="color: red;">✗ Pasif</span>')
    active_status.short_description = "Durum"
    
    def stock_summary(self, obj):
        from django.db.models import Sum
        entries = obj.entries.aggregate(total=Sum('boxes_count'))['total'] or 0
        shipments = obj.shipments.aggregate(total=Sum('boxes_count'))['total'] or 0
        stock = entries - shipments
        
        color = "green" if stock > 0 else ("red" if stock < 0 else "gray")
        return format_html('<span style="color: {}; font-weight: bold;">{} kutu</span>', color, stock)
    stock_summary.short_description = "Mevcut Stok"
    
    def stock_info(self, obj):
        from django.db.models import Sum
        entries = obj.entries.aggregate(total=Sum('boxes_count'))['total'] or 0
        shipments = obj.shipments.aggregate(total=Sum('boxes_count'))['total'] or 0
        stock = entries - shipments
        
        return format_html(
            '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">'
            '<p><strong>Toplam Giriş:</strong> {} kutu</p>'
            '<p><strong>Toplam Çıkış:</strong> {} kutu</p>'
            '<p><strong>Mevcut Stok:</strong> <span style="color: {}; font-weight: bold;">{} kutu</span></p>'
            '</div>',
            entries, shipments,
            "green" if stock > 0 else ("red" if stock < 0 else "gray"),
            stock
        )
    stock_info.short_description = "Stok Detayları"
    
    def activate_materials(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} malzeme tipi aktif edildi.")
    activate_materials.short_description = "Seçili malzeme tiplerini aktif et"
    
    def deactivate_materials(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} malzeme tipi pasif edildi.")
    deactivate_materials.short_description = "Seçili malzeme tiplerini pasif et"


@admin.register(MaterialEntry)
class MaterialEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "material_type", "boxes_count", "units_per_box", "total_units", "created_by", "created_at")
    list_display_links = ("id", "material_type")
    list_filter = ("material_type", "created_by", "created_at")
    search_fields = ("material_type__name", "created_by__username")
    date_hierarchy = "created_at"
    readonly_fields = ("id", "created_at", "total_units")
    
    fieldsets = (
        ("Malzeme Bilgisi", {
            "fields": ("id", "material_type")
        }),
        ("Miktar", {
            "fields": ("boxes_count", "units_per_box", "total_units")
        }),
        ("Kayıt Bilgisi", {
            "fields": ("created_by", "created_at")
        }),
    )
    
    def total_units(self, obj):
        if obj.units_per_box:
            total = obj.boxes_count * obj.units_per_box
            return format_html('<strong>{}</strong> adet', total)
        return "-"
    total_units.short_description = "Toplam Adet"


@admin.register(MaterialShipment)
class MaterialShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "material_type", "boxes_count", "note_short", "created_by", "created_at")
    list_display_links = ("id", "material_type")
    list_filter = ("material_type", "created_by", "created_at")
    search_fields = ("material_type__name", "created_by__username", "note")
    date_hierarchy = "created_at"
    readonly_fields = ("id", "created_at")
    
    fieldsets = (
        ("Sevkiyat Bilgisi", {
            "fields": ("id", "material_type", "boxes_count")
        }),
        ("Notlar", {
            "fields": ("note",)
        }),
        ("Kayıt Bilgisi", {
            "fields": ("created_by", "created_at")
        }),
    )
    
    def note_short(self, obj):
        if obj.note and len(obj.note) > 30:
            return obj.note[:30] + "..."
        return obj.note or "-"
    note_short.short_description = "Not"


# Custom user admin with simple role selector (admin/user)
class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (("user", "Kullanıcı"), ("admin", "Admin"))
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial="user")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "role", "first_name", "last_name", "email")

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")
        if role == "admin":
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    ROLE_CHOICES = (("user", "Kullanıcı"), ("admin", "Admin"))
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("username", "role", "first_name", "last_name", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial role from current flags
        if self.instance and self.instance.pk:
            self.fields["role"].initial = "admin" if (self.instance.is_staff or self.instance.is_superuser) else "user"

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")
        if role == "admin":
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        if commit:
            user.save()
        return user


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("username", "email", "first_name", "last_name", "user_role", "is_active", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("-date_joined",)
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "role", "password1", "password2", "first_name", "last_name", "email", "is_active"),
        }),
    )
    fieldsets = (
        ("Kullanıcı Bilgileri", {
            "fields": ("username", "password")
        }),
        ("Kişisel Bilgiler", {
            "fields": ("first_name", "last_name", "email")
        }),
        ("Yetki ve Rol", {
            "fields": ("role", "is_active")
        }),
        ("Önemli Tarihler", {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",)
        }),
    )
    
    actions = ["make_admin", "make_user", "activate_users", "deactivate_users"]
    
    def user_role(self, obj):
        if obj.is_superuser or obj.is_staff:
            return format_html('<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px;">Admin</span>')
        return format_html('<span style="background-color: #2196F3; color: white; padding: 3px 10px; border-radius: 3px;">Kullanıcı</span>')
    user_role.short_description = "Rol"
    
    def make_admin(self, request, queryset):
        updated = queryset.update(is_staff=True, is_superuser=True)
        self.message_user(request, f"{updated} kullanıcı admin yapıldı.")
    make_admin.short_description = "Seçili kullanıcıları admin yap"
    
    def make_user(self, request, queryset):
        updated = queryset.update(is_staff=False, is_superuser=False)
        self.message_user(request, f"{updated} kullanıcı normal kullanıcı yapıldı.")
    make_user.short_description = "Seçili kullanıcıları normal kullanıcı yap"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} kullanıcı aktif edildi.")
    activate_users.short_description = "Seçili kullanıcıları aktif et"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} kullanıcı pasif edildi.")
    deactivate_users.short_description = "Seçili kullanıcıları pasif et"


# Replace default User admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)
