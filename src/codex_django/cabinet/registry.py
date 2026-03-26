from typing import Any, Dict, List, Optional

from .types import CabinetSection, NavAction


class CabinetRegistry:
    def __init__(self) -> None:
        self._sections: Dict[str, CabinetSection] = {}
        self._dashboard_widgets: List[str] = []
        self._topbar_actions: List[NavAction] = []
        self._global_actions: List[NavAction] = []

    def register(
        self,
        module_name: str,
        section: Optional[CabinetSection] = None,
        dashboard_widget: Optional[str] = None,
        topbar_actions: Optional[List[NavAction]] = None,
        actions: Optional[List[NavAction]] = None,
    ) -> None:
        if section:
            self._sections[module_name] = section
        if dashboard_widget:
            self._dashboard_widgets.append(dashboard_widget)
        if topbar_actions:
            self._topbar_actions.extend(topbar_actions)
        if actions:
            self._global_actions.extend(actions)

    @property
    def sections(self) -> List[CabinetSection]:
        return sorted(self._sections.values(), key=lambda s: s.order)

    @property
    def dashboard_widgets(self) -> List[str]:
        return self._dashboard_widgets

    @property
    def topbar_actions(self) -> List[NavAction]:
        return self._topbar_actions

    @property
    def global_actions(self) -> List[NavAction]:
        return self._global_actions


# Single instance — lives in process memory
cabinet_registry = CabinetRegistry()


def declare(
    module: str,
    section: Optional[CabinetSection] = None,
    **kwargs: Any,
) -> None:
    """Public API for cabinet.py in feature apps. Analogous to admin.site.register().

    module — required explicit parameter, Django app name (e.g. 'booking').
    section — CabinetSection instance (not dict). IDE highlights fields and types.
    Fail fast: ImproperlyConfigured on startup if wrong type is passed.
    """
    from django.core.exceptions import ImproperlyConfigured

    if section is not None and not isinstance(section, CabinetSection):
        raise ImproperlyConfigured(
            f"cabinet.declare() section must be a CabinetSection instance, got {type(section)}"
        )
    cabinet_registry.register(module_name=module, section=section, **kwargs)
