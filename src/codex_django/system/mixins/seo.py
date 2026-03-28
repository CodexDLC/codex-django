"""Reusable SEO model mixins for named static pages.

Examples:
    Declare a project SEO model in the local ``system`` app::

        from codex_django.system.mixins.seo import AbstractStaticPageSeo

        class StaticPageSeo(AbstractStaticPageSeo):
            pass
"""

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from codex_django.core.mixins.models import SeoMixin, TimestampMixin
from codex_django.core.redis.managers.seo import get_seo_redis_manager


class AbstractStaticPageSeo(TimestampMixin, SeoMixin):
    """Store SEO metadata for named static pages with automatic cache invalidation.

    Saving the model invalidates the Redis entry managed by
    :func:`codex_django.core.redis.managers.seo.get_seo_redis_manager`.

    Admin:
        list_display:
            ("page_key", "seo_title", "updated_at")
        search_fields:
            ("page_key", "seo_title", "seo_description")
        readonly_fields:
            ("created_at", "updated_at")
    """

    page_key = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Page key"),
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """Return a readable admin label for the SEO record."""
        return f"SEO: {self.page_key}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Persist the SEO record and invalidate the cached page payload.

        Args:
            *args: Positional arguments forwarded to ``models.Model.save()``.
            **kwargs: Keyword arguments forwarded to ``models.Model.save()``.
        """
        super().save(*args, **kwargs)
        # Invalidate SEO cache using manager
        manager = get_seo_redis_manager()
        manager.invalidate_page(self.page_key)
