<!-- DOC_TYPE: API -->

# Messaging Public API

`codex_django.messaging` is the canonical public package for Django-side messaging.

## Stable imports

```python
from codex_django.messaging import (
    BaseMessagingEngine,
    MessagingPayloadBuilder,
    BaseEmailContentSelector,
    BaseEmailContentMixin,
    AbstractEmailSettings,
    EmailSettingsSyncMixin,
    DjangoQueueAdapter,
    DjangoDirectAdapter,
    DjangoCacheAdapter,
    DjangoI18nAdapter,
    DjangoArqClient,
    email_template,
    email_rendered,
    notification_handler,
    BaseAudienceBuilder,
    CampaignService,
    MessagingBridge,
    MailboxState,
    CampaignListState,
    RecipientListState,
    DeliveryLogState,
    MessagingCabinetPresenter,
    MessagingCabinetWorkflowService,
)
```

## Use cases

- Build a project messaging service on top of `BaseMessagingEngine`
- Register template/rendered event builders with explicit decorators
- Reuse abstract models for email settings, recipients, threads, and campaigns
- Stream recipients via `BaseAudienceBuilder`
- Batch campaign dispatch through `CampaignService`
- Build reusable cabinet mailbox, campaign, recipient, delivery log, and
  settings views via `codex_django.messaging.cabinet`

## Cabinet API

```python
from codex_django.messaging.cabinet import (
    MessagingBridge,
    MessagingActionResult,
    MailboxState,
    MailboxThreadState,
    MessageState,
    ReplyComposerState,
    CampaignListState,
    CampaignDetailState,
    CampaignComposerState,
    RecipientListState,
    DeliveryLogState,
    MessagingSettingsState,
    MessagingCabinetPresenter,
    MessagingCabinetWorkflowService,
    build_messaging_sidebar,
    build_messaging_topbar,
)
```

Legacy cabinet DTOs remain importable for compatibility:
`InboxMessageState`, `InboxPanelState`, `ComposeFieldState`,
`ComposeFormState`, `CampaignRecipientState`, and `RecipientPanelState`.

For full source-level docstrings, open [Messaging internals](internal/messaging.md).
