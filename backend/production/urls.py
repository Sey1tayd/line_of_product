from django.urls import path
from .views import (
    health_check,
    dashboard_data,
    whoami,
    login_view,
    logout_view,
    machines_list,
    create_tool_change,
    create_daily_production,
    create_work_session,
    machine_detail,
    admin_create_machine,
    admin_update_machine,
    admin_delete_machine,
    admin_create_tooltype,
    admin_delete_tooltype,
    admin_activity_logs,
    material_types,
    material_stock_summary,
    material_detail,
    create_material_entry,
    create_material_shipment,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("whoami/", whoami, name="whoami"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_data, name="dashboard-data"),
    path("machines/", machines_list, name="machines-list"),
    path("tool-change/", create_tool_change, name="create-tool-change"),
    path("daily-production/", create_daily_production, name="create-daily-production"),
    path("work-session/", create_work_session, name="create-work-session"),
    path("machines/<int:machine_id>/", machine_detail, name="machine-detail"),
    # Admin endpoints
    path("admin/machines/", admin_create_machine, name="admin-create-machine"),
    path("admin/machines/<int:machine_id>/", admin_update_machine, name="admin-update-machine"),
    path("admin/machines/<int:machine_id>/delete/", admin_delete_machine, name="admin-delete-machine"),
    path("admin/tooltypes/", admin_create_tooltype, name="admin-create-tooltype"),
    path("admin/tooltypes/<int:tooltype_id>/delete/", admin_delete_tooltype, name="admin-delete-tooltype"),
    path("admin/activity-logs/", admin_activity_logs, name="admin-activity-logs"),
    # Material endpoints
    path("materials/types/", material_types, name="material-types"),
    path("materials/stock/", material_stock_summary, name="material-stock"),
    path("materials/<int:material_id>/", material_detail, name="material-detail"),
    path("materials/entry/", create_material_entry, name="material-entry"),
    path("materials/shipment/", create_material_shipment, name="material-shipment"),
]


