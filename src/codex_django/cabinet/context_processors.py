"""Template context helpers for the cabinet UI shell."""

from typing import Any

from django.http import HttpRequest

from .notifications import notification_registry
from .quick_access import get_enabled_staff_quick_access, parse_selected_keys
from .registry import cabinet_registry
from .runtime import CabinetRuntimeResolver


def _detect_space(request: HttpRequest) -> str:
    return CabinetRuntimeResolver(cabinet_registry).detect_space(request)


def _detect_module(request: HttpRequest) -> str:
    space = _detect_space(request)
    return CabinetRuntimeResolver(cabinet_registry).detect_module(request, space)


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

    resolved = CabinetRuntimeResolver(cabinet_registry).get_context(request)
    space = resolved.space
    module = resolved.module
    sidebar_items = [
        item
        for item in resolved.sidebar
        if not item.permissions or any(request.user.has_perm(p) for p in item.permissions)
    ]
    shortcuts = resolved.shortcuts
    topbar_entries = resolved.topbar_entries
    nav_group = resolved.nav_group
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
    from .services.site_settings import SiteSettingsService

    settings_data = SiteSettingsService.get_all_settings()

    return {
        "cabinet_sidebar": sidebar_items,
        "cabinet_shortcuts": shortcuts,
        "cabinet_topbar_entries": topbar_entries,
        "cabinet_space": space,
        "cabinet_active_module": module,
        "cabinet_branding": resolved.branding,
        "cabinet_active_topbar": resolved.active_topbar,
        "cabinet_settings_url": resolved.settings_url,
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
