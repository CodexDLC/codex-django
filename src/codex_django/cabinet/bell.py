"""Deprecated compatibility wrapper.

Use ``codex_django.cabinet.notifications`` instead.
"""

from .notifications import NotificationItem, NotificationRegistry, bell_registry, notification_registry

BellRegistry = NotificationRegistry

__all__ = ["NotificationItem", "NotificationRegistry", "BellRegistry", "notification_registry", "bell_registry"]
