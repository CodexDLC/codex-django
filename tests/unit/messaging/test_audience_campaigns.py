from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from codex_django.messaging.audience import BaseAudienceBuilder, CampaignRecipientDraft
from codex_django.messaging.campaigns import CampaignBatch, CampaignService

pytestmark = pytest.mark.unit


class _FakeRecipient:
    def __init__(self, pk: int, email: str, locale: str = "de") -> None:
        self.pk = pk
        self.email = email
        self.locale = locale
        self.first_name = f"Name{pk}"
        self.last_name = f"Surname{pk}"


class _FakeQuerySet:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self

    def count(self):
        return len(self._items)

    def iterator(self, chunk_size: int):
        self.chunk_size = chunk_size
        yield from self._items


def test_base_audience_builder_uses_primary_setting_and_streams_drafts():
    model = MagicMock()
    model.objects = _FakeQuerySet([_FakeRecipient(1, "a@b.com"), _FakeRecipient(2, "b@b.com")])

    with (
        override_settings(MESSAGING_RECIPIENT_MODEL="tests.FakeRecipient"),
        patch("codex_django.messaging.audience.apps.get_model", return_value=model),
    ):
        builder = BaseAudienceBuilder()
        drafts = list(builder.materialize({"locale": "de"}))

    assert drafts == [
        CampaignRecipientDraft(
            recipient_id="1",
            email="a@b.com",
            first_name="Name1",
            last_name="Surname1",
            locale="de",
            unsubscribe_token=None,
        ),
        CampaignRecipientDraft(
            recipient_id="2",
            email="b@b.com",
            first_name="Name2",
            last_name="Surname2",
            locale="de",
            unsubscribe_token=None,
        ),
    ]
    assert builder.count({}) == 2


def test_base_audience_builder_falls_back_to_legacy_setting():
    model = MagicMock()
    model.objects = _FakeQuerySet([_FakeRecipient(1, "a@b.com")])

    with (
        override_settings(CONVERSATIONS_RECIPIENT_MODEL="tests.LegacyRecipient"),
        patch("codex_django.messaging.audience.apps.get_model", return_value=model) as mock_get_model,
    ):
        builder = BaseAudienceBuilder()
        list(builder.materialize({}))

    mock_get_model.assert_called_once_with("tests.LegacyRecipient")


def test_campaign_service_batches_and_dispatches_without_materializing_everything():
    class StubAudience:
        def count(self, audience_filter):
            return 3

        def materialize(self, audience_filter):
            yield CampaignRecipientDraft(recipient_id="1", email="a@b.com")
            yield CampaignRecipientDraft(recipient_id="2", email="b@b.com")
            yield CampaignRecipientDraft(recipient_id="3", email="c@b.com")

    dispatcher = MagicMock()
    dispatcher.enqueue_batch.side_effect = ["job-1", "job-2"]
    service = CampaignService(audience=StubAudience(), dispatcher=dispatcher, batch_size=2)

    batches = service.build_batches(campaign_id="cmp-1", subject="Hello", audience_filter={"active": True})
    job_ids = service.send(campaign_id="cmp-1", subject="Hello", audience_filter={"active": True})

    assert batches == [
        CampaignBatch(
            campaign_id="cmp-1",
            recipients=[
                CampaignRecipientDraft(recipient_id="1", email="a@b.com"),
                CampaignRecipientDraft(recipient_id="2", email="b@b.com"),
            ],
            subject="Hello",
            audience_filter={"active": True},
        ),
        CampaignBatch(
            campaign_id="cmp-1",
            recipients=[CampaignRecipientDraft(recipient_id="3", email="c@b.com")],
            subject="Hello",
            audience_filter={"active": True},
        ),
    ]
    assert job_ids == ["job-1", "job-2"]
    assert dispatcher.enqueue_batch.call_count == 2
