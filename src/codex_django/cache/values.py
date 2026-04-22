"""Explicit helpers for caching non-JSON-native Python values.

The Redis cache backend stores values as strict JSON and raises ``TypeError``
for anything that ``json.dumps`` cannot handle (``datetime``, ``date``,
``Decimal``, ``UUID``, ``set`` …). Rather than smuggle magic type tags into
the serializer (which would leak into every Redis consumer and make reverting
impossible), we expose an **explicit** coder that callers invoke themselves::

    from codex_django.cache.values import CacheCoder

    cache.set("user:42:last_seen", CacheCoder.dump_datetime(user.last_seen), 3600)
    raw = cache.get("user:42:last_seen")
    last_seen = CacheCoder.load_datetime(raw) if raw else None

The ``dump()`` / ``load()`` helpers cover ad-hoc payloads (nested ``dict`` /
``list`` / ``tuple``); ``load()`` requires explicit ``hints`` because JSON
does not preserve Python types.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from django.utils.encoding import force_str
from django.utils.functional import Promise


class CacheCoder:
    """Round-trip helpers for non-JSON-native values.

    Every helper is a pure function — no Redis access, no Django settings
    lookup — so the class is importable and usable anywhere.
    """

    # ---- datetime ------------------------------------------------------

    @staticmethod
    def dump_datetime(value: datetime) -> str:
        return value.isoformat()

    @staticmethod
    def load_datetime(raw: str) -> datetime:
        return datetime.fromisoformat(raw)

    # ---- date ----------------------------------------------------------

    @staticmethod
    def dump_date(value: date) -> str:
        return value.isoformat()

    @staticmethod
    def load_date(raw: str) -> date:
        return date.fromisoformat(raw)

    # ---- time ----------------------------------------------------------

    @staticmethod
    def dump_time(value: time) -> str:
        return value.isoformat()

    @staticmethod
    def load_time(raw: str) -> time:
        return time.fromisoformat(raw)

    # ---- timedelta -----------------------------------------------------

    @staticmethod
    def dump_timedelta(value: timedelta) -> float:
        return value.total_seconds()

    @staticmethod
    def load_timedelta(raw: float | int) -> timedelta:
        return timedelta(seconds=float(raw))

    # ---- decimal -------------------------------------------------------

    @staticmethod
    def dump_decimal(value: Decimal) -> str:
        return str(value)

    @staticmethod
    def load_decimal(raw: str) -> Decimal:
        return Decimal(raw)

    # ---- uuid ----------------------------------------------------------

    @staticmethod
    def dump_uuid(value: UUID) -> str:
        return str(value)

    @staticmethod
    def load_uuid(raw: str) -> UUID:
        return UUID(raw)

    # ---- set -----------------------------------------------------------

    @staticmethod
    def dump_set(value: set[Any] | frozenset[Any]) -> list[Any]:
        return list(value)

    @staticmethod
    def load_set(raw: Sequence[Any]) -> set[Any]:
        return set(raw)

    # ---- bytes ---------------------------------------------------------

    @staticmethod
    def dump_bytes(value: bytes) -> str:
        """Encode ``bytes`` as a hex string (roundtrip-safe, ASCII)."""
        return value.hex()

    @staticmethod
    def load_bytes(raw: str) -> bytes:
        return bytes.fromhex(raw)

    # ---- scalar helpers ------------------------------------------------

    @staticmethod
    def dump_bool(value: bool) -> str:
        return "1" if value else "0"

    @staticmethod
    def load_bool(raw: str) -> bool:
        return raw == "1"

    @staticmethod
    def dump_none() -> str:
        return ""

    # ---- generic recursive dump ---------------------------------------

    @classmethod
    def dump(cls, value: Any) -> Any:
        """Best-effort conversion of a nested structure to JSON-native types.

        Recurses through ``dict`` / ``list`` / ``tuple``. Any value of an
        unknown type is returned as-is — JSON serialization will raise
        ``TypeError`` on it later, which is the intended strict-mode signal.
        """
        if isinstance(value, bool):
            return cls.dump_bool(value)
        if value is None:
            return cls.dump_none()
        if isinstance(value, str | int | float):
            return value
        if isinstance(value, Enum):
            return cls.dump(value.value)
        if isinstance(value, Promise):
            return force_str(value)
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, datetime):
            return cls.dump_datetime(value)
        if isinstance(value, date):
            return cls.dump_date(value)
        if isinstance(value, time):
            return cls.dump_time(value)
        if isinstance(value, timedelta):
            return cls.dump_timedelta(value)
        if isinstance(value, Decimal):
            return cls.dump_decimal(value)
        if isinstance(value, UUID):
            return cls.dump_uuid(value)
        if isinstance(value, set | frozenset):
            return [cls.dump(v) for v in value]
        if isinstance(value, bytes):
            return cls.dump_bytes(value)
        if isinstance(value, Mapping):
            return {k: cls.dump(v) for k, v in value.items()}
        if isinstance(value, list | tuple):
            return [cls.dump(v) for v in value]
        return value
