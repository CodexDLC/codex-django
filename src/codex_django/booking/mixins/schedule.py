"""
codex_django.booking.mixins.schedule
=====================================
Relational models for master working schedule and days off.

AbstractWorkingDay replaces JSONField ``work_days`` — gives proper SQL
filtering, per-day hours, and index support.

Usage::

    from codex_django.booking.mixins import AbstractWorkingDay, MasterDayOffMixin

    class MasterWorkingDay(AbstractWorkingDay):
        master = models.ForeignKey(
            "masters.Master",
            on_delete=models.CASCADE,
            related_name="working_days",
        )

        class Meta:
            verbose_name = _("Working Day")
            unique_together = [("master", "weekday")]

    class MasterDayOff(MasterDayOffMixin):
        master = models.ForeignKey(
            "masters.Master",
            on_delete=models.CASCADE,
            related_name="days_off",
        )

        class Meta:
            verbose_name = _("Day Off")
            unique_together = [("master", "date")]
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractWorkingDay(models.Model):
    """Per-weekday schedule for a master.

    FK to the master model is NOT included — the user adds it
    pointing at their own model.

    Admin fieldsets example::

        (_("Schedule"), {
            "fields": ("weekday", "start_time", "end_time", "break_start", "break_end"),
        }),
    """

    WEEKDAY_CHOICES = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]

    weekday = models.PositiveSmallIntegerField(
        _("Day of Week"),
        choices=WEEKDAY_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        db_index=True,
    )
    start_time = models.TimeField(_("Start Time"))
    end_time = models.TimeField(_("End Time"))
    break_start = models.TimeField(_("Break Start"), null=True, blank=True)
    break_end = models.TimeField(_("Break End"), null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        day_name = dict(self.WEEKDAY_CHOICES).get(self.weekday, self.weekday)
        return f"{day_name}: {self.start_time}–{self.end_time}"


class MasterDayOffMixin(models.Model):
    """A single day-off record for a master.

    FK to the master model is NOT included — the user adds it.

    Admin fieldsets example::

        (_("Day Off"), {
            "fields": ("date", "reason"),
        }),
    """

    date = models.DateField(_("Date"), db_index=True)
    reason = models.CharField(
        _("Reason"),
        max_length=255,
        blank=True,
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"Day off: {self.date}"
