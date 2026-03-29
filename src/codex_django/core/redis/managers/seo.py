"""Redis manager for cached static-page SEO payloads."""

from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class SeoRedisManager(BaseDjangoRedisManager):
    """Manage cached SEO payloads for static pages.

    Notes:
        SEO data is stored as a Redis hash per page key so templates and
        selectors can read the payload without repeated database hits.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="seo", **kwargs)

    async def aget_page(self, page_key: str) -> dict[str, str]:
        """Return cached SEO data for a page as a flat string mapping.

        Args:
            page_key: Logical page identifier used by the SEO model.

        Returns:
            A flat string mapping for the page, or an empty dictionary when
            no cache entry exists.
        """
        if self._is_disabled():
            return {}
        result = await self.hash.get_all(self.make_key(f"static_page:{page_key}"))
        return result or {}

    async def aset_page(self, page_key: str, mapping: dict[str, str], timeout: int | None = None) -> None:
        """Store SEO data for a page in a Redis hash.

        Args:
            page_key: Logical page identifier used by the SEO model.
            mapping: Flat string payload to cache.
            timeout: Optional TTL in seconds.
        """
        if self._is_disabled() or not mapping:
            return
        full_key = self.make_key(f"static_page:{page_key}")
        await self.hash.set_fields(full_key, mapping)
        if timeout is not None:
            await self.string.expire(full_key, timeout)

    async def ainvalidate_page(self, page_key: str) -> None:
        """Delete the cached SEO payload for a specific page.

        Args:
            page_key: Logical page identifier used by the SEO model.
        """
        if self._is_disabled():
            return
        await self.string.delete(self.make_key(f"static_page:{page_key}"))

    def get_page(self, page_key: str) -> dict[str, str]:
        """Synchronously return cached SEO data for a page.

        Args:
            page_key: Logical page identifier used by the SEO model.

        Returns:
            A flat string mapping for the page, or an empty dictionary when
            no cache entry exists.
        """
        return async_to_sync(self.aget_page)(page_key)

    def set_page(self, page_key: str, mapping: dict[str, str], timeout: int | None = None) -> None:
        """Synchronously cache SEO data for a page.

        Args:
            page_key: Logical page identifier used by the SEO model.
            mapping: Flat string payload to cache.
            timeout: Optional TTL in seconds.
        """
        async_to_sync(self.aset_page)(page_key, mapping, timeout)

    def invalidate_page(self, page_key: str) -> None:
        """Synchronously invalidate SEO cache for a page.

        Args:
            page_key: Logical page identifier used by the SEO model.
        """
        async_to_sync(self.ainvalidate_page)(page_key)


def get_seo_redis_manager() -> SeoRedisManager:
    """Return an SEO Redis manager configured from Django settings.

    Returns:
        A ready-to-use :class:`SeoRedisManager` instance.
    """
    return SeoRedisManager()
