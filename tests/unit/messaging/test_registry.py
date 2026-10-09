from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_django.messaging.contracts import NotificationDispatchSpec
from codex_django.messaging.registry import (
    MessagingEventRegistry,
    email_rendered,
    email_template,
    messaging_event_registry,
    notification_handler,
)
from codex_django.messaging.service import BaseMessagingEngine

pytestmark = pytest.mark.unit


def test_email_template_builds_notification_dispatch_spec():
    registry = MessagingEventRegistry()

    @registry.email_template("booking.confirmed", channels=["email"])
    def build_payload(booking_id: int = 42):
        return {
            "recipient_email": "a@b.com",
            "subject_key": "booking.confirmed.subject",
            "template_name": "emails/booking.html",
            "context": {"booking_id": booking_id},
        }

    specs = registry.build_specs("booking.confirmed", 7)
    assert specs == [
        NotificationDispatchSpec(
            recipient_email="a@b.com",
            subject_key="booking.confirmed.subject",
            event_type="booking.confirmed",
            channels=["email"],
            template_name="emails/booking.html",
            mode="template",
            context={"booking_id": 7},
        )
    ]


def test_email_rendered_builds_notification_dispatch_spec():
    registry = MessagingEventRegistry()

    @registry.email_rendered("compose.new", channels=["email"])
    def build_payload():
        return {
            "recipient_email": "a@b.com",
            "subject_key": "compose.new.subject",
            "html_content": "<p>Hello</p>",
            "text_content": "Hello",
        }

    specs = registry.build_specs("compose.new")
    assert specs[0].mode == "rendered"
    assert specs[0].html_content == "<p>Hello</p>"
    assert specs[0].text_content == "Hello"


def test_email_template_rejects_invalid_payload_at_registration_time():
    registry = MessagingEventRegistry()

    with pytest.raises(TypeError, match="missing required keys"):

        @registry.email_template("broken", channels=["email"])
        def build_payload():
            return {"recipient_email": "a@b.com", "subject_key": "broken.subject"}


def test_email_rendered_rejects_forbidden_template_name():
    registry = MessagingEventRegistry()

    with pytest.raises(TypeError, match="forbidden keys"):

        @registry.email_rendered("broken", channels=["email"])
        def build_payload():
            return {
                "recipient_email": "a@b.com",
                "subject_key": "broken.subject",
                "html_content": "<p>x</p>",
                "template_name": "emails/bad.html",
            }


async def test_dispatch_event_supports_mixed_registry_styles():
    original_handlers = dict(messaging_event_registry._handlers)
    messaging_event_registry._handlers.clear()
    try:

        @notification_handler("mixed.event")
        def generic_handler():
            return NotificationDispatchSpec(
                recipient_email="one@example.com",
                subject_key="mixed.subject",
                event_type="mixed.event",
                channels=["email"],
            )

        @email_template("mixed.event", channels=["email"])
        def template_handler():
            return {
                "recipient_email": "two@example.com",
                "subject_key": "mixed.subject",
                "template_name": "emails/mixed.html",
            }

        @email_rendered("mixed.event", channels=["email"])
        def rendered_handler():
            return {
                "recipient_email": "three@example.com",
                "subject_key": "mixed.subject",
                "html_content": "<p>Three</p>",
            }

        queue = MagicMock()
        queue.enqueue.return_value = "job-sync"
        queue.aenqueue = AsyncMock(return_value="job-async")
        selector = MagicMock()
        selector.get.return_value = "Subject"
        engine = BaseMessagingEngine(
            queue_adapter=queue,
            cache_adapter=MagicMock(),
            i18n_adapter=MagicMock(),
            selector=selector,
        )

        sync_results = engine.dispatch_event("mixed.event")
        async_results = await engine.adispatch_event("mixed.event")

        assert sync_results == ["job-sync", "job-sync", "job-sync"]
        assert async_results == ["job-async", "job-async", "job-async"]
    finally:
        messaging_event_registry._handlers.clear()
        messaging_event_registry._handlers.update(original_handlers)
