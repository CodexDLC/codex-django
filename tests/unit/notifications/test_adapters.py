"""Unit tests for all notification adapters."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# DjangoArqClient
# ---------------------------------------------------------------------------


class TestDjangoArqClient:
    def test_enqueue_uses_injected_adapter_without_pool_creation(self):
        from codex_django.notifications.adapters.arq_client import DjangoArqClient

        mock_adapter = MagicMock()
        mock_adapter.enqueue.return_value = "job-123"

        with patch("arq.connections.create_pool", new=AsyncMock()) as mock_create_pool:
            arq = DjangoArqClient(adapter=mock_adapter)
            result = arq.enqueue("task", {"key": "val"})

        mock_create_pool.assert_not_called()
        mock_adapter.enqueue.assert_called_once_with("task", {"key": "val"})
        assert result == "job-123"

    def test_enqueue_delegates_to_platform_adapter(self):
        from codex_django.notifications.adapters.arq_client import DjangoArqClient

        mock_adapter = MagicMock()
        mock_adapter.enqueue.return_value = "job-123"

        with (
            patch("arq.connections.create_pool", new=AsyncMock(return_value=MagicMock())),
            patch(
                "codex_platform.notifications.delivery.ArqNotificationAdapter",
                return_value=mock_adapter,
            ),
        ):
            arq = DjangoArqClient()
            result = arq.enqueue("task", {"key": "val"})

        mock_adapter.enqueue.assert_called_once_with("task", {"key": "val"})
        assert result == "job-123"

    def test_enqueue_builds_adapter_from_injected_pool(self):
        from codex_django.notifications.adapters.arq_client import DjangoArqClient

        mock_pool = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter.enqueue.return_value = "job-123"

        with (
            patch("arq.connections.create_pool", new=AsyncMock()) as mock_create_pool,
            patch("codex_platform.notifications.delivery.ArqNotificationAdapter", return_value=mock_adapter) as factory,
        ):
            arq = DjangoArqClient(pool=mock_pool)
            result = arq.enqueue("task", {"key": "val"})

        mock_create_pool.assert_not_called()
        factory.assert_called_once_with(mock_pool)
        assert result == "job-123"

    async def test_aenqueue_delegates_to_platform_adapter(self):
        from codex_django.notifications.adapters.arq_client import DjangoArqClient

        mock_adapter = MagicMock()
        mock_adapter.enqueue_async = AsyncMock(return_value="job-async-1")

        with (
            patch("arq.connections.create_pool", new=AsyncMock(return_value=MagicMock())),
            patch(
                "codex_platform.notifications.delivery.ArqNotificationAdapter",
                return_value=mock_adapter,
            ),
        ):
            arq = DjangoArqClient()
            result = await arq.aenqueue("task", {"key": "val"})

        mock_adapter.enqueue_async.assert_called_once_with("task", {"key": "val"})
        assert result == "job-async-1"

    def test_build_redis_settings_uses_arq_redis_url(self):
        from codex_django.notifications.adapters.arq_client import DjangoArqClient

        with patch("codex_django.notifications.adapters.arq_client.settings") as mock_settings:
            mock_settings.ARQ_REDIS_URL = "rediss://user:pass@example.com:6380/2"  # pragma: allowlist secret
            mock_settings.REDIS_URL = None
            client = DjangoArqClient()
            redis_settings = client.build_redis_settings_from_django()

        assert redis_settings.host == "example.com"
        assert redis_settings.port == 6380
        assert redis_settings.username == "user"
        assert redis_settings.password == "pass"  # pragma: allowlist secret
        assert redis_settings.database == 2
        assert redis_settings.ssl is True

    def test_build_redis_settings_falls_back_to_django_redis_fields(self):
        from codex_django.notifications.adapters.arq_client import DjangoArqClient

        with patch("codex_django.notifications.adapters.arq_client.settings") as mock_settings:
            mock_settings.ARQ_REDIS_URL = None
            mock_settings.REDIS_URL = None
            mock_settings.REDIS_HOST = "redis"
            mock_settings.REDIS_PORT = 6390
            mock_settings.REDIS_PASSWORD = "secret"  # pragma: allowlist secret
            mock_settings.REDIS_DB = 3
            client = DjangoArqClient()
            redis_settings = client.build_redis_settings_from_django()

        assert redis_settings.host == "redis"
        assert redis_settings.port == 6390
        assert redis_settings.password == "secret"  # pragma: allowlist secret
        assert redis_settings.database == 3


# ---------------------------------------------------------------------------
# DjangoQueueAdapter
# ---------------------------------------------------------------------------


class TestDjangoQueueAdapterWithOnCommit:
    @pytest.fixture
    def mock_arq(self):
        arq = MagicMock()
        arq.enqueue.return_value = "job-123"
        arq.aenqueue = AsyncMock(return_value="async-job-1")
        return arq

    def test_enqueue_registers_on_commit_not_immediate(self, mock_arq):
        from codex_django.notifications.adapters.queue_adapter import DjangoQueueAdapter

        adapter = DjangoQueueAdapter(mock_arq, use_on_commit=True)
        mock_txn = MagicMock()
        with patch("codex_django.notifications.adapters.queue_adapter.transaction", mock_txn, create=True):
            # The lazy import means we need to patch at the right place
            # DjangoQueueAdapter imports transaction lazily inside enqueue()
            pass

        # Re-test with the actual Django transaction patched
        with patch("django.db.transaction") as mock_txn:
            result = adapter.enqueue("task", {"k": "v"})
            mock_txn.on_commit.assert_called_once()
            mock_arq.enqueue.assert_not_called()
            assert result is None

    def test_enqueue_without_on_commit_calls_arq_immediately(self, mock_arq):
        from codex_django.notifications.adapters.queue_adapter import DjangoQueueAdapter

        adapter = DjangoQueueAdapter(mock_arq, use_on_commit=False)
        result = adapter.enqueue("task", {"k": "v"})
        mock_arq.enqueue.assert_called_once_with("task", payload={"k": "v"})
        assert result == "job-123"

    async def test_aenqueue_calls_arq_aenqueue(self, mock_arq):
        from codex_django.notifications.adapters.queue_adapter import DjangoQueueAdapter

        adapter = DjangoQueueAdapter(mock_arq, use_on_commit=True)
        result = await adapter.aenqueue("task", {"k": "v"})
        mock_arq.aenqueue.assert_called_once_with("task", payload={"k": "v"})
        assert result == "async-job-1"

    def test_on_commit_lambda_calls_arq(self, mock_arq):
        """Verify the on_commit callback actually calls arq.enqueue when invoked."""
        from codex_django.notifications.adapters.queue_adapter import DjangoQueueAdapter

        adapter = DjangoQueueAdapter(mock_arq, use_on_commit=True)
        captured_callback = None

        def capture_callback(fn):
            nonlocal captured_callback
            captured_callback = fn

        with patch("django.db.transaction") as mock_txn:
            mock_txn.on_commit.side_effect = capture_callback
            adapter.enqueue("my_task", {"data": 1})

        assert captured_callback is not None
        captured_callback()
        mock_arq.enqueue.assert_called_once_with("my_task", payload={"data": 1})


# ---------------------------------------------------------------------------
# DjangoCacheAdapter
# ---------------------------------------------------------------------------


class TestDjangoCacheAdapter:
    @pytest.fixture
    def mock_manager(self):
        mgr = MagicMock()
        return mgr

    @pytest.fixture
    def adapter(self, mock_manager):
        from codex_django.notifications.adapters.cache_adapter import DjangoCacheAdapter

        with patch(
            "codex_django.notifications.adapters.cache_adapter.get_notifications_cache_manager",
            return_value=mock_manager,
        ):
            yield DjangoCacheAdapter(), mock_manager

    def test_get_delegates_to_manager(self):
        from codex_django.notifications.adapters.cache_adapter import DjangoCacheAdapter

        mgr = MagicMock()
        mgr.get.return_value = "cached-value"
        with patch(
            "codex_django.notifications.adapters.cache_adapter.get_notifications_cache_manager",
            return_value=mgr,
        ):
            result = DjangoCacheAdapter().get("my:key")
        mgr.get.assert_called_once_with("my:key")
        assert result == "cached-value"

    def test_get_returns_none_on_miss(self):
        from codex_django.notifications.adapters.cache_adapter import DjangoCacheAdapter

        mgr = MagicMock()
        mgr.get.return_value = None
        with patch(
            "codex_django.notifications.adapters.cache_adapter.get_notifications_cache_manager",
            return_value=mgr,
        ):
            assert DjangoCacheAdapter().get("missing") is None

    def test_set_delegates_to_manager(self):
        from codex_django.notifications.adapters.cache_adapter import DjangoCacheAdapter

        mgr = MagicMock()
        with patch(
            "codex_django.notifications.adapters.cache_adapter.get_notifications_cache_manager",
            return_value=mgr,
        ):
            DjangoCacheAdapter().set("my:key", "value", timeout=3600)
        mgr.set.assert_called_once_with("my:key", "value", timeout=3600)

    def test_get_calls_factory_each_time(self):
        """get_notifications_cache_manager is called on every .get() call."""
        from codex_django.notifications.adapters.cache_adapter import DjangoCacheAdapter

        mgr = MagicMock()
        mgr.get.return_value = None
        with patch(
            "codex_django.notifications.adapters.cache_adapter.get_notifications_cache_manager",
            return_value=mgr,
        ) as factory:
            adapter = DjangoCacheAdapter()
            adapter.get("key1")
            adapter.get("key2")
            assert factory.call_count == 2


# ---------------------------------------------------------------------------
# DjangoI18nAdapter
# ---------------------------------------------------------------------------


class TestDjangoI18nAdapter:
    def test_translation_override_calls_django_override(self):
        from codex_django.notifications.adapters.i18n_adapter import DjangoI18nAdapter

        adapter = DjangoI18nAdapter()
        mock_ctx = MagicMock()
        with patch("django.utils.translation.override", return_value=mock_ctx) as mock_override:
            result = adapter.translation_override("de")
            mock_override.assert_called_once_with("de")
            assert result is mock_ctx

    def test_translation_override_passes_language(self):
        from codex_django.notifications.adapters.i18n_adapter import DjangoI18nAdapter

        adapter = DjangoI18nAdapter()
        mock_ctx = MagicMock()
        with patch("django.utils.translation.override", return_value=mock_ctx) as mock_override:
            adapter.translation_override("ru")
            mock_override.assert_called_once_with("ru")

    def test_translation_override_is_usable_as_context_manager(self):
        from codex_django.notifications.adapters.i18n_adapter import DjangoI18nAdapter

        adapter = DjangoI18nAdapter()
        # Use a real contextmanager-compatible mock
        from contextlib import contextmanager

        @contextmanager
        def fake_override(lang):
            yield

        with patch("django.utils.translation.override", side_effect=fake_override), adapter.translation_override("de"):
            pass  # Should not raise


# ---------------------------------------------------------------------------
# DjangoDirectAdapter — rendered mode
# ---------------------------------------------------------------------------


class TestDjangoDirectAdapterRenderedMode:
    def _rendered_payload(self, recipient="a@b.com"):
        return {
            "mode": "rendered",
            "html_content": "<p>Hi</p>",
            "text_content": "Hi",
            "recipient_email": recipient,
            "subject": "Test Subject",
        }

    def test_send_mode_rendered_calls_send_mail(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(use_on_commit=False)
        with patch("django.core.mail.send_mail") as mock_send:
            adapter._send(self._rendered_payload())
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["subject"] == "Test Subject"
        assert call_kwargs["recipient_list"] == ["a@b.com"]
        assert call_kwargs["html_message"] == "<p>Hi</p>"

    def test_send_skips_when_no_recipient(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(use_on_commit=False)
        with patch("django.core.mail.send_mail") as mock_send:
            result = adapter._send(self._rendered_payload(recipient=""))
        mock_send.assert_not_called()
        assert result is None

    def test_enqueue_with_on_commit_wraps(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(use_on_commit=True)
        with patch("django.db.transaction") as mock_txn:
            result = adapter.enqueue("task", self._rendered_payload())
        mock_txn.on_commit.assert_called_once()
        assert result is None

    def test_enqueue_without_on_commit_calls_send_directly(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(use_on_commit=False)
        with patch.object(adapter, "_send", return_value=None) as mock_send:
            adapter.enqueue("task", self._rendered_payload())
        mock_send.assert_called_once_with(self._rendered_payload())

    async def test_aenqueue_returns_none(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(use_on_commit=False)
        with patch("django.core.mail.send_mail"):
            result = await adapter.aenqueue("task", self._rendered_payload())
        assert result is None

    def test_send_html_none_when_empty(self):
        """html_message should be None (not empty string) when html_content is ''."""
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(use_on_commit=False)
        payload = {
            "mode": "rendered",
            "html_content": "",
            "text_content": "Plain text",
            "recipient_email": "a@b.com",
            "subject": "S",
        }
        with patch("django.core.mail.send_mail") as mock_send:
            adapter._send(payload)
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["html_message"] is None


# ---------------------------------------------------------------------------
# DjangoDirectAdapter — template mode
# ---------------------------------------------------------------------------


class TestDjangoDirectAdapterTemplateMode:
    def _template_payload(self):
        return {
            "mode": "template",
            "template_name": "emails/t.html",
            "context_data": {"name": "Alice"},
            "recipient_email": "a@b.com",
            "subject": "S",
            "text_content": "",
        }

    def test_render_raises_without_renderer(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        adapter = DjangoDirectAdapter(renderer=None, use_on_commit=False)
        with pytest.raises(ValueError, match="renderer"):
            adapter._send(self._template_payload())

    def test_render_calls_renderer_and_sends(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<h1>Hello Alice</h1>"
        adapter = DjangoDirectAdapter(renderer=mock_renderer, use_on_commit=False)
        with patch("django.core.mail.send_mail") as mock_send:
            adapter._send(self._template_payload())
        mock_renderer.render.assert_called_once_with("emails/t.html", {"name": "Alice"})
        mock_send.assert_called_once()

    def test_render_html_content_used_in_send_mail(self):
        from codex_django.notifications.adapters.direct_adapter import DjangoDirectAdapter

        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<h1>Rendered</h1>"
        adapter = DjangoDirectAdapter(renderer=mock_renderer, use_on_commit=False)
        with patch("django.core.mail.send_mail") as mock_send:
            adapter._send(self._template_payload())
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["html_message"] == "<h1>Rendered</h1>"
