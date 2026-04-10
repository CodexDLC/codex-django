"""Redis integration helpers used by the codex-django core modules.

This package re-exports the most common manager classes and factory
functions so projects can import them from a single place.
"""

from .managers import (
    BaseDjangoRedisManager,
    BookingCacheManager,
    DjangoSiteSettingsManager,
    NotificationsCacheManager,
    SeoRedisManager,
    StaticContentManager,
    get_booking_cache_manager,
    get_default_redis_manager,
    get_notifications_cache_manager,
    get_seo_redis_manager,
    get_site_settings_manager,
    get_static_content_manager,
)

__all__ = [
    "BaseDjangoRedisManager",
    "get_default_redis_manager",
    "BookingCacheManager",
    "get_booking_cache_manager",
    "NotificationsCacheManager",
    "get_notifications_cache_manager",
    "DjangoSiteSettingsManager",
    "get_site_settings_manager",
    "StaticContentManager",
    "get_static_content_manager",
    "SeoRedisManager",
    "get_seo_redis_manager",
]
