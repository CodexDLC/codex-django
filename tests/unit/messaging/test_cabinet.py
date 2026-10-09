import pytest

from codex_django.messaging.cabinet import (
    CampaignComposerState,
    CampaignRecipientState,
    ComposeFieldState,
    ComposeFormState,
    InboxMessageState,
    InboxPanelState,
    MessagingBridge,
    MessagingSettingsSection,
    MessagingSettingsState,
    RecipientPanelState,
)

pytestmark = pytest.mark.unit


def test_messaging_cabinet_state_dataclasses_roundtrip():
    state = InboxPanelState(
        threads=[InboxMessageState(thread_id="42", subject="Hello", preview="Preview")],
        unread_count=1,
        filters={"status": "open"},
    )
    compose = ComposeFormState(fields=[ComposeFieldState(name="subject", label="Subject")])
    settings_state = MessagingSettingsState(
        sections=[MessagingSettingsSection(key="identity", title="Identity", fields=["email_from"])],
        values={"email_from": "team@example.com"},
    )
    campaign = CampaignComposerState(
        campaign_id="cmp-1",
        recipients=[CampaignRecipientState(recipient_id="1", email="a@b.com")],
    )
    recipients = RecipientPanelState(recipients=campaign.recipients, total_count=1)

    assert state.threads[0].thread_id == "42"
    assert compose.fields[0].name == "subject"
    assert settings_state.sections[0].key == "identity"
    assert campaign.recipients[0].email == "a@b.com"
    assert recipients.total_count == 1


def test_messaging_bridge_protocol_is_implementable():
    class StubBridge:
        def get_inbox_state(self, *, user, filters=None):
            return InboxPanelState()

        def get_compose_form_state(self, *, user):
            return ComposeFormState()

        def get_settings_state(self):
            return MessagingSettingsState()

        def get_campaign_state(self, *, campaign_id: str):
            return CampaignComposerState(campaign_id=campaign_id)

        def get_recipient_state(self, *, filters=None):
            return RecipientPanelState()

    bridge: MessagingBridge = StubBridge()
    assert isinstance(bridge.get_inbox_state(user=object()), InboxPanelState)
