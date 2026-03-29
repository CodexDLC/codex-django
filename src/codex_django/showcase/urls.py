from collections.abc import Callable

from django.http import HttpResponse
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "codex_showcase"


def _t(template: str) -> Callable[..., HttpResponse]:
    # Using the same debug_only protection for template generic views
    return views.debug_only(TemplateView.as_view(template_name=template))  # type: ignore[arg-type]


urlpatterns = [
    path("", views.index, name="index"),
    path("staff/", views.staff_view, name="staff"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("clients/", views.clients_view, name="clients"),
    path("conversations/", views.conversations_view, name="conversations"),
    path("conversations/<int:pk>/", views.conversation_detail_view, name="conversation_detail"),
    path("booking/", views.booking_view, name="booking"),
    path("booking/appointments/", views.booking_appointments_view, name="booking_appointments"),
    path("booking/new/", views.booking_new_view, name="booking_new"),
    path("analytics/reports/", views.reports_view, name="reports"),
    path("site/settings/", views.site_settings_view, name="site_settings"),
    path("site/settings/<str:tab>/", views.site_settings_tab_view, name="site_settings_tab"),
    path("catalog/", views.catalog_view, name="catalog"),
    path("catalog/<int:category_pk>/", views.catalog_view, name="catalog_category"),
    path("notifications/", views.notifications_log_view, name="notifications_log"),
    path("notifications/templates/", views.notifications_templates_view, name="notifications_templates"),
    # Client side
    path("profile/", _t("showcase/cabinet/client/profile.html"), name="profile"),
    path("my/", _t("showcase/cabinet/client/my_appointments.html"), name="my_appointments"),
    path("my/settings/", _t("showcase/cabinet/client/settings.html"), name="settings"),
    path(
        "my/settings/notifications/",
        _t("showcase/cabinet/client/settings_notifications.html"),
        name="settings_notifications",
    ),
    path("my/settings/privacy/", _t("showcase/cabinet/client/settings_privacy.html"), name="settings_privacy"),
]
