"""Redis-backed helpers for fixture hash tracking."""

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class FixtureHashManager(BaseDjangoRedisManager):
    """Store fixture content hashes to skip redundant import operations.

    Notes:
        Each logical fixture group is stored under a ``fixture:<key>`` Redis
        string so import commands can quickly decide whether work is needed.
    """

    async def aget_hash(self, fixture_key: str) -> str | None:
        """Return the stored hash for a logical fixture group, if any.

        Args:
            fixture_key: Logical identifier for the fixture bundle.

        Returns:
            The stored hash string or ``None`` when no value exists.
        """
        if self._is_disabled():
            return None
        return await self.string.get(self.make_key(f"fixture:{fixture_key}"))  # type: ignore[no-any-return]

    async def aset_hash(self, fixture_key: str, hash_string: str) -> None:
        """Persist the latest hash for a logical fixture group.

        Args:
            fixture_key: Logical identifier for the fixture bundle.
            hash_string: Newly computed content hash to store.
        """
        if self._is_disabled():
            return
        await self.string.set(self.make_key(f"fixture:{fixture_key}"), hash_string)

    def get_hash(self, fixture_key: str) -> str | None:
        """Synchronously return the stored hash for a fixture bundle.

        Args:
            fixture_key: Logical identifier for the fixture bundle.

        Returns:
            The stored hash string or ``None`` when no value exists.
        """
        return async_to_sync(self.aget_hash)(fixture_key)

    def set_hash(self, fixture_key: str, hash_string: str) -> None:
        """Synchronously persist a fixture hash value.

        Args:
            fixture_key: Logical identifier for the fixture bundle.
            hash_string: Newly computed content hash to store.
        """
        async_to_sync(self.aset_hash)(fixture_key, hash_string)


def get_fixture_hash_manager() -> FixtureHashManager:
    """Return a fixture hash manager configured from Django settings.

    Returns:
        A ready-to-use :class:`FixtureHashManager` instance.
    """
    return FixtureHashManager()
