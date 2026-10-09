"""Typed state contracts for messaging mailbox cabinet views."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MailboxFolderState:
    key: str
    label: str
    url: str
    icon: str = ""
    count: int = 0
    active: bool = False


@dataclass(frozen=True)
class MailboxThreadState:
    id: str
    url: str
    subject: str
    preview: str
    sender_name: str = ""
    sender_email: str = ""
    sender_label: str = ""
    received_at: str = ""
    status: str = "open"
    status_label: str = ""
    unread: bool = False
    channel: str = "email"
    topic: str = ""
    source: str = ""


@dataclass(frozen=True)
class MessageState:
    id: str
    direction: str
    sender_label: str
    body: str
    recipient_label: str = ""
    subject: str = ""
    created_at: str = ""
    channel: str = "email"
    attachments: list[Any] = field(default_factory=list)


@dataclass(frozen=True)
class ReplyComposerState:
    action_url: str
    method: str = "post"
    body_field_name: str = "body"
    submit_label: str = "Send reply"
    placeholder: str = ""
    disabled: bool = False


@dataclass(frozen=True)
class MailboxActionState:
    key: str
    label: str
    url: str
    method: str = "post"
    icon: str = ""
    variant: str = "secondary"
    confirm: str = ""


@dataclass(frozen=True)
class MailboxDetailState:
    thread: MailboxThreadState | None = None
    messages: list[MessageState] = field(default_factory=list)
    composer: ReplyComposerState | None = None
    actions: list[MailboxActionState] = field(default_factory=list)


@dataclass(frozen=True)
class MailboxState:
    title: str = "Mailbox"
    folders: list[MailboxFolderState] = field(default_factory=list)
    threads: list[MailboxThreadState] = field(default_factory=list)
    selected: MailboxDetailState | None = None
    search_query: str = ""
    active_folder: str = "inbox"
    empty_title: str = "No messages"
    empty_message: str = "There are no messages in this folder."


def build_default_mailbox_folders(*, base_url: str, active_folder: str = "inbox") -> list[MailboxFolderState]:
    """Return common mailbox folders that projects may override in their bridge."""
    definitions = [
        ("inbox", "Inbox", "bi-inbox"),
        ("unread", "Unread", "bi-envelope"),
        ("processed", "Processed", "bi-check2-circle"),
        ("spam", "Spam", "bi-exclamation-octagon"),
        ("archived", "Archived", "bi-archive"),
        ("all", "All", "bi-collection"),
    ]
    separator = "&" if "?" in base_url else "?"
    return [
        MailboxFolderState(
            key=key,
            label=label,
            icon=icon,
            url=f"{base_url}{separator}folder={key}",
            active=key == active_folder,
        )
        for key, label, icon in definitions
    ]


__all__ = [
    "MailboxActionState",
    "MailboxDetailState",
    "MailboxFolderState",
    "MailboxState",
    "MailboxThreadState",
    "MessageState",
    "ReplyComposerState",
    "build_default_mailbox_folders",
]
