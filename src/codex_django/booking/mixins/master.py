"""
codex_django.booking.mixins.master
===================================
Composable mixins for the master/resource/specialist model.

Usage::

    from codex_django.booking.mixins import AbstractBookableMaster

    class Master(AbstractBookableMaster):
        name = models.CharField(max_length=255)
        # ... project-specific fields

        class Meta:
            verbose_name = _("Master")

Or pick individual mixins::

    class Master(MasterScheduleMixin, MasterBufferMixin, models.Model):
        ...
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class MasterScheduleMixin(models.Model):
    """Default working hours and breaks.

    These serve as fallback values. Per-day overrides live in the
    ``AbstractWorkingDay`` relational model (see ``schedule.py``).

    Admin fieldsets example::

        (_("Working Hours"), {
            "fields": (
                "work_start", "work_end",
                "break_start", "break_end",
            ),
        }),
    """

    work_start = models.TimeField(_("Work Start"), null=True, blank=True)
    work_end = models.TimeField(_("Work End"), null=True, blank=True)
    break_start = models.TimeField(_("Break Start"), null=True, blank=True)
    break_end = models.TimeField(_("Break End"), null=True, blank=True)

    class Meta:
        abstract = True


class MasterBufferMixin(models.Model):
    """Buffer time and advance booking limits.

    Admin fieldsets example::

        (_("Booking Constraints"), {
            "fields": (
                "buffer_between_minutes",
                "min_advance_minutes",
                "max_advance_days",
            ),
            "classes": ("collapse",),
        }),
    """

    buffer_between_minutes = models.PositiveIntegerField(
        _("Buffer Between Appointments (min)"),
        null=True,
        blank=True,
        help_text=_("Overrides global default when set."),
    )
    min_advance_minutes = models.PositiveIntegerField(
        _("Minimum Advance Booking (min)"),
        null=True,
        blank=True,
        help_text=_("How far in advance a client must book."),
    )
    max_advance_days = models.PositiveIntegerField(
        _("Maximum Advance Booking (days)"),
        null=True,
        blank=True,
        help_text=_("How far ahead a client can book."),
    )

    class Meta:
        abstract = True


class MasterCapacityMixin(models.Model):
    """Parallel client capacity.

    Admin fieldsets example::

        (_("Capacity"), {
            "fields": ("max_clients_parallel",),
        }),
    """

    max_clients_parallel = models.PositiveSmallIntegerField(
        _("Max Parallel Clients"),
        default=1,
    )

    class Meta:
        abstract = True


class MasterTimezoneMixin(models.Model):
    """Individual timezone for the master.

    Falls back to the booking adapter timezone when empty.

    Admin fieldsets example::

        (_("Timezone"), {
            "fields": ("timezone",),
            "classes": ("collapse",),
        }),
    """

    timezone = models.CharField(
        _("Timezone"),
        max_length=64,
        default="UTC",
        blank=True,
    )

    class Meta:
        abstract = True


class AbstractBookableMaster(
    MasterScheduleMixin,
    MasterBufferMixin,
    MasterCapacityMixin,
    MasterTimezoneMixin,
    models.Model,
):
    """Convenience base that assembles all master mixins.

    Usage::

        class Master(AbstractBookableMaster):
            name = models.CharField(max_length=255)
            status = models.CharField(...)
            categories = models.ManyToManyField(...)

            class Meta:
                verbose_name = _("Master")
    """

    class Meta:
        abstract = True
