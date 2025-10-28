from django.db import models
from django.contrib.auth.models import User


class Machine(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    order_in_line = models.IntegerField()
    location = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.short_name or self.name


class ToolType(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="tool_types")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.machine.short_name} - {self.name}"


class ToolChangeBatch(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="change_batches")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    current_counter = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.machine.short_name} @ {self.timestamp} sayaç={self.current_counter}"


class ToolChangeBatchItem(models.Model):
    batch = models.ForeignKey(ToolChangeBatch, on_delete=models.CASCADE, related_name="items")
    tool_type = models.ForeignKey(ToolType, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    extra_note = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.tool_type.name} x{self.quantity}"


class DailyProduction(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="daily_counts")
    date = models.DateField()
    total_count = models.IntegerField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine.short_name} - {self.date} : {self.total_count}"


class WorkSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="work_sessions")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="work_sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    produced_count = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} @ {self.machine.short_name} {self.start_time} -> {self.end_time}"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("login", "Login"),
        ("tool_change", "Tool Change"),
        ("daily_production", "Daily Production"),
        ("work_session", "Work Session"),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} {self.action} {self.machine} {self.created_at}"


# Packaged materials (hazır paketlenmiş malzeme)
class MaterialType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MaterialEntry(models.Model):
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, related_name="entries")
    boxes_count = models.IntegerField()  # girilen kutu sayısı
    units_per_box = models.IntegerField(default=1)  # kutu başına adet sayısı (ZORUNLU)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="material_entries")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material_type.name} +{self.boxes_count} kutu ({self.boxes_count * self.units_per_box} adet)"


class MaterialShipment(models.Model):
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, related_name="shipments")
    boxes_count = models.IntegerField()  # giden kutu sayısı
    units_per_box = models.IntegerField(default=1)  # kutu başına adet sayısı (ZORUNLU)
    note = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="material_shipments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material_type.name} -{self.boxes_count} kutu ({self.boxes_count * self.units_per_box} adet)"