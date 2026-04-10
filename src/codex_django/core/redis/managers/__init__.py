"""Concrete Redis manager exports for core caching concerns."""

from .base import BaseDjangoRedisManager, get_default_redis_manager
from .booking import BookingCacheManager, get_booking_cache_manager
from .notifications import NotificationsCacheManager, get_notifications_cache_manager
from .seo import SeoRedisManager, get_seo_redis_manager
from .settings import DjangoSiteSettingsManager, get_site_settings_manager
from .static_content import StaticContentManager, get_static_content_manager

__all__ = [
    "BaseDjangoRedisManager",
    "get_default_redis_manager",
    "BookingCacheManager",
    "get_booking_cache_manager",
    "NotificationsCacheManager",
    "get_notifications_cache_manager",
    "SeoRedisManager",
    "get_seo_redis_manager",
    "DjangoSiteSettingsManager",
    "get_site_settings_manager",
    "StaticContentManager",
    "get_static_content_manager",
]
