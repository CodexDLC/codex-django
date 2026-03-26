import logging
from typing import Any

from django.apps import apps
from django.conf import settings
from django.forms.models import model_to_dict

from codex_django.core.redis.managers.seo import get_seo_redis_manager

log = logging.getLogger(__name__)


def get_static_page_seo(page_key: str) -> Any:
    """
    Gets SEO data for a static page by key.
    Uses centralized Redis manager for optimization via hashes.

    Requires CODEX_STATIC_PAGE_SEO_MODEL setting in settings.py.
    """
    manager = get_seo_redis_manager()

    cached_data = manager.get_page(page_key)
    if cached_data:
        return cached_data

    model_path = getattr(settings, "CODEX_STATIC_PAGE_SEO_MODEL", None)
    if not model_path:
        return None

    try:
        model = apps.get_model(model_path)
        obj = model.objects.filter(page_key=page_key).first()
        if obj:
            data = obj.to_dict() if hasattr(obj, "to_dict") else model_to_dict(obj)

            # Cache as Redis Hash (no JSON serialization needed)
            # Redis strictly requires string values for mapping. Convert all values to strings.
            flat_data = {k: str(v) if v is not None else "" for k, v in data.items()}

            manager.set_page(page_key, mapping=flat_data, timeout=3600 * 24)
            return flat_data
    except Exception as e:
        log.warning(f"Error fetching static page SEO for key {page_key}: {e}")
        pass

    return None
