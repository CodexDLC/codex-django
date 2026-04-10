"""Cabinet views for tracking analytics."""

from __future__ import annotations

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .selector import TrackingSelector

_staff_check = user_passes_test(lambda user: user.is_active and (user.is_staff or user.is_superuser))


@_staff_check
def tracking_analytics_view(request: HttpRequest) -> HttpResponse:
    """Render the reusable cabinet analytics page for tracking data."""

    request.cabinet_module = "tracking"  # type: ignore[attr-defined]
    request.cabinet_nav_group = "admin"  # type: ignore[attr-defined]
    context = TrackingSelector.get_analytics_context().as_dict()
    return render(request, "tracking/cabinet/analytics.html", context)
