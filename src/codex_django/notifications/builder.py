"""Compatibility facade for :mod:`codex_django.messaging.builder`."""

from codex_django.messaging.builder import MessagingPayloadBuilder as NotificationPayloadBuilder

__all__ = ["NotificationPayloadBuilder"]
