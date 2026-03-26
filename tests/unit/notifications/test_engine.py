"""Unit tests for BaseNotificationEngine."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_django.notifications.service import BaseNotificationEngine

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_queue():
    q = MagicMock()
    q.enqueue.return_value = "job-1"
    q.aenqueue = AsyncMock(return_value="async-job-1")
    return q


@pytest.fixture
def mock_selector():
    sel = MagicMock()
    sel.get.return_value = "Test Subject"
    return sel


@pytest.fixture
def engine(mock_queue, mock_selector):
    return BaseNotificationEngine(
        queue_adapter=mock_queue,
        cache_adapter=MagicMock(),
        i18n_adapter=MagicMock(),
        selector=mock_selector,
    )


def _dispatch_kwargs(**overrides):
    base = {
        "recipient_email": "a@b.com",
        "event_type": "booking",
        "channels": ["email"],
        "subject_key": "booking_subject",
        "template_name": "emails/t.html",
        "language": "de",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# dispatch() — template mode
# ---------------------------------------------------------------------------

class TestBaseNotificationEngineDispatchTemplateMode:
    def test_dispatch_calls_selector_get(self, engine, mock_selector):
        engine.dispatch(**_dispatch_kwargs())
        mock_selector.get.assert_called_once_with("booking_subject", "de")

    def test_dispatch_enqueues_payload(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs())
        mock_queue.enqueue.assert_called_once()
        task_name, payload = mock_queue.enqueue.call_args[0]
        assert task_name == "send_universal_notification_task"
        assert payload["mode"] == "template"
        assert payload["recipient_email"] == "a@b.com"
        assert payload["subject"] == "Test Subject"

    def test_dispatch_returns_job_id(self, engine):
        result = engine.dispatch(**_dispatch_kwargs())
        assert result == "job-1"

    def test_dispatch_uses_default_mode_template(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs())
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["mode"] == "template"

    def test_dispatch_mode_override_to_rendered(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs(mode="rendered", html_content="<p>Hi</p>"))
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["mode"] == "rendered"
        assert payload["html_content"] == "<p>Hi</p>"

    def test_dispatch_subject_none_becomes_empty_string(self, engine, mock_queue, mock_selector):
        mock_selector.get.return_value = None
        engine.dispatch(**_dispatch_kwargs())
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["subject"] == ""

    def test_dispatch_uses_task_name_attribute(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs())
        task_name, _ = mock_queue.enqueue.call_args[0]
        assert task_name == "send_universal_notification_task"

    def test_dispatch_notification_id_is_uuid_string(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs())
        _, payload = mock_queue.enqueue.call_args[0]
        nid = payload["notification_id"]
        import uuid
        uuid.UUID(nid)  # raises if not valid UUID

    def test_dispatch_template_name_in_payload(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs(template_name="emails/booking.html"))
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["template_name"] == "emails/booking.html"

    def test_dispatch_extra_context_in_context_data(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs(booking_id=42, master_name="Anna"))
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["context_data"]["booking_id"] == 42
        assert payload["context_data"]["master_name"] == "Anna"

    def test_dispatch_language_in_payload(self, engine, mock_queue):
        engine.dispatch(**_dispatch_kwargs(language="ru"))
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["language"] == "ru"


# ---------------------------------------------------------------------------
# adispatch() — async
# ---------------------------------------------------------------------------

class TestBaseNotificationEngineAdispatch:
    async def test_adispatch_template_mode(self, engine, mock_queue):
        result = await engine.adispatch(**_dispatch_kwargs())
        mock_queue.aenqueue.assert_called_once()
        task_name, payload = mock_queue.aenqueue.call_args[0]
        assert payload["mode"] == "template"
        assert result == "async-job-1"

    async def test_adispatch_rendered_mode(self, engine, mock_queue):
        await engine.adispatch(**_dispatch_kwargs(mode="rendered", html_content="<h1>H</h1>"))
        _, payload = mock_queue.aenqueue.call_args[0]
        assert payload["mode"] == "rendered"
        assert payload["html_content"] == "<h1>H</h1>"

    async def test_adispatch_calls_selector(self, engine, mock_selector):
        await engine.adispatch(**_dispatch_kwargs(subject_key="my_key", language="ru"))
        mock_selector.get.assert_called_once_with("my_key", "ru")

    async def test_adispatch_uses_aenqueue_not_enqueue(self, engine, mock_queue):
        await engine.adispatch(**_dispatch_kwargs())
        mock_queue.aenqueue.assert_called_once()
        mock_queue.enqueue.assert_not_called()


# ---------------------------------------------------------------------------
# Subclassing
# ---------------------------------------------------------------------------

class TestBaseNotificationEngineSubclassing:
    def test_custom_task_name_used(self, mock_queue, mock_selector):
        class MyEngine(BaseNotificationEngine):
            task_name = "my_custom_task"

        eng = MyEngine(
            queue_adapter=mock_queue,
            cache_adapter=MagicMock(),
            i18n_adapter=MagicMock(),
            selector=mock_selector,
        )
        eng.dispatch(**_dispatch_kwargs())
        task_name, _ = mock_queue.enqueue.call_args[0]
        assert task_name == "my_custom_task"

    def test_custom_default_mode_rendered(self, mock_queue, mock_selector):
        class MyEngine(BaseNotificationEngine):
            mode = "rendered"

        eng = MyEngine(
            queue_adapter=mock_queue,
            cache_adapter=MagicMock(),
            i18n_adapter=MagicMock(),
            selector=mock_selector,
        )
        eng.dispatch(**_dispatch_kwargs())
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["mode"] == "rendered"

    def test_mode_kwarg_overrides_class_default(self, mock_queue, mock_selector):
        class RenderedEngine(BaseNotificationEngine):
            mode = "rendered"

        eng = RenderedEngine(
            queue_adapter=mock_queue,
            cache_adapter=MagicMock(),
            i18n_adapter=MagicMock(),
            selector=mock_selector,
        )
        eng.dispatch(**_dispatch_kwargs(mode="template", template_name="t.html"))
        _, payload = mock_queue.enqueue.call_args[0]
        assert payload["mode"] == "template"
