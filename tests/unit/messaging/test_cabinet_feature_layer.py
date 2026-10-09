from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from django.template.loader import render_to_string

from codex_django.messaging import (
    CampaignListState,
    CampaignRowState,
    CampaignStatusSummaryState,
    DeliveryLogRowState,
    DeliveryLogState,
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
    RecipientRowState,
    ReplyComposerState,
    build_messaging_sidebar,
    build_messaging_topbar,
)
from codex_django.messaging.cabinet import (
    CampaignRecipientState,
    ComposeFieldState,
    ComposeFormState,
    InboxMessageState,
    InboxPanelState,
    RecipientPanelState,
)

pytestmark = pytest.mark.unit


def test_new_public_imports_and_dataclass_defaults():
    mailbox = MailboxState()
    settings = MessagingSettingsState(sections=[MessagingSettingsSection(key="identity", title="Identity")])
    topbar = build_messaging_topbar("/cabinet/messaging/")

    assert mailbox.title == "Mailbox"
    assert mailbox.active_folder == "inbox"
    assert settings.submit_label == "Save settings"
    assert topbar.label == "Messaging"


def test_legacy_cabinet_imports_remain_available():
    inbox = InboxPanelState(threads=[InboxMessageState(thread_id="1", subject="Hello", preview="Body")])
    compose = ComposeFormState(fields=[ComposeFieldState(name="subject", label="Subject")])
    recipients = RecipientPanelState(recipients=[CampaignRecipientState(recipient_id="1", email="a@example.com")])

    assert inbox.threads[0].thread_id == "1"
    assert compose.fields[0].name == "subject"
    assert recipients.total_count == 0


def test_messaging_bridge_protocol_is_importable():
    class StubBridge:
        def get_mailbox_state(self, **kwargs: Any) -> MailboxState:
            return MailboxState()

    bridge: MessagingBridge = StubBridge()  # type: ignore[assignment]
    assert isinstance(bridge.get_mailbox_state(user=object()), MailboxState)


def test_build_messaging_sidebar_order_badges_and_no_settings_item():
    sidebar = build_messaging_sidebar(
        mailbox_url="/mailbox/",
        campaigns_url="/campaigns/",
        recipients_url="/recipients/",
        delivery_log_url="/delivery-log/",
        unread_badge_key="custom_unread",
    )

    assert [item.label for item in sidebar] == ["Mailbox", "Campaigns", "Recipients", "Delivery log"]
    assert [item.icon for item in sidebar] == ["bi-inbox", "bi-megaphone", "bi-people", "bi-list-check"]
    assert sidebar[0].badge_key == "custom_unread"
    assert all(item.badge_key == "" for item in sidebar[1:])
    assert "Settings" not in [str(item.label) for item in sidebar]


def test_presenter_mailbox_context_preserves_state_and_builds_split_panel():
    thread = MailboxThreadState(
        id="t1",
        url="/thread/t1/",
        subject="Question",
        preview="Can you help?",
        sender_label="Ada",
        received_at="10:00",
        unread=True,
    )
    state = MailboxState(
        folders=[MailboxFolderState(key="inbox", label="Inbox", url="/mailbox/", active=True)],
        threads=[thread],
        selected=MailboxDetailState(
            thread=thread,
            messages=[MessageState(id="m1", direction="inbound", sender_label="Ada", body="Hi")],
        ),
    )

    context = MessagingCabinetPresenter().mailbox_context(state)

    assert context["mailbox"] is state
    assert context["mailbox_panel"].items[0].id == "t1"
    assert context["mailbox_panel"].active_id == "t1"
    assert context["unread_messages_count"] == 1


def test_presenter_table_mappings_for_campaigns_recipients_and_delivery():
    presenter = MessagingCabinetPresenter()

    campaign_context = presenter.campaign_list_context(
        CampaignListState(
            status_filters=[CampaignStatusSummaryState(key="draft", label="Drafts")],
            rows=[CampaignRowState(id="c1", url="/c1/", subject="Sale", status="draft", recipient_count=5)],
        )
    )
    recipient_context = presenter.recipient_list_context(
        RecipientListState(rows=[RecipientRowState(id="r1", email="a@example.com", name="Ada", enabled=False)])
    )
    delivery_context = presenter.delivery_log_context(
        DeliveryLogState(rows=[DeliveryLogRowState(id="d1", recipient="a@example.com", status="sent", subject="Sale")])
    )

    assert campaign_context["campaigns_table"].rows[0]["subject"] == "Sale"
    assert campaign_context["campaigns_table"].filters[0].label == "Drafts"
    assert recipient_context["recipients_table"].rows[0]["enabled_label"] == "Disabled"
    assert delivery_context["delivery_log_table"].rows[0]["status"] == "sent"


