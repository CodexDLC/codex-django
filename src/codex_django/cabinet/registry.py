from __future__ import annotations

from typing import Any

from .types import CabinetSection, DashboardWidget, NavAction


class CabinetRegistry:
    def __init__(self) -> None:
        self._sections: dict[str, CabinetSection] = {}
        self._dashboard_widgets: list[DashboardWidget] = []
        self._topbar_actions: list[NavAction] = []
        self._global_actions: list[NavAction] = []

    def register(
        self,
        module_name: str,
        section: CabinetSection | None = None,
        dashboard_widget: DashboardWidget | str | None = None,
        topbar_actions: list[NavAction] | None = None,
        actions: list[NavAction] | None = None,
    ) -> None:
        if section:
            self._sections[module_name] = section

        if dashboard_widget:
            if isinstance(dashboard_widget, str):
                # Legacy support: wrap string template into DashboardWidget
                widget = DashboardWidget(template=dashboard_widget)
            else:
                widget = dashboard_widget
            self._dashboard_widgets.append(widget)

        if topbar_actions:
            self._topbar_actions.extend(topbar_actions)
        if actions:
            self._global_actions.extend(actions)

    @property
    def sections(self) -> list[CabinetSection]:
        return sorted(self._sections.values(), key=lambda s: s.order)

    def get_sections(self, nav_group: str | None = None) -> list[CabinetSection]:
        sections = self.sections
        if nav_group:
            sections = [s for s in sections if s.nav_group == nav_group]
        return sections

    @property
    def dashboard_widgets(self) -> list[DashboardWidget]:
        return sorted(self._dashboard_widgets, key=lambda w: w.order)

    def get_dashboard_widgets(self, nav_group: str | None = None) -> list[DashboardWidget]:
        widgets = self.dashboard_widgets
        if nav_group:
            widgets = [w for w in widgets if w.nav_group == nav_group]
        return widgets

    @property
    def topbar_actions(self) -> list[NavAction]:
        return self._topbar_actions

    @property
    def global_actions(self) -> list[NavAction]:
        return self._global_actions


# Single instance — lives in process memory
cabinet_registry = CabinetRegistry()


def declare(
    module: str,
    section: CabinetSection | None = None,
    dashboard_widget: DashboardWidget | str | None = None,
    **kwargs: Any,
) -> None:
    """Public API for cabinet.py in feature apps. Analogous to admin.site.register().

    module — required explicit parameter, Django app name (e.g. 'booking').
    section — CabinetSection instance (not dict).
    dashboard_widget — DashboardWidget instance or template string (legacy).
    """
    from django.core.exceptions import ImproperlyConfigured

    if section is not None and not isinstance(section, CabinetSection):
        raise ImproperlyConfigured(f"cabinet.declare() section must be a CabinetSection instance, got {type(section)}")

    if dashboard_widget is not None and not isinstance(dashboard_widget, DashboardWidget | str):
        raise ImproperlyConfigured(
            "cabinet.declare() dashboard_widget must be a DashboardWidget instance or string, "
            f"got {type(dashboard_widget)}"
        )

    cabinet_registry.register(
        module_name=module,
        section=section,
        dashboard_widget=dashboard_widget,
        **kwargs,
    )
