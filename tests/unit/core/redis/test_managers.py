from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codex_django.core.redis.managers.booking import BookingCacheManager
from codex_django.core.redis.managers.notifications import NotificationsCacheManager
from codex_django.core.redis.managers.seo import SeoRedisManager
from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager
from codex_django.core.redis.managers.static_content import StaticContentManager
from codex_django.system.redis.managers.fixtures import FixtureHashManager
from codex_django.system.redis.managers.tokens import JsonActionTokenRedisManager

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


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


@pytest.mark.asyncio
async def test_seo_manager_aset_page_skips_empty_mapping(seo_manager):
    await seo_manager.aset_page("home", {})
    seo_manager.hash.set_fields.assert_not_called()
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


def test_settings_manager_load_cached_populates_from_db(settings_manager):
    settings_manager.hash.get_all.return_value = None
    instance = MagicMock()
    instance.to_dict.return_value = {"sitename": "From DB"}
    model_cls = MagicMock()
    model_cls.objects.first.return_value = instance

    res = settings_manager.load_cached(model_cls)

    assert res == {"sitename": "From DB"}
    model_cls.objects.first.assert_called_once_with()
    settings_manager.hash.set_fields.assert_called_once_with(
        settings_manager.make_key("site_settings"),
        {"sitename": "From DB"},
    )


def test_settings_manager_load_cached_returns_empty_without_to_dict(settings_manager):
    settings_manager.hash.get_all.return_value = None
    instance = MagicMock(spec=[])
    model_cls = MagicMock()
    model_cls.objects.first.return_value = instance

    res = settings_manager.load_cached(model_cls)

    assert res == {}
    settings_manager.hash.set_fields.assert_not_called()


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
def static_content_manager(mock_redis_from_url):
    mgr = StaticContentManager()
    mgr.hash = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_static_content_manager_aload_cached(static_content_manager):
    static_content_manager.hash.get_all.return_value = {"hero_title": "Welcome!"}
    res = await static_content_manager.aload_cached(None)
    assert res == {"hero_title": "Welcome!"}


def test_static_content_manager_load_cached(static_content_manager):
    static_content_manager.hash.get_all.return_value = {"hero_title": "Welcome!"}
    res = static_content_manager.load_cached(None)
    assert res == {"hero_title": "Welcome!"}


def test_static_content_manager_load_cached_populates_from_db(static_content_manager):
    static_content_manager.hash.get_all.return_value = None
    row1 = MagicMock(key="hero_title", content="Welcome!")
    row2 = MagicMock(key="cta_label", content="Book now")
    model_cls = MagicMock()
    model_cls.objects.all.return_value = [row1, row2]

    res = static_content_manager.load_cached(model_cls)

    assert res == {"hero_title": "Welcome!", "cta_label": "Book now"}
    static_content_manager.hash.set_fields.assert_called_once_with(
        static_content_manager.make_key("static_content"),
        {"hero_title": "Welcome!", "cta_label": "Book now"},
    )


def test_static_content_manager_load_cached_skips_empty_db_result(static_content_manager):
    static_content_manager.hash.get_all.return_value = None
    model_cls = MagicMock()
    model_cls.objects.all.return_value = []

    res = static_content_manager.load_cached(model_cls)

    assert res == {}
    static_content_manager.hash.set_fields.assert_not_called()


@pytest.mark.asyncio
async def test_static_content_manager_asave_mapping(static_content_manager):
    await static_content_manager.asave_mapping({"hero_title": "Welcome!"})
    static_content_manager.hash.set_fields.assert_called_once_with(
        static_content_manager.make_key("static_content"),
        {"hero_title": "Welcome!"},
    )


def test_static_content_manager_save_mapping(static_content_manager):
    static_content_manager.save_mapping({"hero_title": "Welcome!"})
    static_content_manager.hash.set_fields.assert_called_once_with(
        static_content_manager.make_key("static_content"),
        {"hero_title": "Welcome!"},
    )


@pytest.mark.asyncio
async def test_static_content_manager_asave_mapping_skips_empty_payload(static_content_manager):
    await static_content_manager.asave_mapping({})
    static_content_manager.hash.set_fields.assert_not_called()


