"""Deprecated compatibility facade for :mod:`codex_django.messaging`."""

from __future__ import annotations

import warnings

from codex_django import messaging as _messaging

__all__ = [
    "DjangoArqClient",
    "DjangoCacheAdapter",
    "DjangoDirectAdapter",
    "DjangoI18nAdapter",
    "DjangoQueueAdapter",
    "QueueAdapterProtocol",
    "ContentSelectorProtocol",
    "NotificationEventHandler",
    "NotificationDispatchSpec",
    "NotificationPayloadBuilder",
    "BaseEmailContentMixin",
    "BaseEmailContentSelector",
    "BaseNotificationEngine",
    "NotificationEventRegistry",
    "notification_event_registry",
    "notification_handler",
]

_ATTRIBUTE_MAP = {
    "DjangoArqClient": "DjangoArqClient",
    "DjangoCacheAdapter": "DjangoCacheAdapter",
    "DjangoDirectAdapter": "DjangoDirectAdapter",
    "DjangoI18nAdapter": "DjangoI18nAdapter",
    "DjangoQueueAdapter": "DjangoQueueAdapter",
    "QueueAdapterProtocol": "QueueAdapterProtocol",
    "ContentSelectorProtocol": "ContentSelectorProtocol",
    "NotificationEventHandler": "NotificationEventHandler",
    "NotificationDispatchSpec": "NotificationDispatchSpec",
    "NotificationPayloadBuilder": "MessagingPayloadBuilder",
    "BaseEmailContentMixin": "BaseEmailContentMixin",
    "BaseEmailContentSelector": "BaseEmailContentSelector",
    "BaseNotificationEngine": "BaseMessagingEngine",
    "NotificationEventRegistry": "MessagingEventRegistry",
    "notification_event_registry": "messaging_event_registry",
    "notification_handler": "notification_handler",
}


def __getattr__(name: str) -> object:
    if name not in _ATTRIBUTE_MAP:
        raise AttributeError(name)
    warnings.warn(
        "codex_django.notifications is deprecated; import from codex_django.messaging instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(_messaging, _ATTRIBUTE_MAP[name])
