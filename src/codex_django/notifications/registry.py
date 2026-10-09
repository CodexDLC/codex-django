"""Compatibility facade for :mod:`codex_django.messaging.registry`."""

from codex_django.messaging.registry import (
    MessagingEventRegistry as NotificationEventRegistry,
)
from codex_django.messaging.registry import (
    email_rendered,
    email_template,
    notification_handler,
)
from codex_django.messaging.registry import (
    messaging_event_registry as notification_event_registry,
)

__all__ = [
    "NotificationEventRegistry",
    "email_rendered",
    "email_template",
    "notification_event_registry",
    "notification_handler",
]