@pytest.fixture
def booking_manager(mock_redis_from_url):
    mgr = BookingCacheManager()
    mgr.string = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_booking_manager_aget_busy_returns_none_on_miss(booking_manager):
    booking_manager.string.get.return_value = None

    assert await booking_manager.aget_busy("42", "2026-03-29") is None


@pytest.mark.asyncio
async def test_booking_manager_aget_busy_decodes_json(booking_manager):
    booking_manager.string.get.return_value = '[["2026-03-29T10:00", "2026-03-29T11:00"]]'

    result = await booking_manager.aget_busy("42", "2026-03-29")

    assert result == [["2026-03-29T10:00", "2026-03-29T11:00"]]


def test_booking_manager_set_busy(booking_manager):
    booking_manager.set_busy("42", "2026-03-29", [["10:00", "11:00"]], timeout=900)

    booking_manager.string.set.assert_called_once_with(
        booking_manager.make_key("busy:42:2026-03-29"),
        '[["10:00", "11:00"]]',
        ttl=900,
    )


def test_booking_manager_invalidate_master_date(booking_manager):
    booking_manager.invalidate_master_date("42", "2026-03-29")
    booking_manager.string.delete.assert_called_once_with(booking_manager.make_key("busy:42:2026-03-29"))


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


@pytest.fixture
def action_token_manager(mock_redis_from_url):
    mgr = JsonActionTokenRedisManager()
    mgr.string = AsyncMock()
    return mgr


@pytest.mark.asyncio
async def test_action_token_manager_acreate_token(action_token_manager):
    with patch.object(action_token_manager, "make_token", return_value="token123"):
        token = await action_token_manager.acreate_token({"appointment_id": 1}, ttl_hours=2)

    assert token == "token123"
    action_token_manager.string.set.assert_called_once_with(
        action_token_manager.make_key("token123"),
        '{"appointment_id": 1}',
        ttl=7200,
    )


def test_action_token_manager_create_token(action_token_manager):
    with patch.object(action_token_manager, "make_token", return_value="token123"):
        token = action_token_manager.create_token({"appointment_id": 1}, ttl_seconds=60)

    assert token == "token123"
    action_token_manager.string.set.assert_called_once_with(
        action_token_manager.make_key("token123"),
        '{"appointment_id": 1}',
        ttl=60,
    )


@pytest.mark.asyncio
async def test_action_token_manager_aget_token_data(action_token_manager):
    action_token_manager.string.get.return_value = '{"appointment_id": 1}'

    assert await action_token_manager.aget_token_data("token123") == {"appointment_id": 1}
    action_token_manager.string.get.assert_called_once_with(action_token_manager.make_key("token123"))


@pytest.mark.asyncio
async def test_action_token_manager_aget_token_data_returns_none_for_bad_json(action_token_manager):
    action_token_manager.string.get.return_value = "{"

    assert await action_token_manager.aget_token_data("token123") is None


@pytest.mark.asyncio
async def test_action_token_manager_aget_token_data_returns_none_for_non_mapping(action_token_manager):
    action_token_manager.string.get.return_value = '["not", "a", "dict"]'

    assert await action_token_manager.aget_token_data("token123") is None


def test_action_token_manager_get_token_data(action_token_manager):
    action_token_manager.string.get.return_value = '{"appointment_id": 1}'

    assert action_token_manager.get_token_data("token123") == {"appointment_id": 1}


@pytest.mark.asyncio
async def test_action_token_manager_adelete_token(action_token_manager):
    await action_token_manager.adelete_token("token123")

    action_token_manager.string.delete.assert_called_once_with(action_token_manager.make_key("token123"))


def test_action_token_manager_delete_token(action_token_manager):
    action_token_manager.delete_token("token123")

    action_token_manager.string.delete.assert_called_once_with(action_token_manager.make_key("token123"))


@pytest.mark.asyncio
async def test_action_token_manager_disabled_returns_token_without_storing(action_token_manager, settings):
    settings.DEBUG = True
    settings.CODEX_REDIS_ENABLED = False

    with patch.object(action_token_manager, "make_token", return_value="token123"):
        token = await action_token_manager.acreate_token({"appointment_id": 1})

    assert token == "token123"
    action_token_manager.string.set.assert_not_called()
