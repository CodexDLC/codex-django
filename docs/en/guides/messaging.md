<!-- DOC_TYPE: GUIDE -->

# Messaging Guide

## When To Use It

Use `messaging` when your project needs a reusable Django-side messaging layer with:

- content models for editable email text
- payload builders and dispatch engines
- queue/direct delivery adapters
- abstract models for recipients, threads, messages, and campaigns
- audience and campaign batching primitives

`codex_django.messaging` is the canonical package.
`codex_django.notifications` remains available for one minor release as a deprecated compatibility path.

## Stable Entry Points

- `codex_django.messaging`
- `codex_django.messaging.adapters`
- `codex_django.messaging.mixins`
- `codex_django.messaging.cabinet`
- `codex_django.messaging.audience`
- `codex_django.messaging.campaigns`

## Migration From `notifications`

Replace:

```python
from codex_django.notifications import BaseNotificationEngine, NotificationPayloadBuilder
```

with:

```python
from codex_django.messaging import BaseMessagingEngine, MessagingPayloadBuilder
```

Other key migrations:

- `codex_django.notifications` -> `codex_django.messaging`
- `BaseNotificationEngine` -> `BaseMessagingEngine`
- `NotificationPayloadBuilder` -> `MessagingPayloadBuilder`
- `CONVERSATIONS_RECIPIENT_MODEL` -> `MESSAGING_RECIPIENT_MODEL`

## Delivery Modes

The runtime keeps the existing two-mode contract:

- `template`: worker renders the template from `template_name`
- `rendered`: host renders HTML/text before enqueueing

Decorator helpers make that split explicit:

- `@email_template(...)`
- `@email_rendered(...)`
- `@notification_handler(...)` for the fully generic path

## Related Reading

- Architecture: `messaging`
- API reference: `codex_django.messaging`
- Legacy compatibility: `notifications`

## Messaging Cabinet Integration

Use the cabinet feature layer when a project needs a staff mailbox and campaign
surface without coupling library code to project models.

1. Add concrete models by subclassing the abstract messaging models you need:
   `AbstractThread`, `AbstractMessage`, `AbstractMessageReply`,
   `AbstractCampaign`, `AbstractCampaignRecipient`, `AbstractSystemRecipient`,
   `AbstractEmailLog`, and `AbstractEmailSettings`.
2. Implement `MessagingBridge` in the project. The bridge reads concrete ORM
   data and returns typed state such as `MailboxState`, `CampaignListState`,
   `RecipientListState`, `DeliveryLogState`, and `MessagingSettingsState`.
3. Keep cabinet views thin: read query parameters, call the bridge, pass the
   state through `MessagingCabinetPresenter`, set
   `request.cabinet_module = "messaging"`, and render a project template.
4. Register navigation with `build_messaging_topbar()` and
   `build_messaging_sidebar()`. Pass settings through
   `declare(..., settings_url="cabinet:messaging_settings")`; settings are not
   a normal sidebar item.
5. Override `cabinet/messaging/...` templates when the project needs custom
   markup. The library ships fallback pages and reusable components under the
   same paths.

The default cabinet navigation is:

- Mailbox: operator inbox, thread detail, actions, and reply composer.
- Campaigns: broadcast list and campaign composer.
- Recipients: audience/recipient table.
- Delivery log: technical delivery audit table.

`Templates` is intentionally not a default top-level item. Template management
should become a campaign sub-flow or optional module only after a real
email/content template model exists.

Minimal Atlas-like registration:

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
