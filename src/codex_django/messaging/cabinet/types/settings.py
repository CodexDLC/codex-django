"""Typed state contracts for messaging settings cabinet views."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MessagingSettingsSection:
    key: str
    title: str
    description: str = ""
    fields: list[Any] = field(default_factory=list)


@dataclass(frozen=True)
class MessagingSettingsState:
    title: str = "Messaging settings"
    action_url: str = ""
    sections: list[MessagingSettingsSection] = field(default_factory=list)
    values: dict[str, Any] = field(default_factory=dict)
    submit_label: str = "Save settings"


__all__ = ["MessagingSettingsSection", "MessagingSettingsState"]
