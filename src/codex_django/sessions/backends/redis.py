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

from collections.abc import Awaitable, Callable
from typing import Any, cast

from django.conf import settings
from django.contrib.sessions.backends.base import CreateError, SessionBase, UpdateError

from codex_django.core.redis.managers.base import get_default_redis_manager

_DEFAULT_PREFIX = "session"


class SessionStore(SessionBase):
    """Session store that persists session payloads in Redis as strings.

    Instances are cheap and stateless with respect to Redis connections — the
    manager builds clients lazily.
    """

    def __init__(self, session_key: str | None = None) -> None:
        super().__init__(session_key)
        self._manager: Any = None

    # ---- infrastructure ---------------------------------------------------

    @property
    def redis_manager(self) -> Any:
        if self._manager is None:
            self._manager = get_default_redis_manager()
        return self._manager

    @staticmethod
    def _key_prefix() -> str:
        return str(getattr(settings, "CODEX_SESSION_KEY_PREFIX", _DEFAULT_PREFIX))

    def _key(self, session_key: str) -> str:
        # Build the namespaced key without an extra make_key call since
        # we prefix manually to match old behaviour, or use the manager's make_key
        # but old code used namespaced_key(self._key_prefix(), session_key)
        # We can just use the manager's make_key by passing prefix to manager
        # or doing it inline.
        parts = [getattr(settings, "PROJECT_NAME", ""), self._key_prefix(), session_key]
        return ":".join(p for p in parts if p)

    # ---- async core -------------------------------------------------------

    async def aexists(self, session_key: str) -> bool:
        async with self.redis_manager.async_string() as s:
            return bool(await s.exists(self._key(session_key)))

    async def acreate(self) -> None:
        aget_new_session_key = cast(Callable[[], Awaitable[str]], self._aget_new_session_key)  # type: ignore[attr-defined]
        while True:
            self._session_key = await aget_new_session_key()
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
        async with self.redis_manager.async_string() as s:
            raw = await s.get(self._key(key))
        if raw is None:
            return {}
        # SessionBase.decode returns {} for tampered/unreadable payloads.
        return dict(self.decode(raw))

    async def asave(self, must_create: bool = False) -> None:
        if self.session_key is None:
            await self.acreate()
            return

        aget_session = cast(Callable[[bool], Awaitable[dict[str, Any]]], self._aget_session)  # type: ignore[attr-defined]
        payload = self.encode(await aget_session(must_create))
        ttl = self.get_expiry_age()
        key = self._key(self.session_key)

        async with self.redis_manager.async_string() as s:
            if must_create:
                created = await s.client.set(key, payload, nx=True, ex=ttl)
                if not created:
                    raise CreateError
                return

            if not await s.exists(key):
                raise UpdateError
            await s.set(key, payload, ttl=ttl)

    async def adelete(self, session_key: str | None = None) -> None:
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        async with self.redis_manager.async_string() as s:
            await s.delete(self._key(session_key))

    # ---- sync wrappers ----------------------------------------------------

    def exists(self, session_key: str) -> bool:
        with self.redis_manager.sync_string() as s:
            return bool(s.exists(self._key(session_key)))

    def create(self) -> None:
        get_new_session_key = cast(Callable[[], str], self._get_new_session_key)  # type: ignore[attr-defined]
        while True:
            self._session_key = get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def load(self) -> dict[str, Any]:
        key = self.session_key
        if key is None:
            return {}
        with self.redis_manager.sync_string() as s:
            raw = s.get(self._key(key))
        if raw is None:
            return {}
        return dict(self.decode(raw))

    def save(self, must_create: bool = False) -> None:
        if self.session_key is None:
            self.create()
            return

        get_session = cast(Callable[[bool], dict[str, Any]], self._get_session)  # type: ignore[attr-defined]
        payload = self.encode(get_session(must_create))
        ttl = self.get_expiry_age()
        key = self._key(self.session_key)

        with self.redis_manager.sync_string() as s:
            if must_create:
                created = s.client.set(key, payload, nx=True, ex=ttl)
                if not created:
                    raise CreateError
                return

            if not s.exists(key):
                raise UpdateError
            s.set(key, payload, ttl=ttl)

    def delete(self, session_key: str | None = None) -> None:
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        with self.redis_manager.sync_string() as s:
            s.delete(self._key(session_key))

    # ---- misc -------------------------------------------------------------

    @classmethod
    def clear_expired(cls) -> None:
        """Redis expires keys on its own — nothing to sweep."""
        return None

    @classmethod
    async def aclear_expired(cls) -> None:
        return None
