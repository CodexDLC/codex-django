"""Context processors for project-level system data.

This module injects site settings and editable static content into templates,
using the configured Django models and Redis-backed managers when available.
"""

import logging
from typing import Any

from django.apps import apps
from django.conf import settings
from django.http import HttpRequest

from codex_django.core.redis.managers.settings import SettingsProxy, get_site_settings_manager
from codex_django.core.redis.managers.static_content import get_static_content_manager

log = logging.getLogger(__name__)


def site_settings(request: HttpRequest) -> dict[str, Any]:
    """Expose cached site settings in templates via a safe proxy object.

    The processor reads the configured singleton settings model, loads its
    cached representation through the Redis-backed manager, and injects the
    result into templates as ``site_settings``. Missing configuration or
    cache failures degrade to an empty :class:`SettingsProxy`.

    Args:
        request: Incoming Django request. The request itself is unused but
            kept to satisfy the Django context processor contract.

    Returns:
        A template context mapping with the ``site_settings`` key containing
        a :class:`SettingsProxy` instance.
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
    """Expose static translation content as a simple template dictionary.

    The processor reads the configured translation model and materializes all
    ``key -> content`` pairs into the template context as ``static_content``.
    Missing configuration or query failures degrade to an empty dictionary.

    Args:
        request: Incoming Django request. The request itself is unused but
            kept to satisfy the Django context processor contract.

    Returns:
        A template context mapping with the ``static_content`` key.
    """
    model_path = getattr(settings, "CODEX_STATIC_TRANSLATION_MODEL", None)
    if not model_path:
        return {"static_content": {}}

    try:
        model = apps.get_model(model_path)
        manager = get_static_content_manager()
        data = manager.load_cached(model)
        return {"static_content": data}
    except Exception as e:
        log.warning("static_content context processor failed: %s", e)
        return {"static_content": {}}
