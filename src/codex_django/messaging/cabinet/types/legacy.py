"""Compatibility state contracts kept for old messaging cabinet imports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class InboxMessageState:
    thread_id: str
    subject: str
    preview: str
    sender_label: str = ""
    received_at: str = ""
    unread: bool = False
    status: str = "open"
    url: str = ""


@dataclass(frozen=True)
class InboxPanelState:
    threads: list[InboxMessageState] = field(default_factory=list)
    unread_count: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComposeFieldState:
    name: str
    label: str
    field_type: str = "text"
    value: str = ""
    placeholder: str = ""
    required: bool = False
    help_text: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class ComposeFormState:
    fields: list[ComposeFieldState] = field(default_factory=list)
    submit_label: str = "Send"
    action_url: str = ""
    cancel_url: str = ""


@dataclass(frozen=True)
class CampaignRecipientState:
    recipient_id: str
    email: str
    label: str = ""
    locale: str = "de"
    status: str = "queued"


@dataclass(frozen=True)
class RecipientPanelState:
    recipients: list[CampaignRecipientState] = field(default_factory=list)
    total_count: int = 0


__all__ = [
    "CampaignRecipientState",
    "ComposeFieldState",
    "ComposeFormState",
    "InboxMessageState",
    "InboxPanelState",
    "RecipientPanelState",
]
