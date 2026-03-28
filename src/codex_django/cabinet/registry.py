"""In-memory registry for cabinet navigation and dashboard contributions.

Feature apps typically interact with this module through :func:`declare`,
while the internal registry object stores normalized sections, widgets, and
actions for later rendering in context processors and views.
"""

from __future__ import annotations

from typing import Any

from .types import CabinetSection, DashboardWidget, NavAction


class CabinetRegistry:
    """Store cabinet sections, widgets, and actions in process memory."""

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
        """Register cabinet contributions for a feature module.

        Args:
            module_name: Django app or feature identifier.
            section: Optional sidebar/navigation section declaration.
            dashboard_widget: Optional dashboard widget declaration or legacy
                template-string shortcut.
            topbar_actions: Optional actions for the cabinet top bar.
            actions: Optional global actions shown elsewhere in the UI.
        """
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
        """Return all registered sections ordered by their display order."""
        return sorted(self._sections.values(), key=lambda s: s.order)

    def get_sections(self, nav_group: str | None = None) -> list[CabinetSection]:
        """Return registered sections, optionally filtered by nav group."""
        sections = self.sections
        if nav_group:
            sections = [s for s in sections if s.nav_group == nav_group]
        return sections

    @property
    def dashboard_widgets(self) -> list[DashboardWidget]:
        """Return all registered dashboard widgets ordered by their display order."""
        return sorted(self._dashboard_widgets, key=lambda w: w.order)

    def get_dashboard_widgets(self, nav_group: str | None = None) -> list[DashboardWidget]:
        """Return registered dashboard widgets, optionally filtered by nav group."""
        widgets = self.dashboard_widgets
        if nav_group:
            widgets = [w for w in widgets if w.nav_group == nav_group]
        return widgets

    @property
    def topbar_actions(self) -> list[NavAction]:
        """Return topbar action declarations in registration order."""
        return self._topbar_actions

    @property
    def global_actions(self) -> list[NavAction]:
        """Return global action declarations in registration order."""
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

    Args:
        module: Django app name or feature identifier, for example ``booking``.
        section: Optional :class:`CabinetSection` instance.
        dashboard_widget: Optional :class:`DashboardWidget` instance or a
            legacy template-string shortcut.
        **kwargs: Additional keyword arguments forwarded to
            :meth:`CabinetRegistry.register`.
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
