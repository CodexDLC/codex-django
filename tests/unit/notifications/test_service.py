from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codex_django.notifications.contracts import NotificationDispatchSpec
from codex_django.notifications.service import BaseNotificationEngine


@pytest.fixture
def engine():
    return BaseNotificationEngine(
        queue_adapter=MagicMock(),
        cache_adapter=MagicMock(),
        i18n_adapter=MagicMock(),
        selector=MagicMock(),
    )


@pytest.mark.unit
def test_dispatch_rendered_mode(engine):
    engine.dispatch(
        recipient_email="a@b.com",
        subject_key="S",
        event_type="e",
        channels=[],
        mode="rendered",
        html_content="<h1>Hi</h1>",
    )
    assert engine._queue.enqueue.called


@pytest.mark.asyncio
@pytest.mark.unit
async def test_adispatch_template(engine):
    engine._queue.aenqueue = AsyncMock(return_value="job-async")
    result = await engine.adispatch(
        recipient_email="a@b.com", subject_key="S", event_type="e", channels=[], template_name="t.html"
    )
    assert result == "job-async"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_adispatch_spec(engine):
    spec = NotificationDispatchSpec(
        recipient_email="a@b.com",
        subject_key="S",
        event_type="e",
        channels=[],
    )
    engine._queue.aenqueue = AsyncMock(return_value="job-spec")
    result = await engine.adispatch_spec(spec)
    assert result == "job-spec"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_adispatch_event(engine):
    spec = NotificationDispatchSpec(
        recipient_email="a@b.com",
        subject_key="S",
        event_type="e",
        channels=[],
    )
    with patch("codex_django.notifications.registry.notification_event_registry.build_specs", return_value=[spec]):
        engine._queue.aenqueue = AsyncMock(return_value="job-event")
        results = await engine.adispatch_event("test_event")
    assert len(results) == 1
    assert results[0] == "job-event"
