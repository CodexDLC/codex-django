"""Template context helpers for the cabinet UI shell."""

import contextlib
from typing import Any

from django.http import HttpRequest

from .notifications import notification_registry
from .quick_access import get_enabled_staff_quick_access, parse_selected_keys
from .redis.managers.settings import CabinetSettingsRedisManager
from .registry import cabinet_registry

_settings_manager = CabinetSettingsRedisManager()
_CABINET_PREFIX = "/cabinet/"
_CLIENT_PREFIX = "/cabinet/my/"


def _detect_space(request: HttpRequest) -> str:
    if request.path.startswith(_CLIENT_PREFIX):
        return "client"
    return "staff"


def _detect_module(request: HttpRequest) -> str:
    explicit: str | None = getattr(request, "cabinet_module", None)
    if explicit:
        return str(explicit)
    match = getattr(request, "resolver_match", None)
    if match and match.app_name and match.app_name != "cabinet":
        return str(match.app_name)
    return "admin"


def cabinet(request: HttpRequest) -> dict[str, Any]:
    if not request.user.is_authenticated:
        return {
            "cabinet_nav": [],
            "cabinet_sidebar": [],
            "cabinet_shortcuts": [],
            "cabinet_topbar_entries": [],
            "cabinet_topbar_actions": [],
            "cabinet_dashboard_widgets": [],
            "cabinet_space": "staff",
            "cabinet_active_module": "admin",
            "cabinet_branding": {},
            "cabinet_active_topbar": None,
            "cabinet_settings": None,
            "cabinet_settings_url": None,
        }

    space = _detect_space(request)
    module = _detect_module(request)
    sidebar_items = [
        item
        for item in cabinet_registry.get_sidebar(space, module)
        if not item.permissions or any(request.user.has_perm(p) for p in item.permissions)
    ]
    shortcuts = cabinet_registry.get_shortcuts(space, module)
    topbar_entries = cabinet_registry.get_topbar_entries()
    nav_group = getattr(request, "cabinet_nav_group", None)
    visible_sections = sorted(
        (
            section
            for section in cabinet_registry.get_sections(nav_group)
            if not section.permissions or any(request.user.has_perm(p) for p in section.permissions)
        ),
        key=lambda s: (s.nav_group, s.order),
    )
    visible_widgets = [
        widget
        for widget in cabinet_registry.get_dashboard_widgets(nav_group)
        if not widget.permissions or any(request.user.has_perm(p) for p in widget.permissions)
    ]
    settings_data = _settings_manager.get()

    settings_url = None
    if space == "staff":
        from django.urls import NoReverseMatch, reverse

        custom_url = cabinet_registry.get_settings_url(space, module)
        if custom_url:
            try:
                settings_url = reverse(custom_url)
            except NoReverseMatch:
                settings_url = custom_url

        if not settings_url:
            with contextlib.suppress(NoReverseMatch):
                settings_url = reverse("cabinet:site_settings")

    return {
        "cabinet_sidebar": sidebar_items,
        "cabinet_shortcuts": shortcuts,
        "cabinet_topbar_entries": topbar_entries,
        "cabinet_space": space,
        "cabinet_active_module": module,
        "cabinet_branding": cabinet_registry.get_branding(space),
        "cabinet_active_topbar": cabinet_registry.get_module_topbar(module),
        "cabinet_settings_url": settings_url,
        "cabinet_nav": visible_sections,
        "cabinet_topbar_actions": cabinet_registry.topbar_actions,
        "cabinet_dashboard_widgets": visible_widgets,
        "cabinet_settings": settings_data,
        "cabinet_quick_access": (
            get_enabled_staff_quick_access(
                parse_selected_keys((settings_data or {}).get("staff_quick_access_links")),
                request.user,
            )
            if space == "staff"
            else []
        ),
    }


def notifications(request: HttpRequest) -> dict[str, Any]:
    items = notification_registry.get_items(request)
    return {"notification_items": items, "bell_items": items}
