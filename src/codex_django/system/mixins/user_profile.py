"""
AbstractUserProfile
===================
Reusable abstract mixin for a user-profile model.

The target project inherits this class in its own concrete ``UserProfile``
(scaffolded by ``codex-django add-client-cabinet``).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class AbstractUserProfile(models.Model):
    """Base profile linked 1-to-1 to AUTH_USER_MODEL."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="profile",
    )

    # ── Personal data ──────────────────────────────────────────────
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    patronymic = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    # ── Acquisition ────────────────────────────────────────────────
    source = models.CharField(
        max_length=50,
        blank=True,
        help_text="How the profile was created: booking / form / manual / allauth",
    )
    notes = models.TextField(blank=True)

    # ── Meta timestamps ────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    # ── Helpers ─────────────────────────────────────────────────────

    def get_full_name(self) -> str:
        """Return «Last First Patronymic», trimmed."""
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p).strip()

    def get_initials(self) -> str:
        """Return up to two uppercase initials (first + last name)."""
        initials = ""
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        return initials or "?"
