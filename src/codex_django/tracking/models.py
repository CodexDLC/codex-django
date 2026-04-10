"""Database models for flushed tracking snapshots."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class PageView(models.Model):
    """Aggregated daily page view counts flushed from Redis."""

    path = models.CharField(_("path"), max_length=500, db_index=True)
    date = models.DateField(_("date"), db_index=True)
    views = models.PositiveIntegerField(_("views"), default=0)

    class Meta:
        verbose_name = _("Page view")
        verbose_name_plural = _("Page views")
        constraints = [
            models.UniqueConstraint(fields=["path", "date"], name="codex_tracking_pageview_path_date_uniq"),
        ]
        ordering = ["-date", "-views", "path"]

    def __str__(self) -> str:
        return f"{self.date} {self.path} - {self.views}"
