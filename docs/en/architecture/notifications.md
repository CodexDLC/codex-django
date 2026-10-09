<!-- DOC_TYPE: CONCEPT -->

# Notifications Module

## Status

`codex_django.notifications` is now a deprecated compatibility facade for `codex_django.messaging`.
It remains available for one minor release so existing projects can migrate without a hard import break.

## Compatibility Contract

The legacy package keeps the old names available:

- `BaseNotificationEngine` forwards to `BaseMessagingEngine`
- `NotificationPayloadBuilder` forwards to `MessagingPayloadBuilder`
- `NotificationEventRegistry` forwards to `MessagingEventRegistry`
- `notification_event_registry` is the same global object as `messaging_event_registry`
- adapter, selector, contract, and mixin import paths remain importable

Package-level legacy symbol access emits `DeprecationWarning`. Tests should not promote that warning to an error unless they deliberately cover the migration.

## Canonical Architecture

The canonical runtime architecture now lives in [Messaging Module](messaging.md). New code should use:

```python
from codex_django.messaging import BaseMessagingEngine, MessagingPayloadBuilder
```

Existing code can continue to import:

```python
from codex_django.notifications import BaseNotificationEngine, NotificationPayloadBuilder
```

That path is compatibility-only and should be migrated before the facade is removed.
