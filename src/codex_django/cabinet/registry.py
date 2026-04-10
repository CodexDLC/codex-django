"""In-memory registry for cabinet navigation and dashboard contributions.

Feature apps interact with this module through :func:`declare`.
The registry stores sections, widgets, actions, sidebar items, and shortcuts
for rendering via context processors and views.

Supports two APIs:
- **Legacy** (v1): ``declare(module, section=CabinetSection(...))``
- **New** (v2): ``declare(module, space="staff", topbar=TopbarEntry(...), sidebar=[...])``
"""

from __future__ import annotations

from typing import Any

from .types import (
    CabinetModuleConfig,
    CabinetSection,
    DashboardWidget,
    NavAction,
    Shortcut,
    SidebarItem,
    TopbarEntry,
)


class CabinetRegistry:
    """Store cabinet contributions in process memory."""

    def __init__(self) -> None:
        # Legacy v1 storage
        self._sections: dict[str, CabinetSection] = {}
        self._dashboard_widgets: list[DashboardWidget] = []
        self._topbar_actions: list[NavAction] = []
        self._global_actions: list[NavAction] = []

        # New v2 two-space storage
        # key: (space, module) → value
        self._topbar_entries: dict[str, list[TopbarEntry]] = {
            "admin": [],
            "services": [],
        }
        self._sidebar: dict[tuple[str, str], list[SidebarItem]] = {}
        self._shortcuts: dict[tuple[str, str], list[Shortcut]] = {}
        self._settings_urls: dict[tuple[str, str], str] = {}
        self._branding: dict[str, dict[str, Any]] = {}
        self._module_topbar: dict[str, TopbarEntry] = {}
        self._module_spaces: dict[str, set[str]] = {}

    # ------------------------------------------------------------------
    # Branding & Meta
    # ------------------------------------------------------------------

    def register_branding(
        self,
        space: str,
        label: str | None = None,
        icon: str | None = None,
    ) -> None:
        """Set branding metadata for a specific space."""
        self._branding[space] = {
            "label": label,
            "icon": icon,
        }

    def get_branding(self, space: str) -> dict[str, Any]:
        """Return branding metadata for a specific space."""
        return self._branding.get(space, {})

    # ------------------------------------------------------------------
    # V2 API — two-space model
    # ------------------------------------------------------------------

    def register_v2(
        self,
        module: str,
        space: str,
        topbar: TopbarEntry | None = None,
        sidebar: list[SidebarItem] | None = None,
        shortcuts: list[Shortcut] | None = None,
        dashboard_widgets: list[DashboardWidget] | DashboardWidget | str | None = None,
        settings_url: str | None = None,
    ) -> None:
        """Register cabinet contributions for the new two-space model."""
        self._module_spaces.setdefault(module, set()).add(space)

        if topbar:
            self._module_topbar[module] = topbar
            group = topbar.group
            if group not in self._topbar_entries:
                self._topbar_entries[group] = []
            self._topbar_entries[group].append(topbar)

        if sidebar:
            self._sidebar[(space, module)] = sidebar

        if shortcuts:
            self._shortcuts[(space, module)] = shortcuts

        if dashboard_widgets:
            widgets = [dashboard_widgets] if isinstance(dashboard_widgets, DashboardWidget | str) else dashboard_widgets

            for w in widgets:
                widget = DashboardWidget(template=w) if isinstance(w, str) else w
                self._dashboard_widgets.append(widget)

        if settings_url is not None:
            self._settings_urls[(space, module)] = settings_url

    def get_topbar_entries(self, group: str | None = None) -> list[TopbarEntry]:
        """Return topbar entries, optionally filtered by group."""
        if group:
            return sorted(self._topbar_entries.get(group, []), key=lambda t: t.order)
        entries = []
        for group_entries in self._topbar_entries.values():
            entries.extend(group_entries)
        return sorted(entries, key=lambda t: (t.group, t.order))

    def get_sidebar(self, space: str, module: str) -> list[SidebarItem]:
        """Return sidebar items for a given space and module."""
        return self._sidebar.get((space, module), [])

    def get_shortcuts(self, space: str, module: str) -> list[Shortcut]:
        """Return topbar shortcuts for a given space and module."""
        return self._shortcuts.get((space, module), [])

    def get_settings_url(self, space: str, module: str) -> str | None:
        """Return the custom settings URL for a given space and module."""
        return self._settings_urls.get((space, module))

    def get_module_topbar(self, module: str) -> TopbarEntry | None:
        """Return the TopbarEntry associated with a specific module."""
        return self._module_topbar.get(module)

    def iter_modules(self, space: str | None = None) -> list[str]:
        """Return registered module names without exposing private storage.

        Args:
            space: Optional cabinet space filter. When omitted, modules from
                all spaces are returned.
        """
        modules: set[str] = set()
        for storage in (self._sidebar, self._shortcuts, self._settings_urls):
            for registered_space, module in storage:
                if space is None or registered_space == space:
                    modules.add(module)

        for module, spaces in self._module_spaces.items():
            if space is None or space in spaces:
                modules.add(module)

        return sorted(modules)

    def iter_sidebar(self, space: str | None = None) -> list[tuple[str, str, list[SidebarItem]]]:
        """Return sidebar registrations as ``(space, module, items)`` tuples."""
        entries = [
            (registered_space, module, list(items))
            for (registered_space, module), items in self._sidebar.items()
            if space is None or registered_space == space
        ]
        return sorted(entries, key=lambda entry: (entry[0], entry[1]))

    def get_default_module(self, space: str, group: str | None = None) -> str | None:
        """Return the first registered module for a cabinet space.

        The selection is deterministic and prefers topbar order when a module
        has a topbar declaration. ``None`` is returned when the registry has no
        module for the requested space.
        """
        candidates: list[tuple[int, str, str]] = []
        for module in self.iter_modules(space):
            topbar = self.get_module_topbar(module)
            if group is not None and (topbar is None or topbar.group != group):
                continue
            candidates.append((topbar.order if topbar else 999, str(topbar.label) if topbar else module, module))

        if not candidates:
            return None
        return sorted(candidates)[0][2]

    def get_module_config(self, space: str, module: str) -> CabinetModuleConfig:
        """Return a read-only snapshot for ``space``/``module``."""
        return CabinetModuleConfig(
            space=space,
            module=module,
            topbar=self.get_module_topbar(module),
            sidebar=list(self.get_sidebar(space, module)),
            shortcuts=list(self.get_shortcuts(space, module)),
            settings_url=self.get_settings_url(space, module),
        )

    # ------------------------------------------------------------------
    # V1 API — legacy (backward compatible)
    # ------------------------------------------------------------------

    def register(
        self,
        module_name: str,
        section: CabinetSection | None = None,
        dashboard_widget: DashboardWidget | str | None = None,
        topbar_actions: list[NavAction] | None = None,
        actions: list[NavAction] | None = None,
    ) -> None:
        """Register cabinet contributions (legacy API).

        .. deprecated:: Use :meth:`register_v2` with the two-space model.
        """
        if section:
            self._sections[module_name] = section

        if dashboard_widget:
            if isinstance(dashboard_widget, str):
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
    # V2 params
    space: str | None = None,
    topbar: TopbarEntry | None = None,
    sidebar: list[SidebarItem] | None = None,
    shortcuts: list[Shortcut] | None = None,
    settings_url: str | None = None,
    dashboard_widgets: list[DashboardWidget] | DashboardWidget | str | None = None,
    # V1 params (backward compat)
    section: CabinetSection | None = None,
    dashboard_widget: DashboardWidget | str | None = None,
    **kwargs: Any,
) -> None:
    """Public API for cabinet.py in feature apps. Analogous to admin.site.register().

    **New two-space API** (when ``space`` is provided)::

        declare(
            module="booking",
            space="staff",
            topbar=TopbarEntry(group="services", label="Booking", ...),
            sidebar=[SidebarItem(label="Schedule", url="booking:schedule", ...)],
            shortcuts=[Shortcut(label="New", url="booking:new", icon="bi-plus")],
        )

    **Legacy API** (when ``space`` is None)::

        declare(module="booking", section=CabinetSection(...))

    Args:
        module: Django app name or feature identifier.
        space: ``"staff"`` or ``"client"``. Activates v2 API when provided.
        topbar: Topbar dropdown entry (v2 only).
        sidebar: Sidebar navigation items (v2 only).
        shortcuts: Topbar shortcuts for this module (v2 only).
        section: Legacy :class:`CabinetSection` instance (v1 only).
        dashboard_widgets: Dashboard widget declaration (v2).
        dashboard_widget: Legacy dashboard widget declaration (v1).
        **kwargs: Additional keyword arguments forwarded to registry.
    """
    from django.core.exceptions import ImproperlyConfigured

    if space is not None:
        # V2 two-space API
        if space not in ("staff", "client"):
            raise ImproperlyConfigured(f"declare() space must be 'staff' or 'client', got '{space}'")
        cabinet_registry.register_v2(
            module=module,
            space=space,
            topbar=topbar,
            sidebar=sidebar,
            shortcuts=shortcuts,
            dashboard_widgets=dashboard_widgets or dashboard_widget,
            settings_url=settings_url,
        )
    else:
        # V1 legacy API
        if section is not None and not isinstance(section, CabinetSection):
            raise ImproperlyConfigured(
                f"cabinet.declare() section must be a CabinetSection instance, got {type(section)}"
            )
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


def configure_space(
    space: str,
    label: str | None = None,
    icon: str | None = None,
) -> None:
    """Configure space-wide metadata (branding, icon, etc).

    Example::

        configure_space(
            space="staff",
            label=_("Admin Panel"),
            icon="bi-shield-lock",
        )
    """
    if space not in ("staff", "client"):
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(f"configure_space() space must be 'staff' or 'client', got '{space}'")

    cabinet_registry.register_branding(space=space, label=label, icon=icon)
