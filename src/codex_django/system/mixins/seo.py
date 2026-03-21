from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from codex_django.core.mixins.models import SeoMixin, TimestampMixin
from codex_django.core.redis.managers.seo import get_static_page_seo_manager


class AbstractStaticPageSeo(TimestampMixin, SeoMixin):
    """
    Abstract model for static page SEO.
    Contains basic cache invalidation logic.
    """

    page_key = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Page key"),
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"SEO: {self.page_key}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        # Invalidate SEO cache using manager
        manager = get_static_page_seo_manager()
        manager.invalidate_page(self.page_key)
