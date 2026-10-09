"""Typed state contracts for messaging campaign cabinet views."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .mailbox import MailboxActionState


@dataclass(frozen=True)
class CampaignStatusSummaryState:
    key: str
    label: str
    count: int = 0
    active: bool = False
    url: str = ""


@dataclass(frozen=True)
class CampaignRowState:
    id: str
    url: str
    subject: str
    status: str = "draft"
    status_label: str = ""
    locale: str = ""
    recipient_count: int = 0
    sent_count: int = 0
    failed_count: int = 0
    scheduled_at: str = ""
    sent_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class CampaignListState:
    title: str = "Campaigns"
    create_url: str = ""
    status_filters: list[CampaignStatusSummaryState] = field(default_factory=list)
    rows: list[CampaignRowState] = field(default_factory=list)
    empty_title: str = "No campaigns"
    empty_message: str = "Create a campaign to send a broadcast message."


@dataclass(frozen=True)
class CampaignComposerState:
    campaign_id: str = ""
    action_url: str = ""
    subject: str = ""
    body_text: str = ""
    template_key: str = ""
    locale: str = ""
    available_locales: list[tuple[str, str]] = field(default_factory=list)
    audience_summary: str = ""
    audience_filter: dict[str, Any] = field(default_factory=dict)
    recipients_preview: list[Any] = field(default_factory=list)
    submit_label: str = "Save campaign"
    test_send_url: str = ""
    schedule_url: str = ""
    recipients: list[Any] = field(default_factory=list)


@dataclass(frozen=True)
class CampaignDetailState:
    campaign: CampaignRowState
    body_preview: str = ""
    recipients: list[Any] = field(default_factory=list)
    actions: list[MailboxActionState] = field(default_factory=list)


__all__ = [
    "CampaignComposerState",
    "CampaignDetailState",
    "CampaignListState",
    "CampaignRowState",
    "CampaignStatusSummaryState",
]
