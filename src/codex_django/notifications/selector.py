"""
BaseEmailContentSelector
========================
Looks up notification content blocks from the DB with cache support.

Abstracts over the concrete EmailContent model — the model is injected
at construction time so the selector stays reusable across projects.

Usage::

    from codex_django.notifications import (
        BaseEmailContentSelector,
        DjangoCacheAdapter,
        DjangoI18nAdapter,
    )
    from myapp.models import EmailContent

    selector = BaseEmailContentSelector(
        model=EmailContent,
        cache_adapter=DjangoCacheAdapter(),
        i18n_adapter=DjangoI18nAdapter(),
    )

    subject = selector.get("booking_subject", language="de")
"""

from __future__ import annotations

import logging
from typing import Any, cast

log = logging.getLogger(__name__)


class BaseEmailContentSelector:
    """
    Retrieves email content text by key with i18n and cache support.

    Cache key format: ``notification_content:{language}:{key}``
    Default TTL: 3600 seconds (1 hour).
    """

    cache_timeout: int = 3600
    cache_key_prefix: str = ""

    def __init__(
        self,
        model: Any,
        cache_adapter: Any,
        i18n_adapter: Any,
    ) -> None:
        self._model = model
        self._cache = cache_adapter
        self._i18n = i18n_adapter

    def get(self, key: str, language: str = "de") -> str | None:
        """
        Return the text for *key* in *language*.

        1. Check cache → return on hit.
        2. Query DB inside translation_override(language).
        3. Store in cache and return.
        Returns None if no record found.
        """
        cache_key = self._cache_key(key, language)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cast(str | None, cached)

        value = self._fetch_from_db(key, language)
        if value is not None:
            self._cache.set(cache_key, value, self.cache_timeout)

        return value

    def invalidate(self, key: str, language: str) -> None:
        """Remove a single cached entry."""
        self._cache.set(self._cache_key(key, language), "", timeout=0)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _cache_key(self, key: str, language: str) -> str:
        return f"{key}:{language}"

    def _fetch_from_db(self, key: str, language: str) -> str | None:
        try:
            with self._i18n.translation_override(language):
                obj = self._model.objects.get(key=key)
                return cast(str, obj.text)
        except self._model.DoesNotExist:
            log.warning("EmailContent key=%r language=%r not found in DB", key, language)
            return None
