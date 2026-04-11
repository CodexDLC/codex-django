"""
codex_django.booking.mixins.settings
======================================
Booking system configuration model mixins.

Usage::

    from codex_django.booking.mixins import AbstractBookingSettings

    class BookingSettings(AbstractBookingSettings):
        class Meta:
            verbose_name = _("Booking Settings")

    # In your Django settings:
    # CODEX_BOOKING_SETTINGS_MODEL = 'system.BookingSettings'
"""

import logging
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook

log = logging.getLogger(__name__)


class BookingSettingsMixin(models.Model):
    """Core booking configuration fields.

    Admin fieldsets example::

        (_("Booking Defaults"), {
            "fields": (
                "step_minutes",
                "default_buffer_between_minutes",
                "min_advance_minutes",
                "max_advance_days",
            ),
        }),
        (_("Monday"), {"fields": ("monday_is_closed", "work_start_monday", "work_end_monday")}),
        (_("Tuesday"), {"fields": ("tuesday_is_closed", "work_start_tuesday", "work_end_tuesday")}),
        (_("Wednesday"), {"fields": ("wednesday_is_closed", "work_start_wednesday", "work_end_wednesday")}),
        (_("Thursday"), {"fields": ("thursday_is_closed", "work_start_thursday", "work_end_thursday")}),
        (_("Friday"), {"fields": ("friday_is_closed", "work_start_friday", "work_end_friday")}),
        (_("Saturday"), {"fields": ("saturday_is_closed", "work_start_saturday", "work_end_saturday")}),
        (_("Sunday"), {"fields": ("sunday_is_closed", "work_start_sunday", "work_end_sunday")}),
    """

    step_minutes = models.PositiveIntegerField(
        _("Slot Step (min)"),
        default=30,
        help_text=_("Time grid granularity for the booking engine."),
    )
    default_buffer_between_minutes = models.PositiveIntegerField(
        _("Default Buffer Between Appointments (min)"),
        default=0,
    )
    min_advance_minutes = models.PositiveIntegerField(
        _("Minimum Advance Booking (min)"),
        default=60,
        help_text=_("Global minimum; masters can override individually."),
    )
    max_advance_days = models.PositiveIntegerField(
        _("Maximum Advance Booking (days)"),
        default=60,
    )

    # Default working hours (fallback when a resource has no individual schedule)
    monday_is_closed = models.BooleanField(_("Monday Closed"), default=False)
    work_start_monday = models.TimeField(_("Monday Start"), null=True, blank=True)
    work_end_monday = models.TimeField(_("Monday End"), null=True, blank=True)
    tuesday_is_closed = models.BooleanField(_("Tuesday Closed"), default=False)
    work_start_tuesday = models.TimeField(_("Tuesday Start"), null=True, blank=True)
    work_end_tuesday = models.TimeField(_("Tuesday End"), null=True, blank=True)
    wednesday_is_closed = models.BooleanField(_("Wednesday Closed"), default=False)
    work_start_wednesday = models.TimeField(_("Wednesday Start"), null=True, blank=True)
    work_end_wednesday = models.TimeField(_("Wednesday End"), null=True, blank=True)
    thursday_is_closed = models.BooleanField(_("Thursday Closed"), default=False)
    work_start_thursday = models.TimeField(_("Thursday Start"), null=True, blank=True)
    work_end_thursday = models.TimeField(_("Thursday End"), null=True, blank=True)
    friday_is_closed = models.BooleanField(_("Friday Closed"), default=False)
    work_start_friday = models.TimeField(_("Friday Start"), null=True, blank=True)
    work_end_friday = models.TimeField(_("Friday End"), null=True, blank=True)
    saturday_is_closed = models.BooleanField(_("Saturday Closed"), default=False)
    work_start_saturday = models.TimeField(_("Saturday Start"), null=True, blank=True)
    work_end_saturday = models.TimeField(_("Saturday End"), null=True, blank=True)
    sunday_is_closed = models.BooleanField(_("Sunday Closed"), default=False)
    work_start_sunday = models.TimeField(_("Sunday Start"), null=True, blank=True)
    work_end_sunday = models.TimeField(_("Sunday End"), null=True, blank=True)

    class Meta:
        abstract = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize concrete fields for Redis storage."""
        data: dict[str, Any] = {}
        for field in self._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.one_to_many:
                if field.name in ("id", "pk"):
                    continue
                value = getattr(self, field.name)
                data[field.name] = str(value) if value is not None else None
        return data

    def get_day_schedule(self, weekday: int) -> tuple[Any, Any] | None:
        """Return the configured fallback schedule for a weekday.

        Weekday numbering follows ``date.weekday()``:
        ``0=Monday`` ... ``6=Sunday``.
        """
        day_names = (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        )
        day_name = day_names[weekday]
        if getattr(self, f"{day_name}_is_closed", False):
            return None
        start_t = getattr(self, f"work_start_{day_name}", None)
        end_t = getattr(self, f"work_end_{day_name}", None)
        if not start_t or not end_t:
            return None
        return (start_t, end_t)


class BookingSettingsSyncMixin(LifecycleModelMixin, models.Model):
    """Sync booking settings to Redis on save.

    Follows rule R1: Redis errors are swallowed with logging so that
    a Redis outage never prevents saving settings in the database.
    """

    class Meta:
        abstract = True

    @hook(AFTER_SAVE)  # type: ignore[untyped-decorator]
    def sync_booking_settings_to_redis(self) -> None:
        """Persist the latest booking settings payload to Redis after save."""
        from django.conf import settings as django_settings

        if django_settings.DEBUG and not getattr(django_settings, "CODEX_REDIS_ENABLED", False):
            return

        try:
            from codex_django.core.redis.managers.booking import (
                get_booking_cache_manager,
            )

            manager = get_booking_cache_manager()
            if hasattr(self, "to_dict"):
                data = self.to_dict()
                if data:
                    key = manager.make_key("settings")
                    from asgiref.sync import async_to_sync

                    async_to_sync(manager.string.set)(key, str(data))
        except Exception:
            log.warning("Failed to sync booking settings to Redis", exc_info=True)


class AbstractBookingSettings(
    BookingSettingsMixin,
    BookingSettingsSyncMixin,
    models.Model,
):
    """Convenience base that assembles settings fields + Redis sync.

    Usage::

        class BookingSettings(AbstractBookingSettings):
            class Meta:
                verbose_name = _("Booking Settings")
    """

    class Meta:
        abstract = True
