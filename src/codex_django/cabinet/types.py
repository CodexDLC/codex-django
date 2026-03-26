from dataclasses import dataclass, field
from typing import Optional


# --- Widget contracts ---

@dataclass
class TableColumn:
    key: str
    label: str
    align: str = "left"
    bold: bool = False
    muted: bool = False
    sortable: bool = False
    badge_key: Optional[str] = None
    icon_key: Optional[str] = None


@dataclass
class ListItem:
    label: str
    value: str
    avatar: Optional[str] = None
    sublabel: Optional[str] = None
    subvalue: Optional[str] = None


@dataclass
class NavAction:
    label: str
    url: str
    icon: Optional[str] = None


# --- Registration contract ---

@dataclass(frozen=True)
class CabinetSection:
    """Declaration of a cabinet navigation section.

    frozen=True: any attempt to mutate attributes after creation raises FrozenInstanceError.
    This protects the global cabinet_registry from accidental mutation in views/middleware.
    """

    label: str
    icon: str
    nav_group: str = "admin"      # 'admin' | 'services'
    url: Optional[str] = None     # None is valid for future dropdown parents
    permissions: tuple[str, ...] = ()  # tuple instead of list — hashable, frozen-compatible
    order: int = 99

    def __post_init__(self) -> None:
        from django.core.exceptions import ImproperlyConfigured

        if self.nav_group not in ("admin", "services"):
            raise ImproperlyConfigured(
                f"CabinetSection.nav_group must be 'admin' or 'services', got '{self.nav_group}'"
            )
