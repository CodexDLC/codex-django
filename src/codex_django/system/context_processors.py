import logging
from typing import Any

from django.apps import apps
from django.conf import settings
from django.http import HttpRequest

from codex_django.core.redis.managers.settings import SettingsProxy, get_site_settings_manager

log = logging.getLogger(__name__)


def site_settings(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor for accessing site settings from Redis.
    The object {{ site_settings }} is available in templates.

    Requires setting CODEX_SITE_SETTINGS_MODEL = 'app.ModelName' in settings.py.
    """
    model_path = getattr(settings, "CODEX_SITE_SETTINGS_MODEL", None)
    if not model_path:
        return {"site_settings": SettingsProxy({})}

    try:
        model = apps.get_model(model_path)
        manager = get_site_settings_manager()
        data = manager.load_cached(model)
        return {"site_settings": SettingsProxy(data)}
    except Exception as e:
        log.warning("site_settings context processor failed: %s", e)
        return {"site_settings": SettingsProxy({})}


def static_content(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor for accessing static translations/content.
    The object {{ static_content }} is available in templates.

    Requires setting CODEX_STATIC_TRANSLATION_MODEL = 'app.ModelName' in settings.py.
    """
    model_path = getattr(settings, "CODEX_STATIC_TRANSLATION_MODEL", None)
    if not model_path:
        return {"static_content": {}}

    try:
        model = apps.get_model(model_path)
        # For now, simple DB query. Can be cached in Redis later if needed.
        data = {obj.key: obj.content for obj in model.objects.all()}
        return {"static_content": data}
    except Exception as e:
        log.warning("static_content context processor failed: %s", e)
        return {"static_content": {}}
