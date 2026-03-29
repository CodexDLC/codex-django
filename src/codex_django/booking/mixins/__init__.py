"""Composable abstract booking model mixins.

These exports provide the reusable field groups and abstract base classes used
to assemble booking-related models inside a concrete Django project.

Examples:
    Build a project appointment model::

        from codex_django.booking.mixins import AbstractBookableAppointment

        class Appointment(AbstractBookableAppointment):
            ...
"""

from .appointment import (
    AbstractBookableAppointment,
    AppointmentCoreMixin,
    AppointmentStatusMixin,
)
from .master import (
    AbstractBookableMaster,
    MasterBufferMixin,
    MasterCapacityMixin,
    MasterScheduleMixin,
    MasterTimezoneMixin,
)
from .schedule import AbstractWorkingDay, MasterDayOffMixin
from .service import (
    AbstractBookableService,
    ServiceDurationMixin,
    ServiceGapMixin,
    ServiceParallelMixin,
)
from .settings import (
    AbstractBookingSettings,
    BookingSettingsMixin,
    BookingSettingsSyncMixin,
)

__all__ = [
    # Master
    "MasterScheduleMixin",
    "MasterBufferMixin",
    "MasterCapacityMixin",
    "MasterTimezoneMixin",
    "AbstractBookableMaster",
    # Service
    "ServiceDurationMixin",
    "ServiceGapMixin",
    "ServiceParallelMixin",
    "AbstractBookableService",
    # Appointment
    "AppointmentStatusMixin",
    "AppointmentCoreMixin",
    "AbstractBookableAppointment",
    # Schedule
    "AbstractWorkingDay",
    "MasterDayOffMixin",
    # Settings
    "BookingSettingsMixin",
    "BookingSettingsSyncMixin",
    "AbstractBookingSettings",
]
