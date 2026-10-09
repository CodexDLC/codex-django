<!-- DOC_TYPE: API -->

# Notifications Compatibility API

`codex_django.notifications` is a deprecated compatibility facade for `codex_django.messaging`.
Existing imports continue to resolve during the deprecation window, but new code should import from `codex_django.messaging`.

## Legacy imports

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

Equivalent canonical imports:

```python
from codex_django.messaging import (
    BaseMessagingEngine,
    MessagingPayloadBuilder,
    BaseEmailContentSelector,
    BaseEmailContentMixin,
    DjangoQueueAdapter,
    DjangoDirectAdapter,
    DjangoCacheAdapter,
    DjangoI18nAdapter,
    DjangoArqClient,
)
```

Package-level legacy symbol access emits `DeprecationWarning`. Submodule imports remain available so downstream test suites and older project code can migrate incrementally.

For the canonical API, use [Messaging Public API](messaging.md).
