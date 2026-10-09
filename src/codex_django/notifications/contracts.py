"""Compatibility facade for :mod:`codex_django.messaging.contracts`."""

from codex_django.messaging.contracts import (
    ContentSelectorProtocol,
    NotificationDispatchSpec,
    NotificationEventHandler,
    QueueAdapterProtocol,
)

__all__ = [
    "ContentSelectorProtocol",
    "NotificationDispatchSpec",
    "NotificationEventHandler",
    "QueueAdapterProtocol",
]
