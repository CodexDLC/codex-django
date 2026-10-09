<!-- DOC_TYPE: GUIDE -->

# Messaging Guide

## Когда использовать

Используйте `messaging`, когда проекту нужен переиспользуемый Django-side messaging layer с:

- content models для редактируемого email-текста
- builders и dispatch engine
- queue/direct delivery adapters
- abstract models для recipients, threads, messages и campaigns
- audience и batching primitives для кампаний

`codex_django.messaging` теперь является canonical пакетом.
`codex_django.notifications` остается совместимым deprecated path на один minor release.

## Основные точки входа

- `codex_django.messaging`
- `codex_django.messaging.adapters`
- `codex_django.messaging.mixins`
- `codex_django.messaging.cabinet`
- `codex_django.messaging.audience`
- `codex_django.messaging.campaigns`

## Переход с `notifications`

Замените:

```python
from codex_django.notifications import BaseNotificationEngine, NotificationPayloadBuilder
```

на:

```python
from codex_django.messaging import BaseMessagingEngine, MessagingPayloadBuilder
```

Ключевые переименования:

- `codex_django.notifications` -> `codex_django.messaging`
- `BaseNotificationEngine` -> `BaseMessagingEngine`
- `NotificationPayloadBuilder` -> `MessagingPayloadBuilder`
- `CONVERSATIONS_RECIPIENT_MODEL` -> `MESSAGING_RECIPIENT_MODEL`

## Messaging Cabinet Integration

Используйте cabinet feature-layer, когда проекту нужен staff mailbox и
campaign surface без привязки библиотечного кода к concrete models проекта.

1. Создайте concrete models через нужные abstract messaging models:
   `AbstractThread`, `AbstractMessage`, `AbstractMessageReply`,
   `AbstractCampaign`, `AbstractCampaignRecipient`, `AbstractSystemRecipient`,
   `AbstractEmailLog`, `AbstractEmailSettings`.
2. Реализуйте `MessagingBridge` в проекте. Bridge читает project ORM и
   возвращает typed state: `MailboxState`, `CampaignListState`,
   `RecipientListState`, `DeliveryLogState`, `MessagingSettingsState`.
3. Держите cabinet views тонкими: прочитать query params, вызвать bridge,
   пропустить state через `MessagingCabinetPresenter`, выставить
   `request.cabinet_module = "messaging"` и отрендерить project template.
4. Регистрируйте навигацию через `build_messaging_topbar()` и
   `build_messaging_sidebar()`. Settings подключаются через
   `declare(..., settings_url="cabinet:messaging_settings")`, а не как обычный
   sidebar item.
5. Переопределяйте `cabinet/messaging/...` templates в проекте, когда нужен
   custom markup. Библиотека поставляет fallback pages и reusable components по
   тем же путям.

Default cabinet navigation:

- Mailbox: inbox оператора, thread detail, actions и reply composer.
- Campaigns: broadcast list и composer.
- Recipients: таблица аудитории/получателей.
- Delivery log: технический delivery audit table.

`Templates` намеренно не является default top-level item. Template management
должен стать sub-flow внутри Campaigns или optional module только после появления
реальной email/content template модели.

Минимальная Atlas-like регистрация:

```python
from codex_django.cabinet import declare
from codex_django.messaging.cabinet import build_messaging_sidebar, build_messaging_topbar
from django.urls import reverse_lazy

declare(
    module="messaging",
    space="staff",
    topbar=build_messaging_topbar(reverse_lazy("cabinet:messaging_mailbox")),
    sidebar=build_messaging_sidebar(
        mailbox_url=reverse_lazy("cabinet:messaging_mailbox"),
        campaigns_url=reverse_lazy("cabinet:messaging_campaigns"),
        recipients_url=reverse_lazy("cabinet:messaging_recipients"),
        delivery_log_url=reverse_lazy("cabinet:messaging_delivery_log"),
    ),
    settings_url="cabinet:messaging_settings",
)
```
