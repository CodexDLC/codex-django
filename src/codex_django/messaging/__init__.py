"""
codex_django.messaging
======================
Django-specific messaging infrastructure for Codex projects.
"""

from __future__ import annotations

from typing import Any

from .adapters.arq_client import DjangoArqClient
from .adapters.cache_adapter import DjangoCacheAdapter
from .adapters.direct_adapter import DjangoDirectAdapter
from .adapters.email_settings import EmailSettingsRedisManager, get_email_settings_manager
from .adapters.i18n_adapter import DjangoI18nAdapter
from .adapters.queue_adapter import DjangoQueueAdapter
from .audience import BaseAudienceBuilder, CampaignRecipientDraft
from .builder import MessagingPayloadBuilder
from .cabinet import (
    CampaignComposerState,
    CampaignDetailState,
    CampaignListState,
    CampaignRecipientState,
    CampaignRowState,
    CampaignStatusSummaryState,
    ComposeFieldState,
    ComposeFormState,
    DeliveryLogRowState,
    DeliveryLogState,
    InboxMessageState,
    InboxPanelState,
    MailboxActionState,
    MailboxDetailState,
    MailboxFolderState,
    MailboxState,
    MailboxThreadState,
    MessageState,
    MessagingActionResult,
    MessagingBridge,
    MessagingCabinetPresenter,
    MessagingCabinetWorkflowService,
    MessagingSettingsSection,
    MessagingSettingsState,
    RecipientListState,
    RecipientPanelState,
    RecipientRowState,
    ReplyComposerState,
    build_default_mailbox_folders,
    build_messaging_sidebar,
    build_messaging_topbar,
)
from .campaigns import CampaignBatch, CampaignDispatcherProtocol, CampaignService
from .contracts import (
    ContentSelectorProtocol,
    NotificationDispatchSpec,
    NotificationEventHandler,
    QueueAdapterProtocol,
)
from .registry import (
    MessagingEventRegistry,
    email_rendered,
    email_template,
    messaging_event_registry,
    notification_handler,
)
from .selector import BaseEmailContentSelector
from .service import BaseMessagingEngine
from .workers_contract import SETTINGS_HASH_KEY

__all__ = [
    "AbstractCampaign",
    "AbstractCampaignRecipient",
    "AbstractEmailLog",
    "AbstractEmailSettings",
    "AbstractMessage",
    "AbstractMessageReply",
    "AbstractSystemRecipient",
    "AbstractThread",
    "BaseAudienceBuilder",
    "BaseEmailContentMixin",
    "BaseEmailContentSelector",
    "BaseMessagingEngine",
    "CampaignBatch",
    "CampaignComposerState",
    "CampaignDetailState",
    "CampaignDispatcherProtocol",
    "CampaignListState",
    "CampaignRecipientDraft",
    "CampaignRecipientState",
    "CampaignRowState",
    "CampaignService",
    "CampaignStatusSummaryState",
    "ComposeFieldState",
    "ComposeFormState",
    "ContentSelectorProtocol",
    "DeliveryLogRowState",
    "DeliveryLogState",
    "DjangoArqClient",
    "DjangoCacheAdapter",
    "DjangoDirectAdapter",
    "DjangoI18nAdapter",
    "DjangoQueueAdapter",
    "EmailSettingsRedisManager",
    "EmailSettingsSyncMixin",
    "InboxMessageState",
    "InboxPanelState",
    "MailboxActionState",
    "MailboxDetailState",
    "MailboxFolderState",
    "MailboxState",
    "MailboxThreadState",
    "MessageState",
    "MessagingActionResult",
    "MessagingBridge",
    "MessagingCabinetPresenter",
    "MessagingCabinetWorkflowService",
    "MessagingEventRegistry",
    "MessagingPayloadBuilder",
    "MessagingSettingsSection",
    "MessagingSettingsState",
    "NotificationDispatchSpec",
    "NotificationEventHandler",
    "QueueAdapterProtocol",
    "RecipientListState",
    "RecipientPanelState",
    "RecipientRowState",
    "ReplyComposerState",
    "SETTINGS_HASH_KEY",
    "build_default_mailbox_folders",
    "build_messaging_sidebar",
    "build_messaging_topbar",
    "email_rendered",
    "email_template",
    "get_email_settings_manager",
    "messaging_event_registry",
    "notification_handler",
]

_LAZY_EXPORTS = {
    "AbstractCampaign": ("codex_django.messaging.mixins.models", "AbstractCampaign"),
    "AbstractCampaignRecipient": ("codex_django.messaging.mixins.models", "AbstractCampaignRecipient"),
    "AbstractEmailLog": ("codex_django.messaging.mixins.models", "AbstractEmailLog"),
    "AbstractEmailSettings": ("codex_django.messaging.mixins.models", "AbstractEmailSettings"),
    "AbstractMessage": ("codex_django.messaging.mixins.models", "AbstractMessage"),
    "AbstractMessageReply": ("codex_django.messaging.mixins.models", "AbstractMessageReply"),
    "AbstractSystemRecipient": ("codex_django.messaging.mixins.models", "AbstractSystemRecipient"),
    "AbstractThread": ("codex_django.messaging.mixins.models", "AbstractThread"),
    "BaseEmailContentMixin": ("codex_django.messaging.mixins.models", "BaseEmailContentMixin"),
    "EmailSettingsSyncMixin": ("codex_django.messaging.mixins.models", "EmailSettingsSyncMixin"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        from importlib import import_module

        module_name, attr_name = _LAZY_EXPORTS[name]
        value = getattr(import_module(module_name), attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'codex_django.messaging' has no attribute {name!r}")
