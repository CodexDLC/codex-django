"""Redis-backed ``SessionBase`` implementation.

Wire this up as ``SESSION_ENGINE = "codex_django.sessions.backends.redis"``.

Storage contract:

* Session payload is stored as the Django encoded string produced by
  :py:meth:`SessionBase.encode`. No pickle is used — the project must rely on
  a JSON-based ``SESSION_SERIALIZER`` (Django's default
  ``django.contrib.sessions.serializers.JSONSerializer`` is fine).
* Redis key format: ``{PROJECT_NAME}:{CODEX_SESSION_KEY_PREFIX}:{session_key}``.
* TTL equals ``self.get_expiry_age()`` (driven by ``SESSION_COOKIE_AGE`` /
  per-session overrides).
* Redis failures propagate as
  :py:class:`codex_platform.redis_service.exceptions.RedisConnectionError`
  (or ``RedisServiceError``). They are **not** swallowed — a broken Redis must
  never look like a valid empty session.

Legacy ``django-redis`` / pickled sessions are **not** readable by this backend
and do not need to be migrated — old keys are simply ignored and the user
re-authenticates.
"""

from __future__ import annotations

from typing import Any

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.sessions.backends.base import CreateError, SessionBase, UpdateError

from codex_django.core.redis.django_adapter import build_redis_service, namespaced_key

_DEFAULT_PREFIX = "session"


class SessionStore(SessionBase):
    """Session store that persists session payloads in Redis as strings.

    Instances are cheap and stateless with respect to Redis connections — the
    :class:`~codex_platform.redis_service.RedisService` is built lazily on
    first use and reused for the lifetime of the store.
    """

    def __init__(self, session_key: str | None = None) -> None:
        super().__init__(session_key)
        self._service: Any = None

    # ---- infrastructure ---------------------------------------------------

    @property
    def _redis(self) -> Any:
        """Lazily build and memoize the per-instance ``RedisService``."""
        if self._service is None:
            self._service = build_redis_service()
        return self._service

    @staticmethod
    def _key_prefix() -> str:
        return str(getattr(settings, "CODEX_SESSION_KEY_PREFIX", _DEFAULT_PREFIX))

    def _key(self, session_key: str) -> str:
        return namespaced_key(self._key_prefix(), session_key)

    # ---- async core -------------------------------------------------------

    async def aexists(self, session_key: str) -> bool:
        return bool(await self._redis.string.exists(self._key(session_key)))

    async def acreate(self) -> None:
        while True:
            self._session_key = await self._aget_new_session_key()  # type: ignore[attr-defined]
            try:
                await self.asave(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    async def aload(self) -> dict[str, Any]:
        key = self.session_key
        if key is None:
            return {}
        raw = await self._redis.string.get(self._key(key))
        if raw is None:
            return {}
        # SessionBase.decode returns {} for tampered/unreadable payloads.
        return dict(self.decode(raw))

    async def asave(self, must_create: bool = False) -> None:
        if self.session_key is None:
            await self.acreate()
            return

        payload = self.encode(await self._aget_session(no_load=must_create))  # type: ignore[attr-defined]
        ttl = self.get_expiry_age()
        key = self._key(self.session_key)

        if must_create:
            created = await self._redis.string.setnx(key, payload, ttl=ttl)
            if not created:
                raise CreateError
            return

        if not await self._redis.string.exists(key):
            raise UpdateError
        await self._redis.string.set(key, payload, ttl=ttl)

    async def adelete(self, session_key: str | None = None) -> None:
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        await self._redis.string.delete(self._key(session_key))

    # ---- sync wrappers ----------------------------------------------------

    def exists(self, session_key: str) -> bool:
        return bool(async_to_sync(self.aexists)(session_key))

    def create(self) -> None:
        async_to_sync(self.acreate)()

    def load(self) -> dict[str, Any]:
        return async_to_sync(self.aload)()

    def save(self, must_create: bool = False) -> None:
        async_to_sync(self.asave)(must_create)

    def delete(self, session_key: str | None = None) -> None:
        async_to_sync(self.adelete)(session_key)

    # ---- misc -------------------------------------------------------------

    @classmethod
    def clear_expired(cls) -> None:
        """Redis expires keys on its own — nothing to sweep."""
        return None

    @classmethod
    async def aclear_expired(cls) -> None:
        return None
