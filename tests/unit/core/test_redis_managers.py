from unittest.mock import MagicMock, patch

import pytest

from codex_django.core.redis import (
    NotificationsCacheManager as TopLevelNotificationsCacheManager,
)
from codex_django.core.redis import (
    StaticContentManager as TopLevelStaticContentManager,
)
from codex_django.core.redis import get_default_redis_manager
from codex_django.core.redis.managers.notifications import NotificationsCacheManager
from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager, SettingsProxy
from codex_django.core.redis.managers.static_content import StaticContentManager


@pytest.fixture
def base_mock():
    # We no longer patch Redis.from_url since we use instance-based mocking.
    # This fixture remains for compatibility with existing tests if any,
    # but we will remove the broken patch.
    yield MagicMock()


@pytest.mark.unit
def test_settings_proxy():
    proxy = SettingsProxy({"a": 1})
    assert proxy.a == 1
    assert proxy["a"] == 1
    assert proxy.b == ""


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
