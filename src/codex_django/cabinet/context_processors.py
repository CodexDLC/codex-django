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

    # OR logic: show section if user has AT LEAST ONE matching permission.
    # Sorted by (nav_group, order) so {% regroup %} in templates works correctly.
    visible_sections = sorted(
        (
            section
            for section in cabinet_registry.sections
            if not section.permissions
            or any(request.user.has_perm(p) for p in section.permissions)
        ),
        key=lambda s: (s.nav_group, s.order),
    )

    return {
        "cabinet_nav": visible_sections,
        "cabinet_topbar_actions": cabinet_registry.topbar_actions,
        "cabinet_dashboard_widgets": cabinet_registry.dashboard_widgets,
        "cabinet_settings": _settings_manager.get(),
    }
