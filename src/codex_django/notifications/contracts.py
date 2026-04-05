"""Public contracts for the Django notification integration layer."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class NotificationDispatchSpec:
    """Normalized dispatch contract for one notification send request."""

    recipient_email: str
    subject_key: str
    event_type: str
    channels: list[str]
    subject: str = ""
    recipient_phone: str | None = None
    client_name: str = ""
    template_name: str = ""
    language: str = "de"
    mode: str | None = None
    html_content: str = ""
    text_content: str = ""
    context: dict[str, Any] = field(default_factory=dict)


class QueueAdapterProtocol(Protocol):
    """Minimal queue adapter contract required by the notification engine."""

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...

    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...


class ContentSelectorProtocol(Protocol):
    """Localized content lookup contract used by notification dispatch."""

    def get(self, key: str, language: str = "de") -> str | None: ...


class NotificationEventHandler(Protocol):
    """Decorator-friendly handler that yields one or more dispatch specs."""

    def __call__(self, *args: Any, **kwargs: Any) -> (
        NotificationDispatchSpec | Iterable[NotificationDispatchSpec] | None
    ): ...
