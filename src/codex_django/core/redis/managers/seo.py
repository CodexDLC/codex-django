from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class SeoRedisManager(BaseDjangoRedisManager):
    """Manager for static page SEO cache."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="seo", **kwargs)

    async def aget_page(self, page_key: str) -> dict[str, str]:
        """Возвращает кэшированные SEO-данные как словарь."""
        if self._is_disabled():
            return {}
        result = await self.hash.get_all(self.make_key(f"static_page:{page_key}"))
        return result or {}

    async def aset_page(self, page_key: str, mapping: dict[str, str], timeout: int | None = None) -> None:
        """Сохраняет SEO-данные (словарь) в Redis Hash."""
        if self._is_disabled() or not mapping:
            return
        full_key = self.make_key(f"static_page:{page_key}")
        await self.hash.set_fields(full_key, mapping)
        if timeout is not None:
            await self.string.expire(full_key, timeout)

    async def ainvalidate_page(self, page_key: str) -> None:
        """Удаляет кэш SEO для конкретной страницы."""
        if self._is_disabled():
            return
        await self.string.delete(self.make_key(f"static_page:{page_key}"))

    def get_page(self, page_key: str) -> dict[str, str]:
        return async_to_sync(self.aget_page)(page_key)

    def set_page(self, page_key: str, mapping: dict[str, str], timeout: int | None = None) -> None:
        async_to_sync(self.aset_page)(page_key, mapping, timeout)

    def invalidate_page(self, page_key: str) -> None:
        async_to_sync(self.ainvalidate_page)(page_key)


def get_seo_redis_manager() -> SeoRedisManager:
    return SeoRedisManager()
