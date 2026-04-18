"""Unit tests for the strict JSON cache serializer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from codex_django.cache.serializers import JsonSerializer

pytestmark = [pytest.mark.unit]


def test_roundtrip_primitives() -> None:
    ser = JsonSerializer()
    payload = {"s": "привет", "i": 42, "f": 3.14, "b": True, "n": None, "l": [1, 2]}
    assert ser.loads(ser.dumps(payload)) == payload


def test_ensure_ascii_is_disabled() -> None:
    ser = JsonSerializer()
    assert ser.dumps("привет") == '"привет"'


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 1, 1, 12, 0, 0),
        Decimal("1.5"),
        uuid4(),
        {"nested": {1, 2, 3}},
        b"bytes",
    ],
)
def test_dumps_raises_on_non_json_native(value: object) -> None:
    ser = JsonSerializer()
    with pytest.raises(TypeError):
        ser.dumps(value)
