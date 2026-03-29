"""Public cabinet integration API.

The :mod:`codex_django.cabinet` package exposes the registration contracts
that feature apps use to contribute navigation sections and dashboard widgets
to the cabinet UI.

Examples:
    Register a feature section from ``booking/cabinet.py``::

        from codex_django.cabinet import CabinetSection, declare

        declare(
            module="booking",
            section=CabinetSection(label="Bookings", icon="calendar", url="/cabinet/bookings/"),
        )
"""

from .registry import cabinet_registry, declare
from .types import CabinetSection, ListItem, NavAction, TableColumn

__all__ = [
    "declare",
    "cabinet_registry",
    "CabinetSection",
    "NavAction",
    "TableColumn",
    "ListItem",
]
