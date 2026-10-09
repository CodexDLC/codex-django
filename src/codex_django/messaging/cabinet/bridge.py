"""Project-owned bridge protocol for messaging cabinet integrations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from .types import (
    CampaignComposerState,
    CampaignDetailState,
    CampaignListState,
    DeliveryLogState,
    MailboxState,
    MessagingSettingsState,
    RecipientListState,
)


@dataclass(frozen=True)
class MessagingActionResult:
    ok: bool
    code: str
    message: str
    target_url: str = ""
    field_errors: dict[str, list[str]] = field(default_factory=dict)


class MessagingBridge(Protocol):
    """Project adapter that exposes messaging state and write actions to cabinet."""

    def get_mailbox_state(
        self,
        *,
        user: Any,
        folder: str = "inbox",
        thread_id: str | None = None,
        filters: Mapping[str, Any] | None = None,
    ) -> MailboxState: ...

    def get_campaign_list_state(
        self,
        *,
        user: Any,
        status: str = "all",
        filters: Mapping[str, Any] | None = None,
    ) -> CampaignListState: ...

    def get_campaign_detail_state(self, *, user: Any, campaign_id: str) -> CampaignDetailState: ...

    def get_campaign_composer_state(
        self,
        *,
        user: Any,
        campaign_id: str | None = None,
    ) -> CampaignComposerState: ...

    def get_recipient_list_state(
        self,
        *,
        user: Any,
        filters: Mapping[str, Any] | None = None,
    ) -> RecipientListState: ...

    def get_delivery_log_state(
        self,
        *,
        user: Any,
        filters: Mapping[str, Any] | None = None,
    ) -> DeliveryLogState: ...

    def get_settings_state(self, *, user: Any) -> MessagingSettingsState: ...

    def reply_to_thread(self, *, user: Any, thread_id: str, body: str) -> MessagingActionResult: ...

    def mark_thread_read(self, *, user: Any, thread_id: str) -> MessagingActionResult: ...

    def mark_thread_processed(self, *, user: Any, thread_id: str) -> MessagingActionResult: ...

    def mark_thread_spam(self, *, user: Any, thread_id: str) -> MessagingActionResult: ...

    def archive_thread(self, *, user: Any, thread_id: str) -> MessagingActionResult: ...

    def create_campaign(self, *, user: Any, payload: Mapping[str, Any]) -> MessagingActionResult: ...

    def update_campaign(self, *, user: Any, campaign_id: str, payload: Mapping[str, Any]) -> MessagingActionResult: ...

    def send_campaign(self, *, user: Any, campaign_id: str) -> MessagingActionResult: ...

    def send_test_campaign(self, *, user: Any, campaign_id: str, email: str) -> MessagingActionResult: ...

    def update_recipient(
        self, *, user: Any, recipient_id: str, payload: Mapping[str, Any]
    ) -> MessagingActionResult: ...

    def update_settings(self, *, user: Any, payload: Mapping[str, Any]) -> MessagingActionResult: ...


__all__ = ["MessagingActionResult", "MessagingBridge"]
