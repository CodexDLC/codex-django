"""
codex_django.booking
====================
Django adapter layer for the codex-services booking engine.

Provides composable model mixins, a Redis cache manager for busy slots,
an availability adapter bridging Django ORM ↔ ChainFinder, and
pure-function selectors for views.

Quick start::

    # models.py
    from codex_django.booking.mixins import (
        AbstractBookableMaster,
        AbstractBookableService,
        AbstractBookableAppointment,
        AbstractWorkingDay,
        MasterDayOffMixin,
        AbstractBookingSettings,
    )

    # selectors.py (in your feature app)
    from codex_django.booking.selectors import get_available_slots
    from codex_django.booking.adapters import DjangoAvailabilityAdapter
"""

from codex_django.booking.adapters import BookingCacheAdapter, DjangoAvailabilityAdapter
from codex_django.booking.mixins import (
    AbstractBookableAppointment,
    AbstractBookableMaster,
    AbstractBookableService,
    AbstractBookingSettings,
    AbstractWorkingDay,
    MasterDayOffMixin,
)

__all__ = [
    # Adapters
    "DjangoAvailabilityAdapter",
    "BookingCacheAdapter",
    # Mixins — abstract models
    "AbstractBookableMaster",
    "AbstractBookableService",
    "AbstractBookableAppointment",
    "AbstractWorkingDay",
    "MasterDayOffMixin",
    "AbstractBookingSettings",
]
