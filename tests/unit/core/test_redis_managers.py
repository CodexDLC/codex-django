from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codex_django.core.redis.managers.booking import BookingCacheManager
from codex_django.core.redis.managers.notifications import NotificationsCacheManager
from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager, SettingsProxy


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