class WorkflowBridge:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []

    def reply_to_thread(self, *, user: Any, thread_id: str, body: str) -> MessagingActionResult:
        self.calls.append(("reply", body))
        return MessagingActionResult(ok=True, code="replied", message="Sent", target_url=f"/thread/{thread_id}/")

    def mark_thread_read(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="read", message="Read")

    def mark_thread_processed(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="processed", message="Processed")

    def mark_thread_spam(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="spam", message="Spam")

    def archive_thread(self, *, user: Any, thread_id: str) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="archived", message="Archived")

    def create_campaign(self, *, user: Any, payload: Mapping[str, Any]) -> MessagingActionResult:
        self.calls.append(("create_campaign", payload["subject"]))
        return MessagingActionResult(ok=True, code="created", message="Created")

    def update_campaign(self, *, user: Any, campaign_id: str, payload: Mapping[str, Any]) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="updated", message=campaign_id)

    def send_campaign(self, *, user: Any, campaign_id: str) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="sent", message=campaign_id)

    def send_test_campaign(self, *, user: Any, campaign_id: str, email: str) -> MessagingActionResult:
        self.calls.append(("send_test", email))
        return MessagingActionResult(ok=True, code="test_sent", message=email)

    def update_recipient(self, *, user: Any, recipient_id: str, payload: Mapping[str, Any]) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="recipient_updated", message=recipient_id)

    def update_settings(self, *, user: Any, payload: Mapping[str, Any]) -> MessagingActionResult:
        return MessagingActionResult(ok=True, code="settings_updated", message="Saved")


def test_workflow_success_and_validation_results():
    bridge = WorkflowBridge()
    workflow = MessagingCabinetWorkflowService(bridge)  # type: ignore[arg-type]

    result = workflow.reply(user=object(), thread_id="t1", payload={"body": " Hello "})
    invalid = workflow.reply(user=object(), thread_id="t1", payload={"body": " "})
    campaign = workflow.save_campaign(user=object(), payload={"subject": "Sale", "body_text": "Body"})
    test_send = workflow.send_test_campaign(user=object(), campaign_id="c1", payload={"email": "team@example.com"})
    unknown = workflow.dispatch("missing", user=object())

    assert result.ok is True
    assert bridge.calls[0] == ("reply", "Hello")
    assert invalid.field_errors == {"body": ["Reply body is required."]}
    assert campaign.code == "created"
    assert test_send.code == "test_sent"
    assert unknown.code == "unknown_action"


def test_workflow_dispatch_routes_each_supported_action():
    bridge = WorkflowBridge()
    workflow = MessagingCabinetWorkflowService(bridge)  # type: ignore[arg-type]
    user = object()

    expected = {
        "reply": "replied",
        "mark_read": "read",
        "mark_processed": "processed",
        "mark_spam": "spam",
        "archive": "archived",
        "save_campaign": "updated",
        "send_campaign": "sent",
        "send_test_campaign": "test_sent",
        "save_recipient": "recipient_updated",
        "save_settings": "settings_updated",
    }
    for action, code in expected.items():
        result = workflow.dispatch(
            action,
            user=user,
            payload={"body": "Hello", "subject": "Sale", "body_text": "Body", "email": "a@example.com"},
            thread_id="t1",
            campaign_id="c1",
            recipient_id="r1",
        )
        assert result.code == code
        assert result.ok


def test_workflow_validates_campaign_recipient_and_settings_before_bridge_writes():
    bridge = WorkflowBridge()
    workflow = MessagingCabinetWorkflowService(bridge)  # type: ignore[arg-type]
    user = object()

    campaign = workflow.save_campaign(user=user, payload={"subject": " ", "body_text": " "})
    recipient = workflow.save_recipient(user=user, recipient_id="r1", payload={"email": "invalid"})
    settings = workflow.save_settings(user=user, payload={})
    test_send = workflow.send_test_campaign(user=user, campaign_id="c1", payload={"email": "invalid"})

    assert campaign.field_errors == {"subject": ["Subject is required."], "body_text": ["Message body is required."]}
    assert recipient.field_errors == {"email": ["Enter an email."]}
    assert settings.field_errors == {"__all__": ["No settings provided."]}
    assert test_send.field_errors == {"email": ["Enter an email."]}
    assert bridge.calls == []


def test_template_rendering_for_messaging_components():
    presenter = MessagingCabinetPresenter()
    thread = MailboxThreadState(id="t1", url="/thread/t1/", subject="Hello", preview="Preview", sender_label="Ada")
    mailbox_context = presenter.mailbox_context(
        MailboxState(
            folders=[MailboxFolderState(key="inbox", label="Inbox", url="/mailbox/", active=True)],
            threads=[thread],
            selected=MailboxDetailState(
                thread=thread,
                messages=[MessageState(id="m1", direction="inbound", sender_label="Ada", body="Message body")],
                composer=ReplyComposerState(action_url="/reply/"),
            ),
        )
    )
    empty_mailbox = presenter.mailbox_context(MailboxState(empty_title="Empty", empty_message="No mail"))
    campaign_context = presenter.campaign_list_context(
        CampaignListState(rows=[CampaignRowState(id="c1", url="/c1/", subject="Campaign")])
    )
    recipient_context = presenter.recipient_list_context(
        RecipientListState(rows=[RecipientRowState(id="r1", email="a@example.com")])
    )
    delivery_context = presenter.delivery_log_context(
        DeliveryLogState(rows=[DeliveryLogRowState(id="d1", recipient="a@example.com", status="sent")])
    )

    assert "Message body" in render_to_string("cabinet/messaging/components/mailbox_shell.html", mailbox_context)
    assert "No mail" in render_to_string("cabinet/messaging/components/mailbox_shell.html", empty_mailbox)
    assert "Campaign" in render_to_string("cabinet/messaging/components/campaign_table.html", campaign_context)
    assert "a@example.com" in render_to_string("cabinet/messaging/components/recipient_table.html", recipient_context)
    assert "sent" in render_to_string("cabinet/messaging/components/delivery_log_table.html", delivery_context)
