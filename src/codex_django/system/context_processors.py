from typing import Any

from django.apps import apps
from django.conf import settings
from django.http import HttpRequest

from codex_django.core.redis.managers.settings import SettingsProxy, get_site_settings_manager


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
    except (LookupError, Exception):
        # If something goes wrong (Redis down or model not found),
        # we return an empty proxy to avoid crashing the site.
        return {"site_settings": SettingsProxy({})}
