from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codex_django.core.redis import (
    NotificationsCacheManager as TopLevelNotificationsCacheManager,
)
from codex_django.core.redis import (
    StaticContentManager as TopLevelStaticContentManager,
)
from codex_django.core.redis import get_default_redis_manager
from codex_django.core.redis.managers.booking import BookingCacheManager
from codex_django.core.redis.managers.notifications import NotificationsCacheManager
from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager, SettingsProxy
from codex_django.core.redis.managers.static_content import StaticContentManager


@pytest.fixture
def base_mock():
    with patch("codex_django.core.redis.managers.base.Redis.from_url") as m:
        yield m


@pytest.mark.unit
def test_settings_proxy():
    proxy = SettingsProxy({"a": 1})
    assert proxy.a == 1
    assert proxy["a"] == 1
    assert proxy.b == ""


@pytest.mark.unit
def test_manager_settings_save_sync(base_mock):
    m = DjangoSiteSettingsManager()
    m.hash = MagicMock()
    # Mock asave_instance because it's called via async_to_sync
    with patch.object(m, "asave_instance", new_callable=AsyncMock) as mock_asave:
        m.save_instance(MagicMock())
        assert mock_asave.called


@pytest.mark.unit
def test_manager_booking_save_sync(base_mock):
    m = BookingCacheManager()
    with patch.object(m, "aset_busy", new_callable=AsyncMock) as mock_aset:
        m.set_busy("m1", "2024-01-01", [])
        assert mock_aset.called


@pytest.mark.unit
def test_manager_notification_save_sync(base_mock):
    m = NotificationsCacheManager()
    with patch.object(m, "aset", new_callable=AsyncMock) as mock_aset:
        m.set("k", "v")
        assert mock_aset.called


@pytest.mark.asyncio
@pytest.mark.unit
async def test_manager_aload_cached_disabled(base_mock):
    m = DjangoSiteSettingsManager()
    with patch.object(m, "_is_disabled", return_value=True):
        assert await m.aload_cached(MagicMock()) == {}


@pytest.mark.unit
def test_top_level_redis_exports_static_content_and_notifications():
    assert TopLevelStaticContentManager is StaticContentManager
    assert TopLevelNotificationsCacheManager is NotificationsCacheManager


@pytest.mark.unit
def test_get_default_redis_manager_uses_base_namespacing(base_mock, settings):
    settings.PROJECT_NAME = "project"
    manager = get_default_redis_manager(prefix="seo")

    assert manager.make_key("home") == "project:seo:home"
