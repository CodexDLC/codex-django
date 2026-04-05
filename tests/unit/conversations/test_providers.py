import pytest

from codex_django.conversations.cabinet.providers import build_inbox_notification_item


@pytest.mark.unit
def test_build_inbox_notification_item_returns_none_if_count_zero():
    assert build_inbox_notification_item(count=0, url="/inbox/") is None


@pytest.mark.unit
def test_build_inbox_notification_item_returns_dict_if_count_positive():
    result = build_inbox_notification_item(count=5, url="/inbox/")
    assert result is not None
    assert result["count"] == 5
    assert result["url"] == "/inbox/"
    assert "New messages" in result["label"]
    assert result["icon"] == "bi-envelope"


@pytest.mark.unit
def test_build_inbox_notification_item_custom_label_and_icon():
    result = build_inbox_notification_item(count=1, url="/chat/", label="Chat", icon="bi-chat")
    assert result["label"] == "Chat"
    assert result["icon"] == "bi-chat"
