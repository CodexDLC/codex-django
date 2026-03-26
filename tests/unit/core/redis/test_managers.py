from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codex_django.core.redis.managers.notifications import NotificationsCacheManager
from codex_django.core.redis.managers.seo import SeoRedisManager
from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager
from codex_django.system.redis.managers.fixtures import FixtureHashManager

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_redis_from_url():
    """Mock Redis.from_url to avoid actually connecting to localhost during unit tests."""
    with patch("codex_django.core.redis.managers.base.Redis.from_url", return_value=AsyncMock()):
        yield


@pytest.fixture
def seo_manager(mock_redis_from_url):
    mgr = SeoRedisManager()
    mgr.hash = AsyncMock()
    mgr.string = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_seo_manager_aget_page(seo_manager):
    seo_manager.hash.get_all.return_value = {"title": "Test Title"}
    result = await seo_manager.aget_page("home")
    seo_manager.hash.get_all.assert_called_once_with(seo_manager.make_key("static_page:home"))
    assert result == {"title": "Test Title"}


def test_seo_manager_get_page(seo_manager):
    seo_manager.hash.get_all.return_value = {"title": "Test Title"}
    result = seo_manager.get_page("home")
    assert result == {"title": "Test Title"}


@pytest.mark.asyncio
async def test_seo_manager_aset_page(seo_manager):
    await seo_manager.aset_page("home", {"title": "New"})
    seo_manager.hash.set_fields.assert_called_once_with(seo_manager.make_key("static_page:home"), {"title": "New"})
    seo_manager.string.expire.assert_not_called()


def test_seo_manager_set_page(seo_manager):
    seo_manager.set_page("home", {"title": "New"}, timeout=3600)
    seo_manager.hash.set_fields.assert_called_once_with(seo_manager.make_key("static_page:home"), {"title": "New"})
    seo_manager.string.expire.assert_called_once_with(seo_manager.make_key("static_page:home"), 3600)


def test_seo_manager_invalidate_page(seo_manager):
    seo_manager.invalidate_page("home")
    seo_manager.string.delete.assert_called_once_with(seo_manager.make_key("static_page:home"))


@pytest.fixture
def notif_manager(mock_redis_from_url):
    mgr = NotificationsCacheManager()
    mgr.string = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_notif_manager_aget(notif_manager):
    notif_manager.string.get.return_value = "val"
    result = await notif_manager.aget("key")
    assert result == "val"
    notif_manager.string.get.assert_called_once_with(notif_manager.make_key("key"))


def test_notif_manager_get(notif_manager):
    notif_manager.string.get.return_value = "val"
    assert notif_manager.get("key") == "val"


@pytest.mark.asyncio
async def test_notif_manager_aset(notif_manager):
    await notif_manager.aset("key", "val", timeout=10)
    notif_manager.string.set.assert_called_once_with(notif_manager.make_key("key"), "val", ttl=10)


def test_notif_manager_set(notif_manager):
    notif_manager.set("key", "val", timeout=10)
    notif_manager.string.set.assert_called_once_with(notif_manager.make_key("key"), "val", ttl=10)


@pytest.fixture
def settings_manager(mock_redis_from_url):
    mgr = DjangoSiteSettingsManager()
    mgr.hash = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_settings_manager_aload_cached(settings_manager):
    settings_manager.hash.get_all.return_value = {"sitename": "My Site"}
    res = await settings_manager.aload_cached(None)
    assert res == {"sitename": "My Site"}


def test_settings_manager_load_cached(settings_manager):
    settings_manager.hash.get_all.return_value = {"sitename": "My Site"}
    res = settings_manager.load_cached(None)
    assert res == {"sitename": "My Site"}


@pytest.mark.asyncio
async def test_settings_manager_asave_instance(settings_manager):
    mock_instance = MagicMock()
    mock_instance.to_dict.return_value = {"k": "v"}
    await settings_manager.asave_instance(mock_instance)
    settings_manager.hash.set_fields.assert_called_once_with(settings_manager.make_key("site_settings"), {"k": "v"})


def test_settings_manager_save_instance(settings_manager):
    mock_instance = MagicMock()
    mock_instance.to_dict.return_value = {"k": "v"}
    settings_manager.save_instance(mock_instance)
    settings_manager.hash.set_fields.assert_called_once_with(settings_manager.make_key("site_settings"), {"k": "v"})


@pytest.fixture
def fixtures_manager(mock_redis_from_url):
    mgr = FixtureHashManager()
    mgr.string = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_fixtures_manager_aget_hash(fixtures_manager):
    fixtures_manager.string.get.return_value = "hash123"
    assert await fixtures_manager.aget_hash("fix1") == "hash123"


def test_fixtures_manager_get_hash(fixtures_manager):
    fixtures_manager.string.get.return_value = "hash123"
    assert fixtures_manager.get_hash("fix1") == "hash123"


@pytest.mark.asyncio
async def test_fixtures_manager_aset_hash(fixtures_manager):
    await fixtures_manager.aset_hash("fix1", "hash123")
    fixtures_manager.string.set.assert_called_once_with(fixtures_manager.make_key("fixture:fix1"), "hash123")


def test_fixtures_manager_set_hash(fixtures_manager):
    fixtures_manager.set_hash("fix1", "hash123")
    fixtures_manager.string.set.assert_called_once_with(fixtures_manager.make_key("fixture:fix1"), "hash123")
