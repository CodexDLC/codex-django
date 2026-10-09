"""Reusable cabinet feature layer for ``codex_django.messaging``.

Compatibility note:
    The old single-file ``codex_django.messaging.cabinet`` module exposed a
    small set of inbox/compose DTOs. Those names remain importable here while
    new projects should prefer the mailbox, campaign, recipient, delivery, and
    settings contracts exported by this package.
"""

from .bridge import MessagingActionResult, MessagingBridge
from .navigation import build_messaging_sidebar, build_messaging_topbar
from .presenters import MessagingCabinetPresenter
from .types import (
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
    MessagingSettingsSection,
    MessagingSettingsState,
    RecipientListState,
    RecipientPanelState,
    RecipientRowState,
    ReplyComposerState,
    build_default_mailbox_folders,
)
from .workflows import MessagingCabinetWorkflowService

__all__ = [
    "CampaignComposerState",
    "CampaignDetailState",
    "CampaignListState",
    "CampaignRecipientState",
    "CampaignRowState",
    "CampaignStatusSummaryState",
    "ComposeFieldState",
    "ComposeFormState",
    "DeliveryLogRowState",
    "DeliveryLogState",
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
    "MessagingSettingsSection",
    "MessagingSettingsState",
    "RecipientListState",
    "RecipientPanelState",
    "RecipientRowState",
    "ReplyComposerState",
    "build_default_mailbox_folders",
    "build_messaging_sidebar",
    "build_messaging_topbar",
]
