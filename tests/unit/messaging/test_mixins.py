from unittest.mock import MagicMock, patch

import pytest
from django.db import connection
from django.test import override_settings

from codex_django.messaging.mixins.models import (
    AbstractCampaign,
    AbstractCampaignRecipient,
    AbstractEmailLog,
    AbstractEmailSettings,
    AbstractMessage,
    AbstractMessageReply,
    AbstractSystemRecipient,
    AbstractThread,
    EmailSettingsSyncMixin,
)

pytestmark = pytest.mark.unit


class ConcreteEmailSettings(AbstractEmailSettings):
    class Meta:
        app_label = "tests"


class ConcreteEmailSettingsSync(AbstractEmailSettings, EmailSettingsSyncMixin):
    class Meta:
        app_label = "tests"


@pytest.mark.django_db(transaction=True)
def test_abstract_email_settings_load_creates_and_returns_singleton():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(ConcreteEmailSettings)
    try:
        first = ConcreteEmailSettings.load()
        second = ConcreteEmailSettings.load()

        assert first.pk == 1
        assert second.pk == 1
        assert ConcreteEmailSettings.objects.count() == 1
    finally:
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(ConcreteEmailSettings)


def test_email_settings_sync_calls_redis_manager_with_serialized_payload():
    instance = ConcreteEmailSettingsSync(
        email_from="team@example.com",
        email_sender_name="Team",
        email_reply_to="reply@example.com",
        site_base_url="https://example.com",
        logo_url="/logo.png",
    )
    manager = MagicMock()

    with (
        override_settings(DEBUG=False),
        patch("codex_django.messaging.mixins.models.get_email_settings_manager", return_value=manager),
    ):
        instance.sync_email_settings_to_redis()

    payload = manager.sync.call_args.args[0]
    assert payload["email_from"] == "team@example.com"
    assert payload["email_sender_name"] == "Team"
    assert payload["site_base_url"] == "https://example.com"


def test_email_settings_sync_skips_when_debug_redis_disabled():
    instance = ConcreteEmailSettingsSync()
    manager = MagicMock()

    with (
        override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False),
        patch("codex_django.messaging.mixins.models.get_email_settings_manager", return_value=manager),
    ):
        instance.sync_email_settings_to_redis()

    manager.sync.assert_not_called()


def test_all_new_mixins_remain_abstract():
    classes = [
        AbstractSystemRecipient,
        AbstractEmailLog,
        AbstractThread,
        AbstractMessage,
        AbstractMessageReply,
        AbstractCampaign,
        AbstractCampaignRecipient,
    ]
    assert all(cls._meta.abstract for cls in classes)
