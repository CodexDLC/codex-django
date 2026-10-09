"""Redis helpers for syncing email settings to worker-readable storage."""

from __future__ import annotations

from typing import Any

from codex_django.core.redis.managers.base import BaseDjangoRedisManager

from ..workers_contract import SETTINGS_HASH_KEY


class EmailSettingsRedisManager(BaseDjangoRedisManager):
    """Persist email settings into a dedicated Redis hash."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="", **kwargs)

    def sync(self, data: dict[str, str | None]) -> None:
        """Write the latest serialized email settings to Redis."""
        if self._is_disabled() or not data:
            return
        key = self.make_key(SETTINGS_HASH_KEY)
        with self.sync_hash() as redis_hash:
            redis_hash.set_fields(key, {name: value if value is not None else "" for name, value in data.items()})


def get_email_settings_manager() -> EmailSettingsRedisManager:
    """Return the default email settings Redis manager."""
    return EmailSettingsRedisManager()
