"""Serializers for the Redis cache backend.

Default policy: strict JSON. Any value that cannot be encoded as JSON
raises :class:`TypeError` — the backend **never** silently falls back to
``pickle``. Callers that need to cache non-JSON-native values (``datetime``,
``Decimal``, ``UUID``, ``set`` …) should use the helpers in
:mod:`codex_django.cache.values` to convert them explicitly.

A downstream project may swap the serializer via ``OPTIONS["SERIALIZER"]``
(dotted path to a class implementing :class:`Serializer`).
"""

from __future__ import annotations

import json
from typing import Any, Protocol


class Serializer(Protocol):
    """Minimal cache serializer interface."""

    def dumps(self, value: Any) -> str:  # pragma: no cover - protocol
        ...

    def loads(self, raw: str) -> Any:  # pragma: no cover - protocol
        ...


class JsonSerializer:
    """Strict JSON serializer — UTF-8, no ``ensure_ascii`` escaping."""

    def dumps(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    def loads(self, raw: str) -> Any:
        return json.loads(raw)
