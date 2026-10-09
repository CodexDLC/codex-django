"""URL patterns for the reusable cabinet dashboard and settings views."""

from django.urls import path

from .views import (
    dashboard_view,
    resource_create_view,
    resource_edit_view,
    resource_list_view,
    resource_smart_preview_view,
    resource_smart_publish_view,
    resource_smart_status_view,
    site_settings_tab_view,
    site_settings_view,
)

# No app_name here — the project's cabinet/urls.py owns the 'cabinet' namespace
# and includes these patterns via include("codex_django.cabinet.urls")

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("site/settings/", site_settings_view, name="site_settings"),
    path("site/settings/<str:tab>/", site_settings_tab_view, name="site_settings_tab"),
    path("resources/<str:resource_key>/", resource_list_view, name="resource_list"),
    path("resources/<str:resource_key>/create/", resource_create_view, name="resource_create"),
    path("resources/<str:resource_key>/<str:pk>/edit/", resource_edit_view, name="resource_edit"),
    path("resources/<str:resource_key>/smart-preview/", resource_smart_preview_view, name="resource_smart_preview"),
    path(
        "resources/<str:resource_key>/drafts/<str:draft_id>/status/",
        resource_smart_status_view,
        name="resource_smart_status",
    ),
    path(
        "resources/<str:resource_key>/drafts/<str:draft_id>/publish/",
        resource_smart_publish_view,
        name="resource_smart_publish",
    ),
]
