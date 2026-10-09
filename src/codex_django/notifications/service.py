"""Compatibility facade for :mod:`codex_django.messaging.service`."""

from codex_django.messaging.service import BaseMessagingEngine as BaseNotificationEngine

__all__ = ["BaseNotificationEngine"]
