"""Selectors for static-page SEO metadata.

Examples:
    Load cached SEO payload for a resolved page name::

        seo = get_static_page_seo("home")
"""

import logging
from typing import Any

from django.apps import apps
from django.conf import settings
from django.forms.models import model_to_dict

from codex_django.core.redis.managers.seo import get_seo_redis_manager

log = logging.getLogger(__name__)


def serialize_static_page_seo(obj: Any) -> dict[str, str]:
    """Serialize a static SEO model instance into a Redis-safe flat mapping."""
    data = obj.to_dict() if hasattr(obj, "to_dict") else model_to_dict(obj)
    return {k: str(v) if v is not None else "" for k, v in data.items()}


def get_static_page_seo(
    page_key: str,
    *,
    model_path: str | None = None,
    page_key_field: str | None = None,
    cache_manager: Any = None,
    timeout: int | None = None,
) -> Any:
    """Load SEO metadata for a static page, using Redis as a read-through cache.

    The helper first checks the centralized SEO Redis manager. On a cache
    miss, it resolves the model declared by
    ``settings.CODEX_STATIC_PAGE_SEO_MODEL``, fetches the matching record by
    ``page_key``, flattens it to a string-only mapping, and stores the result
    back in Redis.

    Args:
        page_key: Logical key that identifies the static page.
        model_path: Optional Django model path override.
        page_key_field: Optional model field used for the page lookup.
        cache_manager: Optional SEO cache manager override.
        timeout: Optional Redis cache TTL override.

    Returns:
        Cached or freshly loaded SEO data as a mapping-like object, or
        ``None`` when the model is not configured, the record does not exist,
        or loading fails.
    """
    manager = cache_manager or get_seo_redis_manager()

    cached_data = manager.get_page(page_key)
    if cached_data:
        return cached_data

    resolved_model_path = model_path or getattr(settings, "CODEX_STATIC_PAGE_SEO_MODEL", None)
    if not resolved_model_path:
        return None

    configured_lookup_field = getattr(settings, "CODEX_STATIC_PAGE_SEO_KEY_FIELD", "page_key")
    lookup_field = page_key_field or (
        configured_lookup_field if isinstance(configured_lookup_field, str) else "page_key"
    )
    configured_timeout = getattr(settings, "CODEX_STATIC_PAGE_SEO_CACHE_TIMEOUT", 3600 * 24)
    cache_timeout = timeout if timeout is not None else configured_timeout

    try:
        model = apps.get_model(resolved_model_path)
        obj = model.objects.filter(**{lookup_field: page_key}).first()
        if obj:
            flat_data = serialize_static_page_seo(obj)
            manager.set_page(page_key, mapping=flat_data, timeout=cache_timeout)
            return flat_data
    except Exception as e:
        log.warning(f"Error fetching static page SEO for key {page_key}: {e}")
        pass

    return None
