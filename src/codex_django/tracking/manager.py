"""Redis-backed counters for page tracking."""

from __future__ import annotations

from typing import Any, Protocol, cast

from .settings import get_tracking_settings


class SupportsTrackingPipeline(Protocol):
    """Subset of Redis pipeline operations used by tracking."""

    def hincrby(self, name: str, key: str, amount: int = 1) -> Any: ...

    def expire(self, name: str, time: int) -> Any: ...

    def pfadd(self, name: str, *values: str) -> Any: ...

    def hgetall(self, name: str) -> Any: ...

    def execute(self) -> list[Any]: ...


class SupportsTrackingRedis(Protocol):
    """Subset of Redis operations used by tracking."""

    def pipeline(self, transaction: bool = False) -> SupportsTrackingPipeline: ...

    def hgetall(self, name: str) -> dict[object, object]: ...

    def pfcount(self, name: str) -> int: ...


def _decode_mapping(raw: dict[object, object]) -> dict[str, str]:
    decoded: dict[str, str] = {}
    for key, value in raw.items():
        k = key.decode() if isinstance(key, bytes) else str(key)
        v = value.decode() if isinstance(value, bytes) else str(value)
        decoded[k] = v
    return decoded


class TrackingRedisManager:
    """Record and read daily tracking counters from Redis."""

    def __init__(self, redis_client: SupportsTrackingRedis | None = None) -> None:
        self._redis_client = redis_client

    def _redis(self) -> SupportsTrackingRedis | None:
        if self._redis_client is not None:
            return self._redis_client
        cfg = get_tracking_settings()
        if not cfg.enabled or not cfg.redis_enabled:
            return None
        try:
            from redis import Redis

            client = Redis.from_url(cfg.redis_url, decode_responses=True)
            return cast(SupportsTrackingRedis, client)
        except Exception:
            return None

    def _daily_key(self, date_str: str) -> str:
        return f"{get_tracking_settings().key_prefix}:daily:{date_str}"

    def _uniq_key(self, date_str: str) -> str:
        return f"{get_tracking_settings().key_prefix}:uniq:{date_str}"

    def record(self, path: str, date_str: str, user_id: str | None) -> None:
        """Increment page view and unique visitor counters for a day."""

        redis = self._redis()
        if redis is None:
            return
        cfg = get_tracking_settings()
        pipe: SupportsTrackingPipeline = redis.pipeline(transaction=False)
        pipe.hincrby(self._daily_key(date_str), path, 1)
        pipe.expire(self._daily_key(date_str), cfg.ttl_seconds)
        if user_id:
            pipe.pfadd(self._uniq_key(date_str), user_id)
            pipe.expire(self._uniq_key(date_str), cfg.ttl_seconds)
        pipe.execute()

    def get_daily(self, date_str: str) -> dict[str, str] | None:
        """Return path -> views for one date from Redis."""

        redis = self._redis()
        if redis is None:
            return None
        raw = redis.hgetall(self._daily_key(date_str))
        return _decode_mapping(raw) if raw else None

    def get_unique_count(self, date_str: str) -> int:
        """Return approximate unique visitor count for one date."""

        redis = self._redis()
        if redis is None:
            return 0
        return int(redis.pfcount(self._uniq_key(date_str)))

    def get_multi_day(self, dates: list[str]) -> list[dict[str, str] | None]:
        """Return Redis daily snapshots for multiple dates."""

        redis = self._redis()
        if redis is None:
            return [None] * len(dates)
        pipe: SupportsTrackingPipeline = redis.pipeline(transaction=False)
        for date_str in dates:
            pipe.hgetall(self._daily_key(date_str))
        results = cast(list[dict[object, object] | None], pipe.execute())
        return [_decode_mapping(snapshot) if snapshot else None for snapshot in results]


_manager = TrackingRedisManager()


def get_tracking_manager() -> TrackingRedisManager:
    """Return the process-wide tracking Redis manager."""

    return _manager
