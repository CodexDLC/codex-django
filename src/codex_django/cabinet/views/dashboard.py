"""Views for the main cabinet dashboard shell."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..selector.dashboard import DashboardSelector


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render the dashboard page with aggregated provider context.

    Args:
        request: Authenticated Django request for the cabinet dashboard.

    Returns:
        Rendered dashboard response using the registered selector providers.
    """
    context = DashboardSelector.get_context(request)
    return render(request, "cabinet/dashboard/index.html", {"dashboard_data": context, **context})
