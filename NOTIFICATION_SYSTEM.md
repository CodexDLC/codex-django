# Notification System — Architecture Reference

> Временный справочный файл. Описывает текущее состояние и план переноса
> notification-инфраструктуры в `codex-django`.

---

## Текущее расположение кода

### codex-platform — ядро (не трогаем)
```
codex_platform/notifications/
  dto.py           — NotificationRecipient, NotificationPayloadDTO, TemplateNotificationDTO
  interfaces.py    — ContentProvider, ContentCacheAdapter (Protocols)
  channels.py      — NotificationChannel (EMAIL, TELEGRAM, SMS, WHATSAPP)
  orchestrator.py  — BaseDeliveryOrchestrator (tries channels in order)
  registry.py      — ChannelRegistry (register/build_channels)
  renderer.py      — TemplateRenderer (Jinja2, Mode 1 worker-side render)
  clients/smtp.py  — AsyncEmailClient (aiosmtplib) ← воркер использует напрямую
  delivery/
    base.py        — NotificationAdapter Protocol
    arq.py         — ArqNotificationAdapter
    direct.py      — DirectNotificationAdapter (in-process)

codex_platform/workers/arq/
  base.py          — BaseArqService (lazy pool init, async enqueue_job, requeue DLQ)
  config.py        — BaseWorkerConfig (SMTP + arq_redis_settings property)
  task_utils.py    — @arq_task decorator (retry backoff)

codex_platform/redis_service/
  service.py       — RedisService (hash/string/list/set/zset/json/pipeline)
  base.py          — BaseRedisManager
  keys.py          — BaseRedisKey (типизированные ключи)
  exceptions.py    — RedisServiceError, RedisConnectionError, RedisDataError
  managers/        — SiteSettingsManager и др.
```

### codex-django _draft/ — черновики (переносим в notifications/)
```
_draft/django_mail.py            — DjangoMailChannel
_draft/notification_mixins.py    — BaseEmailContentMixin
_draft/arq_client.py             — DjangoArqClient (неполный)
```

### lily_website — референс боевого проекта
```
codex_tools/notifications/
  service.py           — BaseNotificationEngine
  builder.py           — NotificationPayloadBuilder
  selector.py          — BaseEmailContentSelector
  adapters/
    django_adapter.py  — DjangoNotificationAdapter

features/system/
  models/email_content.py         — EmailContent(BaseEmailContentMixin)
  selectors/email_content.py      — selector singleton
  services/notification.py        — NotificationService + 10 send_* методов
  redis_managers/notification_cache_manager.py — seed_* методы для Telegram бота
```

---

## Поток данных

```
Событие (booking / cancel / contact)
  → NotificationService.send_*()
  → BaseNotificationEngine.dispatch()
  → BaseEmailContentSelector.get(key, lang)  ← EmailContent из БД (кеш 3600s)
  → NotificationPayloadBuilder.build()        ← payload dict
  → DjangoNotificationAdapter.enqueue()       ← Django cache + DjangoArqClient
  → ARQ / Redis queue
  → send_universal_notification_task (worker)
  → BaseDeliveryOrchestrator.deliver()
  → AsyncEmailClient (SMTP) + TelegramChannel (бот)
```

---

## Типы событий (NotificationEventType)

| Константа | Когда |
|-----------|-------|
| `BOOKING_RECEIVED` | Новая бронь создана |
| `APPOINTMENT_CONFIRMED` | Мастер подтвердил |
| `APPOINTMENT_CANCELLED` | Отмена |
| `APPOINTMENT_NO_SHOW` | Клиент не пришёл |
| `APPOINTMENT_RESCHEDULED` | Перенос |
| `APPOINTMENT_REMINDER` | Напоминание перед визитом |
| `GROUP_BOOKING` | Групповая запись |
| `CONTACT_REQUEST` | Обращение через форму |

---

## Цель: создать `codex_django/notifications/`

```
codex_django/notifications/
  __init__.py          — публичный API (__all__)
  builder.py           — NotificationPayloadBuilder
  service.py           — BaseNotificationEngine
  selector.py          — BaseEmailContentSelector
  mixins/
    models.py          — BaseEmailContentMixin (abstract)
  adapters/
    arq_client.py      — DjangoArqClient(BaseArqService) + a-методы + async_to_sync
    queue_adapter.py   — DjangoQueueAdapter → NotificationAdapter Protocol + on_commit
    cache_adapter.py   — DjangoCacheAdapter → ContentCacheAdapter Protocol
    i18n_adapter.py    — DjangoI18nAdapter → translation_override()
```

**Удалены:** `DjangoMailChannel` (воркер использует `AsyncEmailClient` из platform напрямую),
единый `DjangoNotificationAdapter` (разбит на 3 независимых адаптера).

И CLI блюпринты:
```
codex-django add-notifications --app system --worker
```

Генерирует: EmailContent модель, selector, NotificationService, ARQ task.

---

## Шаги выполнения

1. Создать `notifications/builder.py` + `service.py` + `selector.py` (без Django imports)
2. Создать `notifications/mixins/models.py` (BaseEmailContentMixin)
3. Продвинуть `_draft/arq_client.py` → `notifications/adapters/arq_client.py` (доделать)
4. Продвинуть `_draft/django_mail.py` → `notifications/adapters/django_mail.py`
5. Создать `notifications/adapters/django_adapter.py`
6. Написать `notifications/__init__.py` с `__all__`
7. Удалить черновики из `_draft/` (или forwarding imports)
8. Создать CLI блюпринты `cli/blueprints/notifications/` (.j2 шаблоны)
9. Добавить `add-notifications` команду в `cli/main.py`
10. Обновить `pyproject.toml` extras `[notifications]`
11. В lily_website заменить `codex_tools.notifications` → `codex_django.notifications`
