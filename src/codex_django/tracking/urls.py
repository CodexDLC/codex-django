"""URL patterns for reusable tracking cabinet views."""

from django.urls import path

from .views import tracking_analytics_view

app_name = "codex_tracking"

urlpatterns = [
    path("", tracking_analytics_view, name="analytics"),
]
