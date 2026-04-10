"""Views for cabinet site-settings pages and HTMX partials."""

from typing import cast

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.module_loading import import_string

from ..services.site_settings import SiteSettingsService


def _site_settings_service() -> type[SiteSettingsService]:
    service_path = getattr(settings, "CODEX_CABINET_SITE_SETTINGS_SERVICE", None)
    if not service_path:
        return SiteSettingsService
    return cast(type[SiteSettingsService], import_string(service_path))


@login_required
def site_settings_view(request: HttpRequest) -> HttpResponse:
    """Отображает единую страницу всех настроек сайта и обрабатывает сохранение."""
    from django.contrib import messages

    service = _site_settings_service()
    if not service.user_can_access(request.user):
        return HttpResponseForbidden()

    if request.method == "POST":
        success, msg = service.save_context(request)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)

    context = service.get_context(request)
    return render(request, "cabinet/site_settings/index.html", context)


@login_required
def site_settings_tab_view(request: HttpRequest, tab_slug: str) -> HttpResponse:
    """Устаревшая вьюха для вкладок, теперь просто редиректит на общий корень по якорю."""
    return redirect(f"{reverse('cabinet:site_settings')}#{tab_slug}")
