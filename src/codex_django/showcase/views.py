import functools
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render

from .mock import ShowcaseMockData


def debug_only(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """Decorator: access only in DEBUG mode."""

    @functools.wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not settings.DEBUG:
            return HttpResponseForbidden("This showcase is only available in DEBUG mode.")
        return view_func(request, *args, **kwargs)

    return wrapper


# ── Views ──────────────────────────────────────────────────────────────────────


@debug_only
def index(request: HttpRequest) -> HttpResponse:
    """Showcase Hub."""
    return render(request, "showcase/index.html")


@debug_only
def dashboard_view(request: HttpRequest) -> HttpResponse:
    return render(request, "showcase/cabinet/dashboard/index.html", ShowcaseMockData.get_dashboard_context())


@debug_only
def staff_view(request: HttpRequest) -> HttpResponse:
    segment = request.GET.get("segment", "all")
    q = request.GET.get("q", "").strip().lower()
    return render(
        request, "showcase/cabinet/staff/index.html", ShowcaseMockData.get_staff_context(segment=segment, q=q)
    )


@debug_only
def clients_view(request: HttpRequest) -> HttpResponse:
    segment = request.GET.get("segment", "all")
    q = request.GET.get("q", "").strip().lower()
    return render(
        request, "showcase/cabinet/clients/index.html", ShowcaseMockData.get_clients_context(segment=segment, q=q)
    )


@debug_only
def conversations_view(request: HttpRequest) -> HttpResponse:
    folder = request.GET.get("folder", "inbox")
    topic_pk = request.GET.get("topic")
    q = request.GET.get("q", "").strip().lower()
    return render(
        request,
        "showcase/cabinet/conversations/index.html",
        ShowcaseMockData.get_conversations_context(folder=folder, topic_pk=topic_pk, q=q),
    )


@debug_only
def conversation_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    conv = ShowcaseMockData.get_conversation_detail(pk)
    if not conv:
        return render(request, "showcase/cabinet/conversations/_empty.html")
    return render(request, "showcase/cabinet/conversations/_detail.html", {"conv": conv})


@debug_only
def booking_view(request: HttpRequest) -> HttpResponse:
    return render(request, "showcase/cabinet/booking/index.html", ShowcaseMockData.get_booking_schedule_context())


@debug_only
def booking_appointments_view(request: HttpRequest) -> HttpResponse:
    active_status = request.GET.get("status", "all")
    return render(
        request,
        "showcase/cabinet/booking/appointments.html",
        ShowcaseMockData.get_booking_appointments_context(active_status=active_status),
    )


@debug_only
def booking_new_view(request: HttpRequest) -> HttpResponse:
    return render(request, "showcase/cabinet/booking/new.html", ShowcaseMockData.get_booking_new_context())


@debug_only
def reports_view(request: HttpRequest) -> HttpResponse:
    tab = request.GET.get("tab", "revenue")
    period = request.GET.get("period", "month")
    staff = request.GET.get("staff", "")
    return render(
        request,
        "showcase/cabinet/analytics/reports.html",
        ShowcaseMockData.get_reports_context(tab=tab, period=period, staff=staff),
    )


@debug_only
def site_settings_view(request: HttpRequest) -> HttpResponse:
    return redirect("codex_showcase:site_settings_tab", tab="contact")


@debug_only
def site_settings_tab_view(request: HttpRequest, tab: str) -> HttpResponse:
    VALID_TABS = {"contact", "geo", "social", "marketing", "technical", "email", "legal", "topbar"}
    if tab not in VALID_TABS:
        tab = "contact"
    if request.headers.get("HX-Request"):
        return render(request, f"showcase/cabinet/site_settings/partials/_{tab}.html", {"active_tab": tab})
    return render(request, "showcase/cabinet/site_settings/index.html", {"active_tab": tab})


@debug_only
def catalog_view(request: HttpRequest, category_pk: int | None = None) -> HttpResponse:
    return render(
        request, "showcase/cabinet/catalog/index.html", ShowcaseMockData.get_catalog_context(category_pk=category_pk)
    )
