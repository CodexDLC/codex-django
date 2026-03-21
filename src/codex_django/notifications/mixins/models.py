"""
BaseEmailContentMixin
=====================
Abstract Django model for storing notification content blocks in the DB.

Usage::

    from codex_django.notifications import BaseEmailContentMixin
    from django.db import models

    class EmailContent(BaseEmailContentMixin):
        class Meta(BaseEmailContentMixin.Meta):
            verbose_name = "Email Content"
            verbose_name_plural = "Email Contents"
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseEmailContentMixin(models.Model):
    """Abstract model for storing email/notification content blocks."""

    CATEGORY_CHOICES = [
        ("general", _("General / Shared")),
        ("booking", _("Booking System")),
        ("contacts", _("Contact Form / CRM")),
        ("marketing", _("Marketing / Newsletters")),
    ]

    key = models.CharField(_("Key"), max_length=100, unique=True, db_index=True)
    category = models.CharField(_("Category"), max_length=20, choices=CATEGORY_CHOICES, default="general")
    text = models.TextField(_("Text Content"))
    description = models.CharField(_("Description"), max_length=255, blank=True)

    class Meta:
        abstract = True
        ordering = ["category", "key"]

    def __str__(self) -> str:
        return f"[{self.category}] {self.key}"
