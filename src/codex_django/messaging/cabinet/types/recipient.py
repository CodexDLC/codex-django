"""Typed state contracts for messaging recipients cabinet views."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RecipientRowState:
    id: str
    email: str
    name: str = ""
    kind: str = ""
    locale: str = ""
    enabled: bool = True
    note: str = ""
    url: str = ""


@dataclass(frozen=True)
class RecipientListState:
    title: str = "Recipients"
    create_url: str = ""
    rows: list[RecipientRowState] = field(default_factory=list)
    filters: list[Any] = field(default_factory=list)
    total_count: int = 0
    empty_title: str = "No recipients"
    empty_message: str = "No recipients match the current filters."


__all__ = ["RecipientListState", "RecipientRowState"]
