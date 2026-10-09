<!-- DOC_TYPE: CONCEPT -->

# Модуль Notifications

## Статус

`codex_django.notifications` теперь deprecated compatibility facade для `codex_django.messaging`.
Он остается доступным на один minor release, чтобы существующие проекты могли мигрировать без жесткого import break.

## Compatibility Contract

Legacy package сохраняет старые имена:

- `BaseNotificationEngine` указывает на `BaseMessagingEngine`
- `NotificationPayloadBuilder` указывает на `MessagingPayloadBuilder`
- `NotificationEventRegistry` указывает на `MessagingEventRegistry`
- `notification_event_registry` это тот же global object, что и `messaging_event_registry`
- adapter, selector, contract и mixin import paths остаются importable

Package-level legacy symbol access выбрасывает `DeprecationWarning`. Тесты не должны превращать это предупреждение в ошибку, кроме случаев, когда они специально проверяют миграцию.

## Canonical Architecture

Основная runtime-архитектура теперь описана в [Messaging Module](messaging.md). Новый код должен использовать:

```python
from codex_django.messaging import BaseMessagingEngine, MessagingPayloadBuilder
```

Существующий код временно может продолжать импортировать:

```python
from codex_django.notifications import BaseNotificationEngine, NotificationPayloadBuilder
```

Этот путь является только compatibility layer и должен быть заменен до удаления фасада.
