"""Unit tests for NotificationPayloadBuilder."""

import pytest

from codex_django.notifications.builder import NotificationPayloadBuilder

pytestmark = pytest.mark.unit


@pytest.fixture
def builder():
    return NotificationPayloadBuilder()


class TestNotificationPayloadBuilderTemplate:
    def test_returns_mode_template(self, builder):
        payload = builder.build_template(
            notification_id="nid-1",
            recipient_email="a@b.com",
            template_name="t.html",
            subject="Hello",
            event_type="booking",
            context_data={},
            channels=["email"],
        )
        assert payload["mode"] == "template"

    def test_all_required_keys_present(self, builder):
        payload = builder.build_template(
            notification_id="nid-1",
            recipient_email="a@b.com",
            template_name="t.html",
            subject="Hello",
            event_type="booking",
            context_data={"key": "val"},
            channels=["email"],
        )
        for key in [
            "mode",
            "notification_id",
            "recipient_email",
            "recipient_phone",
            "client_name",
            "template_name",
            "subject",
            "event_type",
            "context_data",
            "channels",
            "language",
        ]:
            assert key in payload

    def test_default_language_is_de(self, builder):
        payload = builder.build_template(
            notification_id="x",
            recipient_email="a@b.com",
            template_name="t.html",
            subject="S",
            event_type="e",
            context_data={},
            channels=[],
        )
        assert payload["language"] == "de"

    def test_none_phone_preserved(self, builder):
        payload = builder.build_template(
            notification_id="x",
            recipient_email="a@b.com",
            recipient_phone=None,
            template_name="t.html",
            subject="S",
            event_type="e",
            context_data={},
            channels=[],
        )
        assert payload["recipient_phone"] is None

    def test_context_data_passthrough(self, builder):
        ctx = {"booking_id": 42, "name": "Alice"}
        payload = builder.build_template(
            notification_id="x",
            recipient_email="a@b.com",
            template_name="t.html",
            subject="S",
            event_type="e",
            context_data=ctx,
            channels=[],
        )
        assert payload["context_data"] == ctx

    def test_channels_preserved(self, builder):
        payload = builder.build_template(
            notification_id="x",
            recipient_email="a@b.com",
            template_name="t.html",
            subject="S",
            event_type="e",
            context_data={},
            channels=["email", "sms"],
        )
        assert payload["channels"] == ["email", "sms"]

    def test_values_roundtrip(self, builder):
        payload = builder.build_template(
            notification_id="nid-42",
            recipient_email="user@example.com",
            recipient_phone="+49123456",
            client_name="Max",
            template_name="emails/booking.html",
            subject="Buchung bestätigt",
            event_type="booking_confirmed",
            context_data={"date": "2025-01-06"},
            channels=["email"],
            language="de",
        )
        assert payload["notification_id"] == "nid-42"
        assert payload["recipient_email"] == "user@example.com"
        assert payload["recipient_phone"] == "+49123456"
        assert payload["client_name"] == "Max"
        assert payload["template_name"] == "emails/booking.html"
        assert payload["subject"] == "Buchung bestätigt"
        assert payload["event_type"] == "booking_confirmed"
        assert payload["language"] == "de"


class TestNotificationPayloadBuilderRendered:
    def test_returns_mode_rendered(self, builder):
        payload = builder.build_rendered(
            notification_id="nid-1",
            recipient_email="a@b.com",
            html_content="<p>Hi</p>",
            subject="Hello",
            event_type="booking",
            channels=["email"],
        )
        assert payload["mode"] == "rendered"

    def test_no_template_name_in_rendered_payload(self, builder):
        payload = builder.build_rendered(
            notification_id="x",
            recipient_email="a@b.com",
            html_content="<p>Hi</p>",
            subject="S",
            event_type="e",
            channels=[],
        )
        assert "template_name" not in payload

    def test_default_text_content_empty_string(self, builder):
        payload = builder.build_rendered(
            notification_id="x",
            recipient_email="a@b.com",
            html_content="<p>Hi</p>",
            subject="S",
            event_type="e",
            channels=[],
        )
        assert payload["text_content"] == ""

    def test_default_language_is_de(self, builder):
        payload = builder.build_rendered(
            notification_id="x",
            recipient_email="a@b.com",
            html_content="<p>Hi</p>",
            subject="S",
            event_type="e",
            channels=[],
        )
        assert payload["language"] == "de"

    def test_html_content_roundtrip(self, builder):
        html = "<h1>Hello World</h1><p>Content</p>"
        payload = builder.build_rendered(
            notification_id="x",
            recipient_email="a@b.com",
            html_content=html,
            subject="S",
            event_type="e",
            channels=[],
        )
        assert payload["html_content"] == html

    def test_all_required_keys_present(self, builder):
        payload = builder.build_rendered(
            notification_id="x",
            recipient_email="a@b.com",
            html_content="<p>Hi</p>",
            subject="S",
            event_type="e",
            channels=["email"],
        )
        for key in [
            "mode",
            "notification_id",
            "recipient_email",
            "recipient_phone",
            "client_name",
            "html_content",
            "text_content",
            "subject",
            "event_type",
            "channels",
            "language",
        ]:
            assert key in payload
