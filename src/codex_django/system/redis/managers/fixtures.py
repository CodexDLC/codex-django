from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class FixtureHashManager(BaseDjangoRedisManager):
    """Stores a hash of the current fixtures to avoid re-loading identical fixtures."""

    async def aget_hash(self, fixture_key: str) -> str | None:
        if self._is_disabled():
            return None
        return await self.string.get(self.make_key(f"fixture:{fixture_key}"))  # type: ignore[no-any-return]

    async def aset_hash(self, fixture_key: str, hash_string: str) -> None:
        if self._is_disabled():
            return
        await self.string.set(self.make_key(f"fixture:{fixture_key}"), hash_string)

    def get_hash(self, fixture_key: str) -> str | None:
        return async_to_sync(self.aget_hash)(fixture_key)

    def set_hash(self, fixture_key: str, hash_string: str) -> None:
        async_to_sync(self.aset_hash)(fixture_key, hash_string)


def get_fixture_hash_manager() -> FixtureHashManager:
    return FixtureHashManager()
