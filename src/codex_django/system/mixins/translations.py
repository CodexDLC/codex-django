"""Reusable model mixin for editable static translations.

Examples:
    Keep simple key-value content in a project model::

        from codex_django.system.mixins.translations import AbstractStaticTranslation

        class StaticTranslation(AbstractStaticTranslation):
            pass
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from codex_django.core.mixins.models import TimestampMixin


class AbstractStaticTranslation(TimestampMixin):
    """Store editable key-value content fragments managed through Django admin.

    This mixin is useful for lightweight static copy that should be editable
    without introducing a more complex CMS or translation workflow.

    Admin:
        list_display:
            ("key", "updated_at")
        search_fields:
            ("key", "content")
        readonly_fields:
            ("created_at", "updated_at")
    """

    key = models.CharField(
        _("Key"),
        max_length=255,
        unique=True,
        help_text=_("Unique identifier for the content piece."),
    )
    content = models.TextField(
        _("Content"),
        blank=True,
        help_text=_("The translated content."),
    )

    class Meta:
        abstract = True
        verbose_name = _("Static Translation")
        verbose_name_plural = _("Static Translations")

    def __str__(self) -> str:
        """Return the translation key for admin and debug output."""
        return self.key
