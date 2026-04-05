"""
codex_django.notifications
==========================
Django-specific notification infrastructure for Codex projects.

Quick start::

    from codex_django.notifications import (
        DjangoArqClient,
        DjangoQueueAdapter,
        DjangoCacheAdapter,
        DjangoI18nAdapter,
        BaseEmailContentSelector,
        BaseNotificationEngine,
        BaseEmailContentMixin,
        NotificationPayloadBuilder,
    )
"""

from .adapters.arq_client import DjangoArqClient
from .adapters.cache_adapter import DjangoCacheAdapter
from .adapters.direct_adapter import DjangoDirectAdapter
from .adapters.i18n_adapter import DjangoI18nAdapter
from .adapters.queue_adapter import DjangoQueueAdapter
from .builder import NotificationPayloadBuilder
from .contracts import ContentSelectorProtocol, NotificationDispatchSpec, NotificationEventHandler, QueueAdapterProtocol
from .mixins.models import BaseEmailContentMixin
from .registry import NotificationEventRegistry, notification_event_registry, notification_handler
from .selector import BaseEmailContentSelector
from .service import BaseNotificationEngine

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
