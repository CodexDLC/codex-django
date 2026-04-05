"""Views for cabinet site-settings pages and HTMX partials."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from ..services.site_settings import SiteSettingsService


@login_required
def site_settings_view(request: HttpRequest) -> HttpResponse:
    """Отображает единую страницу всех настроек сайта и обрабатывает сохранение."""
    from django.contrib import messages

    if request.method == "POST":
        success, msg = SiteSettingsService.save_context(request)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)

    context = SiteSettingsService.get_context(request)
    return render(request, "cabinet/site_settings/index.html", context)


@login_required
def site_settings_tab_view(request: HttpRequest, tab_slug: str) -> HttpResponse:
    """Устаревшая вьюха для вкладок, теперь просто редиректит на общий корень по якорю."""
    return redirect(f"{reverse('cabinet:site_settings')}#{tab_slug}")
