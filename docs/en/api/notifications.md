<!-- DOC_TYPE: API -->

# Notifications Public API

The notifications package exposes the high-level delivery building blocks that projects compose into their own notification service layer.

## Stable imports

```python
from codex_django.notifications import (
    BaseNotificationEngine,
    NotificationPayloadBuilder,
    BaseEmailContentSelector,
    BaseEmailContentMixin,
    DjangoQueueAdapter,
    DjangoDirectAdapter,
    DjangoCacheAdapter,
    DjangoI18nAdapter,
    DjangoArqClient,
)
```

## Use cases

- Build a project-specific notification service on top of `BaseNotificationEngine`.
- Store localized subjects and content via `BaseEmailContentMixin` and `BaseEmailContentSelector`.
- Choose queue-based or direct-delivery adapters depending on runtime needs.

For detailed module docstrings, adapter internals, and selector implementation notes, open [Notifications internals](internal/notifications.md).
