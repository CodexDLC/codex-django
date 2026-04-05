"""Navigation contracts for the cabinet two-space model.

This module defines the dataclasses that feature apps use to register
navigation entries in the cabinet shell. All types here are immutable
(``frozen=True``) to prevent accidental mutation of the global registry.

Two-space model:
    - **staff** space (``/cabinet/``) — owners and administrators.
      Uses :class:`TopbarEntry` for the top navigation bar and
      :class:`SidebarItem` for the per-module sub-navigation.
    - **client** space (``/cabinet/my/``) — end-customers.
      Uses :class:`SidebarItem` only (no topbar dropdowns).

Typical usage in a feature app::

    # features/booking/cabinet.py
    from codex_django.cabinet import declare, TopbarEntry, SidebarItem, Shortcut

    declare(
        space="staff",
        module="booking",
        topbar=TopbarEntry(
            group="services",
            label="Booking",
            icon="bi-calendar-check",
            url="/cabinet/booking/",
            order=10,
        ),
        sidebar=[
            SidebarItem(label="Schedule",    url="booking:schedule",   icon="bi-calendar3"),
            SidebarItem(label="New Booking", url="booking:new",        icon="bi-plus-circle"),
            SidebarItem(label="Pending",     url="booking:pending",    icon="bi-hourglass-split",
                        badge_key="pending_count"),
        ],
        shortcuts=[
            Shortcut(label="New", url="booking:new", icon="bi-plus"),
        ],
    )

    declare(
        space="client",
        module="booking",
        sidebar=[
            SidebarItem(label="My Appointments", url="booking:my_bookings",
                        icon="bi-calendar2-check"),
        ],
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.utils.functional import Promise


@dataclass(frozen=True)
class TopbarEntry:
    """A navigation entry rendered inside a staff topbar dropdown group.

    The staff topbar contains two dropdown menus: **admin** (for management
    pages like analytics, users, and settings) and **services** (for feature
    modules like booking, catalog, etc.). Each :class:`TopbarEntry` declares
    which dropdown it belongs to via the ``group`` field.

    Entries within the same group are sorted ascending by ``order``.
    This class is ``frozen`` — instances are immutable after creation.

    Attributes:
        group: Dropdown group identifier. Must be ``"admin"`` or ``"services"``.
            ``"admin"`` — Администрирование dropdown (analytics, users, settings).
            ``"services"`` — Сервисы dropdown (booking, store, catalog, etc.).
        label: Human-readable display name shown in the topbar link.
        icon: Bootstrap Icons class name, e.g. ``"bi-calendar-check"``.
        url: Absolute URL or named URL string resolved by the template.
        order: Sort order within the group. Lower values appear first.
            Defaults to ``99`` (end of list).

    Raises:
        django.core.exceptions.ImproperlyConfigured: If ``group`` is not
            ``"admin"`` or ``"services"``.

    Example::

        TopbarEntry(
            group="services",
            label="Booking",
            icon="bi-calendar-check",
            url="/cabinet/booking/",
            order=10,
        )
    """

    group: str  # "admin" | "services"
    label: str | Promise
    icon: str
    url: str
    order: int = 99

    def __post_init__(self) -> None:
        from django.core.exceptions import ImproperlyConfigured

        if self.group not in ("admin", "services"):
            raise ImproperlyConfigured(f"TopbarEntry.group must be 'admin' or 'services', got '{self.group}'")


@dataclass(frozen=True)
class SidebarItem:
    """A sub-navigation link rendered in the cabinet module sidebar.

    When a view sets ``request.cabinet_module = "booking"``, the context
    processor fetches ``SidebarItem`` list registered for that space+module
    combination and exposes it as ``cabinet_sidebar``. The ``_sidebar_staff.html``
    or ``_sidebar_client.html`` template then renders each item via
    ``{% include "cabinet/includes/_nav_item.html" %}``.

    Items are sorted ascending by ``order`` at registration time.
    This class is ``frozen`` — instances are immutable after creation.

    Attributes:
        label: Display name of the navigation link.
        url: Named URL (e.g. ``"booking:schedule"``) or absolute path.
            Named URLs are resolved with ``{% url %}`` in the template.
        icon: Bootstrap Icons class name, e.g. ``"bi-calendar3"``.
            Empty string renders no icon.
        badge_key: Context variable name to read a numeric badge count from.
            If the context contains ``{ "pending_count": 3 }``, set
            ``badge_key="pending_count"`` to show a ``3`` badge on this item.
            Empty string disables the badge.
        order: Sort order within the sidebar. Lower values appear first.
            Defaults to ``99``.
        permissions: Tuple of Django permission strings. The item is hidden
            unless the user has **at least one** of the listed permissions.
            Empty tuple (default) means visible to all authenticated users.

    Example::

        SidebarItem(
            label="Pending",
            url="booking:pending",
            icon="bi-hourglass-split",
            badge_key="pending_count",
            order=3,
            permissions=("booking.view_appointment",),
        )
    """

    label: str | Promise
    url: str
    icon: str = ""
    badge_key: str = ""
    order: int = 99
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Shortcut:
    """A quick-action link rendered in the staff topbar for the active module.

    Shortcuts appear as small icon+label buttons in the topbar when the user
    is inside a specific cabinet module. They provide one-click access to
    the most common actions (e.g. "New Booking", "Add Client").

    Shortcuts are registered per ``space+module`` via :func:`codex_django.cabinet.declare`
    and exposed to templates as ``cabinet_shortcuts``.

    This class is ``frozen`` — instances are immutable after creation.

    Attributes:
        label: Short display name, e.g. ``"New"``, ``"Add Client"``.
        url: Named URL or absolute path for the link target.
        icon: Bootstrap Icons class name, e.g. ``"bi-plus"``.
            Empty string renders a text-only shortcut.

    Example::

        Shortcut(label="New Booking", url="booking:new", icon="bi-plus-circle")
    """

    label: str | Promise
    url: str
    icon: str = ""
