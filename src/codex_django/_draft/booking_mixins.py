"""
BookableMasterMixin, BookableServiceMixin
=========================================
Django model mixins for booking engine integration.
"""

from django.db import models


class BookableMasterMixin(models.Model):
    """Mixin for the performer model (master, specialist, resource)."""

    work_start = models.TimeField(null=True, blank=True)
    work_end = models.TimeField(null=True, blank=True)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    buffer_between_minutes = models.PositiveIntegerField(null=True, blank=True)
    min_advance_minutes = models.PositiveIntegerField(null=True, blank=True)
    max_advance_days = models.PositiveIntegerField(null=True, blank=True)
    max_clients_parallel = models.PositiveSmallIntegerField(default=1)
    timezone = models.CharField(max_length=64, default="UTC")

    class Meta:
        abstract = True


class BookableServiceMixin(models.Model):
    """Mixin for the service model."""

    min_gap_after_minutes = models.PositiveIntegerField(default=0)
    parallel_ok = models.BooleanField(default=True)

    class Meta:
        abstract = True
