from django.contrib import admin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Machine, ToolType, ToolChangeBatch, ToolChangeBatchItem, DailyProduction, WorkSession, ActivityLog, MaterialType, MaterialEntry, MaterialShipment


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "short_name", "name", "order_in_line", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "short_name", "location")
    ordering = ("order_in_line",)


@admin.register(ToolType)
class ToolTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "name", "is_active")
    list_filter = ("is_active", "machine")
    search_fields = ("name", "machine__name", "machine__short_name")


class ToolChangeBatchItemInline(admin.TabularInline):
    model = ToolChangeBatchItem
    extra = 0


@admin.register(ToolChangeBatch)
class ToolChangeBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "changed_by", "timestamp", "current_counter")
    list_filter = ("machine", "changed_by")
    date_hierarchy = "timestamp"
    inlines = [ToolChangeBatchItemInline]


@admin.register(DailyProduction)
class DailyProductionAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "date", "total_count", "recorded_by", "created_at")
    list_filter = ("machine", "date")
    date_hierarchy = "date"


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "machine", "start_time", "end_time", "produced_count")
    list_filter = ("machine", "user")
    date_hierarchy = "start_time"
 

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "machine", "created_at")
    list_filter = ("action", "machine", "user")
    date_hierarchy = "created_at"


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(MaterialEntry)
class MaterialEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "material_type", "boxes_count", "units_per_box", "created_by", "created_at")
    list_filter = ("material_type",)
    date_hierarchy = "created_at"


@admin.register(MaterialShipment)
class MaterialShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "material_type", "boxes_count", "created_by", "created_at")
    list_filter = ("material_type",)
    date_hierarchy = "created_at"


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
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "role", "password1", "password2", "first_name", "last_name", "email", "is_active"),
        }),
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Rol", {"fields": ("role",)}),
    )


# Replace default User admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)
