"""
codex_django.booking.mixins.service
====================================
Composable mixins for the bookable service model.

Usage::

    from codex_django.booking.mixins import AbstractBookableService

    class Service(AbstractBookableService):
        name = models.CharField(max_length=255)
        price = models.DecimalField(...)
        category = models.ForeignKey(...)

        class Meta:
            verbose_name = _("Service")
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceDurationMixin(models.Model):
    """Service duration in minutes.

    Admin fieldsets example::

        (_("Duration"), {
            "fields": ("duration",),
        }),
    """

    duration = models.PositiveIntegerField(
        _("Duration (min)"),
        help_text=_("Service duration in minutes."),
    )

    class Meta:
        abstract = True


class ServiceGapMixin(models.Model):
    """Minimum gap after this service before the next one starts.

    Admin fieldsets example::

        (_("Gap"), {
            "fields": ("min_gap_after_minutes",),
            "classes": ("collapse",),
        }),
    """

    min_gap_after_minutes = models.PositiveIntegerField(
        _("Gap After Service (min)"),
        default=0,
        help_text=_("Cleanup/preparation time after this service."),
    )

    class Meta:
        abstract = True


class ServiceParallelMixin(models.Model):
    """Controls whether this service can run in parallel with others.

    Admin fieldsets example::

        (_("Parallel Booking"), {
            "fields": ("parallel_ok", "parallel_group"),
            "classes": ("collapse",),
        }),
    """

    parallel_ok = models.BooleanField(
        _("Allow Parallel"),
        default=True,
        help_text=_("Whether this service can be performed alongside another."),
    )
    parallel_group = models.CharField(
        _("Parallel Group"),
        max_length=50,
        blank=True,
        help_text=_("Services in the same group can run simultaneously."),
    )

    class Meta:
        abstract = True


class AbstractBookableService(
    ServiceDurationMixin,
    ServiceGapMixin,
    ServiceParallelMixin,
    models.Model,
):
    """Convenience base that assembles all service mixins.

    Usage::

        class Service(AbstractBookableService):
            name = models.CharField(max_length=255)
            price = models.DecimalField(max_digits=10, decimal_places=2)

            class Meta:
                verbose_name = _("Service")
    """

    class Meta:
        abstract = True
