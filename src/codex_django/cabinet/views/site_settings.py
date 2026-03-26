from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

_VALID_TABS = frozenset({"contact", "geo", "social", "marketing", "technical", "email", "legal"})


@login_required
def site_settings_view(request: HttpRequest) -> HttpResponse:
    """Main settings page — shows index.html with contact tab active by default."""
    return render(
        request,
        "cabinet/site_settings/index.html",
        {"active_tab": "contact"},
    )


@login_required
def site_settings_tab_view(request: HttpRequest, tab: str) -> HttpResponse:
    """HTMX partial for a settings tab — returns partials/_{tab}.html.

    Renders the full page if the request is not an HTMX request,
    so direct URL navigation works correctly.
    """
    if tab not in _VALID_TABS:
        tab = "contact"

    if request.headers.get("HX-Request"):
        template = f"cabinet/site_settings/partials/_{tab}.html"
        return render(request, template, {"active_tab": tab})

    return render(
        request,
        "cabinet/site_settings/index.html",
        {"active_tab": tab},
    )
