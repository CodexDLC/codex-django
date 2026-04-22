"""Redis manager for cached static-page SEO payloads."""

from typing import Any

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
        async with self.async_hash() as h:
            result = await h.get_all(self.make_key(f"static_page:{page_key}"))
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
        async with self.async_hash() as h:
            await h.set_fields(full_key, mapping)
        if timeout is not None:
            async with self.async_string() as s:
                await s.expire(full_key, timeout)

    async def ainvalidate_page(self, page_key: str) -> None:
        """Delete the cached SEO payload for a specific page.

        Args:
            page_key: Logical page identifier used by the SEO model.
        """
        if self._is_disabled():
            return
        async with self.async_string() as s:
            await s.delete(self.make_key(f"static_page:{page_key}"))

    def get_page(self, page_key: str) -> dict[str, str]:
        """Synchronously return cached SEO data for a page.

        Args:
            page_key: Logical page identifier used by the SEO model.

        Returns:
            A flat string mapping for the page, or an empty dictionary when
            no cache entry exists.
        """
        if self._is_disabled():
            return {}
        with self.sync_hash() as h:
            result = h.get_all(self.make_key(f"static_page:{page_key}"))
        return result or {}

    def set_page(self, page_key: str, mapping: dict[str, str], timeout: int | None = None) -> None:
        """Synchronously cache SEO data for a page.

        Args:
            page_key: Logical page identifier used by the SEO model.
            mapping: Flat string payload to cache.
            timeout: Optional TTL in seconds.
        """
        if self._is_disabled() or not mapping:
            return
        full_key = self.make_key(f"static_page:{page_key}")
        with self.sync_hash() as h:
            h.set_fields(full_key, mapping)
        if timeout is not None:
            with self.sync_string() as s:
                s.expire(full_key, timeout)

    def invalidate_page(self, page_key: str) -> None:
        """Synchronously invalidate SEO cache for a page.

        Args:
            page_key: Logical page identifier used by the SEO model.
        """
        if self._is_disabled():
            return
        with self.sync_string() as s:
            s.delete(self.make_key(f"static_page:{page_key}"))


def get_seo_redis_manager() -> SeoRedisManager:
    """Return an SEO Redis manager configured from Django settings.

    Returns:
        A ready-to-use :class:`SeoRedisManager` instance.
    """
    return SeoRedisManager()
