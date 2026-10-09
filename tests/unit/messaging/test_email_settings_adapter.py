"""Contract checks for the worker-readable email settings hash."""

import pytest
from django.test import override_settings

from codex_django.messaging.adapters.email_settings import EmailSettingsRedisManager

pytestmark = pytest.mark.unit


class RecordingRedisClient:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict[str, str]]] = []
        self.closed = False

    def hset(self, key: str, *, mapping: dict[str, str]) -> None:
        self.writes.append((key, mapping))

    def close(self) -> None:
        self.closed = True


def test_email_settings_sync_uses_real_hash_operations_contract() -> None:
    client = RecordingRedisClient()
    with override_settings(DEBUG=False, PROJECT_NAME="example"):
        manager = EmailSettingsRedisManager(sync_client_factory=lambda: client)
        manager.sync({"email_from": "team@example.com", "email_reply_to": None})

    assert client.writes == [("example:email_settings", {"email_from": "team@example.com", "email_reply_to": ""})]
    assert client.closed


@pytest.mark.parametrize("data", [{}, {"email_from": "team@example.com"}])
def test_email_settings_sync_does_not_open_redis_when_disabled_or_empty(data: dict[str, str]) -> None:
    calls = 0

    def make_client() -> RecordingRedisClient:
        nonlocal calls
        calls += 1
        return RecordingRedisClient()

    with override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False):
        EmailSettingsRedisManager(sync_client_factory=make_client).sync(data)
    assert calls == 0
