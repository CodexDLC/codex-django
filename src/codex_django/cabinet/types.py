from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- Widget data types (contracts) ---


@dataclass
class TableColumn:
    key: str
    label: str
    align: str = "left"
    bold: bool = False
    muted: bool = False
    sortable: bool = False
    badge_key: str | None = None
    icon_key: str | None = None


@dataclass
class ListItem:
    label: str
    value: str
    avatar: str | None = None
    sublabel: str | None = None
    subvalue: str | None = None


@dataclass
class MetricWidgetData:
    label: str
    value: str
    unit: str | None = None
    trend_value: str | None = None
    trend_label: str | None = None
    trend_direction: str = "neutral"  # 'up' | 'down' | 'neutral'
    icon: str | None = None


@dataclass
class TableWidgetData:
    columns: list[TableColumn]
    rows: list[dict[str, Any]]


@dataclass
class ListWidgetData:
    items: list[ListItem]
    title: str | None = None


# --- Registration contracts ---


@dataclass(frozen=True)
class DashboardWidget:
    """Declaration of a dashboard widget."""

    template: str
    col: str = "col-lg-6"
    lazy: bool = False
    nav_group: str = "admin"
    permissions: tuple[str, ...] = ()
    order: int = 99

    def __post_init__(self) -> None:
        from django.core.exceptions import ImproperlyConfigured

        if self.nav_group not in ("admin", "services", "client"):
            raise ImproperlyConfigured(
                f"DashboardWidget.nav_group must be 'admin', 'services' or 'client', got '{self.nav_group}'"
            )


@dataclass(frozen=True)
class NavAction:
    label: str
    url: str
    icon: str | None = None


@dataclass(frozen=True)
class CabinetSection:
    """Declaration of a cabinet navigation section.

    frozen=True: any attempt to mutate attributes after creation raises FrozenInstanceError.
    This protects the global cabinet_registry from accidental mutation in views/middleware.
    """

    label: str
    icon: str
    nav_group: str = "admin"  # 'admin' | 'services' | 'client'
    url: str | None = None  # None is valid for future dropdown parents
    permissions: tuple[str, ...] = ()  # tuple instead of list — hashable, frozen-compatible
    order: int = 99

    def __post_init__(self) -> None:
        from django.core.exceptions import ImproperlyConfigured

        if self.nav_group not in ("admin", "services", "client"):
            raise ImproperlyConfigured(
                f"CabinetSection.nav_group must be 'admin', 'services' or 'client', got '{self.nav_group}'"
            )
