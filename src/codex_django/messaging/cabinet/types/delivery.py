"""Typed state contracts for messaging delivery log cabinet views."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DeliveryLogRowState:
    id: str
    recipient: str = ""
    event_type: str = ""
    channel: str = "email"
    status: str = ""
    subject: str = ""
    queued_at: str = ""
    sent_at: str = ""
    error_message: str = ""
    provider_message_id: str = ""


@dataclass(frozen=True)
class DeliveryLogState:
    title: str = "Delivery log"
    rows: list[DeliveryLogRowState] = field(default_factory=list)
    filters: list[Any] = field(default_factory=list)
    empty_title: str = "No delivery events"
    empty_message: str = "Delivery events will appear after messages are queued or sent."


__all__ = ["DeliveryLogRowState", "DeliveryLogState"]
