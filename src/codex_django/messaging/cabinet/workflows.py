"""HTTP-agnostic workflow helpers for messaging cabinet actions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .bridge import MessagingActionResult, MessagingBridge


class MessagingCabinetWorkflowService:
    """Validate simple cabinet payloads and delegate writes to a project bridge."""

    def __init__(self, bridge: MessagingBridge) -> None:
        self.bridge = bridge

    def reply(self, *, user: Any, thread_id: str, payload: Mapping[str, Any]) -> MessagingActionResult:
        body = self._string(payload.get("body"))
        if not body:
            return self._invalid("reply.invalid", "Reply body is required.", {"body": ["Reply body is required."]})
        return self.bridge.reply_to_thread(user=user, thread_id=thread_id, body=body)

    def mark_read(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return self.bridge.mark_thread_read(user=user, thread_id=thread_id)

    def mark_processed(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return self.bridge.mark_thread_processed(user=user, thread_id=thread_id)

    def mark_spam(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return self.bridge.mark_thread_spam(user=user, thread_id=thread_id)

    def archive(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return self.bridge.archive_thread(user=user, thread_id=thread_id)

    def save_campaign(
        self,
        *,
        user: Any,
        payload: Mapping[str, Any],
        campaign_id: str | None = None,
    ) -> MessagingActionResult:
        errors: dict[str, list[str]] = {}
        if not self._string(payload.get("subject")):
            errors["subject"] = ["Subject is required."]
        if not self._string(payload.get("body_text") or payload.get("body")):
            errors["body_text"] = ["Message body is required."]
        if errors:
            return self._invalid("campaign.invalid", "Campaign payload is invalid.", errors)
        if campaign_id:
            return self.bridge.update_campaign(user=user, campaign_id=campaign_id, payload=payload)
        return self.bridge.create_campaign(user=user, payload=payload)

    def send_campaign(self, *, user: Any, campaign_id: str) -> MessagingActionResult:
        return self.bridge.send_campaign(user=user, campaign_id=campaign_id)

    def send_test_campaign(self, *, user: Any, campaign_id: str, payload: Mapping[str, Any]) -> MessagingActionResult:
        email = self._string(payload.get("email"))
        if not email or "@" not in email:
            return self._invalid("campaign_test.invalid", "A valid email is required.", {"email": ["Enter an email."]})
        return self.bridge.send_test_campaign(user=user, campaign_id=campaign_id, email=email)

    def save_recipient(self, *, user: Any, recipient_id: str, payload: Mapping[str, Any]) -> MessagingActionResult:
        email = self._string(payload.get("email"))
        if not email or "@" not in email:
            return self._invalid("recipient.invalid", "A valid email is required.", {"email": ["Enter an email."]})
        return self.bridge.update_recipient(user=user, recipient_id=recipient_id, payload=payload)

    def save_settings(self, *, user: Any, payload: Mapping[str, Any]) -> MessagingActionResult:
        if not payload:
            return self._invalid(
                "settings.invalid",
                "Settings payload is empty.",
                {"__all__": ["No settings provided."]},
            )
        return self.bridge.update_settings(user=user, payload=payload)

    def dispatch(
        self,
        action: str,
        *,
        user: Any,
        payload: Mapping[str, Any] | None = None,
        thread_id: str = "",
        campaign_id: str = "",
        recipient_id: str = "",
    ) -> MessagingActionResult:
        payload = payload or {}
        if action == "reply":
            return self.reply(user=user, thread_id=thread_id, payload=payload)
        if action == "mark_read":
            return self.mark_read(user=user, thread_id=thread_id)
        if action == "mark_processed":
            return self.mark_processed(user=user, thread_id=thread_id)
        if action == "mark_spam":
            return self.mark_spam(user=user, thread_id=thread_id)
        if action == "archive":
            return self.archive(user=user, thread_id=thread_id)
        if action == "save_campaign":
            return self.save_campaign(user=user, campaign_id=campaign_id or None, payload=payload)
        if action == "send_campaign":
            return self.send_campaign(user=user, campaign_id=campaign_id)
        if action == "send_test_campaign":
            return self.send_test_campaign(user=user, campaign_id=campaign_id, payload=payload)
        if action == "save_recipient":
            return self.save_recipient(user=user, recipient_id=recipient_id, payload=payload)
        if action == "save_settings":
            return self.save_settings(user=user, payload=payload)
        return MessagingActionResult(ok=False, code="unknown_action", message=f"Unknown messaging action: {action}")

    @staticmethod
    def _string(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _invalid(code: str, message: str, field_errors: dict[str, list[str]]) -> MessagingActionResult:
        return MessagingActionResult(ok=False, code=code, message=message, field_errors=field_errors)


__all__ = ["MessagingCabinetWorkflowService"]
