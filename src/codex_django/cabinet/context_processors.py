"""Template context helpers for the cabinet UI shell.

The cabinet context processor filters registered sections and widgets by
navigation group and user permissions, then exposes the resulting navigation
payload to every cabinet template render.
"""

from typing import Any

from django.http import HttpRequest

from .redis.managers.settings import CabinetSettingsRedisManager
from .registry import cabinet_registry

_settings_manager = CabinetSettingsRedisManager()


def cabinet(request: HttpRequest) -> dict[str, Any]:
    """Injects filtered navigation and cabinet settings into every cabinet template.

    Always returns expected structure — templates must not crash on anonymous users.

    Connect in settings.py:
        TEMPLATES = [{'OPTIONS': {'context_processors': [
            'codex_django.cabinet.context_processors.cabinet',
        ]}}]
    """
    if not request.user.is_authenticated:
        return {
            "cabinet_nav": [],
            "cabinet_topbar_actions": [],
            "cabinet_dashboard_widgets": [],
            "cabinet_settings": None,
        }

    # Filter sections by group and permissions
    # If request has 'cabinet_nav_group' attribute, use it, otherwise default to None (all)
    nav_group = getattr(request, "cabinet_nav_group", None)

    visible_sections = sorted(
        (
            section
            for section in cabinet_registry.get_sections(nav_group)
            if not section.permissions or any(request.user.has_perm(p) for p in section.permissions)
        ),
        key=lambda s: (s.nav_group, s.order),
    )

    # Filter widgets by group and permissions
    visible_widgets = [
        widget
        for widget in cabinet_registry.get_dashboard_widgets(nav_group)
        if not widget.permissions or any(request.user.has_perm(p) for p in widget.permissions)
    ]

    return {
        "cabinet_nav": visible_sections,
        "cabinet_topbar_actions": cabinet_registry.topbar_actions,
        "cabinet_dashboard_widgets": visible_widgets,
        "cabinet_settings": _settings_manager.get(),
    }
