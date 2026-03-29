"""
codex_django.booking.mixins.appointment
========================================
Composable mixins for the appointment/booking record model.

Usage::

    from codex_django.booking.mixins import AbstractBookableAppointment

    class Appointment(AbstractBookableAppointment):
        master = models.ForeignKey("masters.Master", ...)
        service = models.ForeignKey("services.Service", ...)
        client = models.ForeignKey(settings.AUTH_USER_MODEL, ...)

        class Meta:
            verbose_name = _("Appointment")

FK fields are NOT included — the user defines them pointing at their
own Master/Service/Client models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppointmentStatusMixin(models.Model):
    """Appointment lifecycle status.

    Status constants are class-level attributes so that the adapter
    and selectors can reference them without hardcoding strings::

        Appointment.STATUS_PENDING
        Appointment.STATUS_CONFIRMED

    Admin fieldsets example::

        (_("Status"), {
            "fields": ("status",),
        }),
    """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUS_NO_SHOW = "no_show"
    STATUS_RESCHEDULE_PROPOSED = "reschedule_proposed"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_CONFIRMED, _("Confirmed")),
        (STATUS_CANCELLED, _("Cancelled")),
        (STATUS_COMPLETED, _("Completed")),
        (STATUS_NO_SHOW, _("No Show")),
        (STATUS_RESCHEDULE_PROPOSED, _("Reschedule Proposed")),
    ]

    ACTIVE_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_RESCHEDULE_PROPOSED]

    status = models.CharField(
        _("Status"),
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    class Meta:
        abstract = True


class AppointmentCoreMixin(models.Model):
    """Core booking data: when and how long.

    Admin fieldsets example::

        (_("Booking Details"), {
            "fields": ("datetime_start", "duration_minutes"),
        }),
    """

    datetime_start = models.DateTimeField(
        _("Start Time"),
        db_index=True,
    )
    duration_minutes = models.PositiveIntegerField(
        _("Duration (min)"),
    )

    class Meta:
        abstract = True


class AbstractBookableAppointment(
    AppointmentStatusMixin,
    AppointmentCoreMixin,
    models.Model,
):
    """Convenience base that assembles all appointment mixins.

    Usage::

        class Appointment(AbstractBookableAppointment):
            master = models.ForeignKey("masters.Master", on_delete=models.CASCADE)
            service = models.ForeignKey("services.Service", on_delete=models.CASCADE)
            client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

            class Meta:
                verbose_name = _("Appointment")
                ordering = ["-datetime_start"]
    """

    class Meta:
        abstract = True
