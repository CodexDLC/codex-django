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
    """Abstract model for storing email/notification content blocks.

    Subclasses may define ``CATEGORY_CHOICES`` to add admin dropdown options::

        class EmailContent(BaseEmailContentMixin):
            CATEGORY_CHOICES = [
                ("general", "General"),
                ("booking", "Booking"),
            ]

    Notes:
        Projects usually subclass this mixin in their own app so the content
        model can be registered in admin and translated by the chosen stack.
    """

    CATEGORY_CHOICES: list[tuple[str, str]] = []

    key = models.CharField(_("Key"), max_length=100, unique=True, db_index=True)
    category = models.CharField(_("Category"), max_length=64, blank=True, db_index=True)
    text = models.TextField(_("Text Content"))
    description = models.CharField(_("Description"), max_length=255, blank=True)

    class Meta:
        abstract = True
        ordering = ["category", "key"]

    def __str__(self) -> str:
        """Return a readable admin label for the content entry."""
        return f"[{self.category}] {self.key}"
