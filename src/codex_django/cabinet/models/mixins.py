"""
Field mixins for cabinet domain models.

These mixins define the expected interface (which fields are required),
not the business logic (choices, validation). Developers declare their own
status choices etc. on the concrete model.

Usage in project:
    from codex_django.cabinet.models import AppointmentFieldsMixin

    class Appointment(AppointmentFieldsMixin):
        STATUS_PENDING = 'pending'
        STATUS_CONFIRMED = 'confirmed'
        STATUS_CHOICES = [(STATUS_PENDING, 'Pending'), (STATUS_CONFIRMED, 'Confirmed')]
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AppointmentFieldsMixin(models.Model):
    """Base fields mixin for appointments/bookings. No choices — developer defines them."""

    start_at = models.DateTimeField(_("Start"))
    end_at = models.DateTimeField(_("End"))
    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        abstract = True


class ClientFieldsMixin(models.Model):
    """Base fields mixin for client profiles."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    phone = models.CharField(_("Phone"), max_length=20, blank=True)

    class Meta:
        abstract = True


class ServiceFieldsMixin(models.Model):
    """Base fields mixin for services/offerings."""

    name = models.CharField(_("Name"), max_length=200)
    duration = models.PositiveIntegerField(_("Duration (minutes)"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        abstract = True
