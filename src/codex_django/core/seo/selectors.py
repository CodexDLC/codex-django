import logging
from typing import Any

from django.apps import apps
from django.conf import settings
from django.core.cache import cache

log = logging.getLogger(__name__)


def get_static_page_seo(page_key: str) -> Any:
    """
    Gets SEO data for a static page by key.
    Uses cache for optimization.

    Requires CODEX_STATIC_PAGE_SEO_MODEL setting in settings.py.
    """
    cache_key = f"seo_cache_{page_key}"
    data = cache.get(cache_key)

    if data:
        return data

    model_path = getattr(settings, "CODEX_STATIC_PAGE_SEO_MODEL", None)
    if not model_path:
        return None

    try:
        model = apps.get_model(model_path)
        obj = model.objects.filter(page_key=page_key).first()
        if obj:
            # Cache the object
            cache.set(cache_key, obj, timeout=3600 * 24)
            return obj
    except Exception as e:
        log.warning(f"Error fetching static page SEO for key {page_key}: {e}")
        pass

    return None
