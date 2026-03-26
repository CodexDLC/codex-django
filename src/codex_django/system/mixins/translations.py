from django.db import models
from django.utils.translation import gettext_lazy as _

from codex_django.core.mixins.models import TimestampMixin


class AbstractStaticTranslation(TimestampMixin):
    """
    Abstract model for static translations/content.
    Can be used for simple key-value content managed via admin.
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
        return self.key
