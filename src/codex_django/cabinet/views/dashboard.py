from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..selector.dashboard import DashboardSelector


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    context = DashboardSelector.get_context(request)
    return render(request, "cabinet/dashboard/index.html", context)
