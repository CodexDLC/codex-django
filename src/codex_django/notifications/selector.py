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
    """Retrieve notification text blocks with cache and language awareness.

    The selector is model-agnostic: the concrete content model, cache adapter,
    and i18n adapter are injected by the project at construction time.

    Notes:
        Default cache TTL is one hour.
    """

    cache_timeout: int = 3600
    cache_key_prefix: str = ""

    def __init__(
        self,
        model: Any,
        cache_adapter: Any,
        i18n_adapter: Any,
    ) -> None:
        """Initialize the selector with project-specific dependencies.

        Args:
            model: Concrete content model class used for lookups.
            cache_adapter: Cache adapter implementing ``get`` and ``set``.
            i18n_adapter: Adapter exposing a ``translation_override`` context manager.
        """
        self._model = model
        self._cache = cache_adapter
        self._i18n = i18n_adapter

    def get(self, key: str, language: str = "de") -> str | None:
        """Return the notification text for a key in the requested language.

        Args:
            key: Logical content key stored in the backing model.
            language: Target Django language code used for translation override.

        Returns:
            The resolved text value, or ``None`` when no matching content block
            exists.
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
        """Invalidate a single cached notification content entry.

        Args:
            key: Logical content key stored in the backing model.
            language: Language code associated with the cached value.
        """
        self._cache.set(self._cache_key(key, language), "", timeout=0)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _cache_key(self, key: str, language: str) -> str:
        """Build the cache key used for one localized content entry."""
        return f"{key}:{language}"

    def _fetch_from_db(self, key: str, language: str) -> str | None:
        """Fetch a localized content value directly from the database."""
        try:
            with self._i18n.translation_override(language):
                obj = self._model.objects.get(key=key)
                return cast(str, obj.text)
        except self._model.DoesNotExist:
            log.warning("EmailContent key=%r language=%r not found in DB", key, language)
            return None
