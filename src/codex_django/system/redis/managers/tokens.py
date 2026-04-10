"""Redis-backed JSON action token helpers."""

import json
import secrets
from collections.abc import Mapping
from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class JsonActionTokenRedisManager(BaseDjangoRedisManager):
    """Store temporary JSON payloads behind secure action tokens.

    Projects can subclass this manager to type or validate their own payload
    shapes while reusing token generation, Redis keying, TTL, decode, and
    cleanup behavior.
    """

    default_ttl_seconds = 24 * 60 * 60
    token_bytes = 32

    def __init__(self, prefix: str = "auth:action", **kwargs: Any) -> None:
        """Initialize the token manager.

        Args:
            prefix: Redis key prefix used for stored token payloads.
            **kwargs: Additional keyword arguments forwarded to
                ``BaseDjangoRedisManager``.
        """
        super().__init__(prefix=prefix, **kwargs)

    def make_token(self) -> str:
        """Return a random URL-safe token string."""
        return secrets.token_urlsafe(self.token_bytes)

    def validate_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Return a JSON-serializable payload mapping.

        Subclasses may override this to enforce project-specific schemas.
        """
        return dict(payload)

    async def acreate_token(
        self,
        payload: Mapping[str, Any],
        *,
        ttl_seconds: int | None = None,
        ttl_hours: int | None = None,
    ) -> str:
        """Create a token and store its payload with a TTL.

        Args:
            payload: Mapping to serialize and store behind the generated token.
            ttl_seconds: Optional TTL override in seconds.
            ttl_hours: Optional TTL override in hours. Used only when
                ``ttl_seconds`` is not provided.

        Returns:
            The generated URL-safe action token.
        """
        token = self.make_token()
        if self._is_disabled():
            return token

        timeout = ttl_seconds
        if timeout is None and ttl_hours is not None:
            timeout = ttl_hours * 60 * 60
        if timeout is None:
            timeout = self.default_ttl_seconds

        await self.string.set(self.make_key(token), json.dumps(self.validate_payload(payload)), ttl=timeout)
        return token

    async def aget_token_data(self, token: str) -> dict[str, Any] | None:
        """Return decoded token payload data when present and valid.

        Args:
            token: Action token previously returned by ``acreate_token()`` or
                ``create_token()``.

        Returns:
            The decoded JSON payload mapping, or ``None`` when the token is
            missing, expired, disabled, or contains invalid JSON data.
        """
        if self._is_disabled():
            return None
        raw_data = await self.string.get(self.make_key(token))
        if not raw_data:
            return None
        try:
            data = json.loads(raw_data)
        except (json.JSONDecodeError, TypeError):
            return None
        if not isinstance(data, dict):
            return None
        return data

    async def adelete_token(self, token: str) -> None:
        """Delete a token payload.

        Args:
            token: Action token whose stored payload should be removed.
        """
        if self._is_disabled():
            return
        await self.string.delete(self.make_key(token))

    def create_token(
        self,
        payload: Mapping[str, Any],
        *,
        ttl_seconds: int | None = None,
        ttl_hours: int | None = None,
    ) -> str:
        """Synchronously create a token and store its payload.

        Args:
            payload: Mapping to serialize and store behind the generated token.
            ttl_seconds: Optional TTL override in seconds.
            ttl_hours: Optional TTL override in hours. Used only when
                ``ttl_seconds`` is not provided.

        Returns:
            The generated URL-safe action token.
        """
        return async_to_sync(self.acreate_token)(payload, ttl_seconds=ttl_seconds, ttl_hours=ttl_hours)

    def get_token_data(self, token: str) -> dict[str, Any] | None:
        """Synchronously return decoded token payload data.

        Args:
            token: Action token previously returned by ``create_token()``.

        Returns:
            The decoded payload mapping, or ``None`` when the token is
            missing, expired, disabled, or invalid.
        """
        return async_to_sync(self.aget_token_data)(token)

    def delete_token(self, token: str) -> None:
        """Synchronously delete token payload data.

        Args:
            token: Action token whose stored payload should be removed.
        """
        async_to_sync(self.adelete_token)(token)


def get_json_action_token_manager(prefix: str = "auth:action") -> JsonActionTokenRedisManager:
    """Return a JSON action token manager.

    Args:
        prefix: Redis key prefix used for stored token payloads.

    Returns:
        A ``JsonActionTokenRedisManager`` configured with the requested key
        prefix.
    """
    return JsonActionTokenRedisManager(prefix=prefix)
