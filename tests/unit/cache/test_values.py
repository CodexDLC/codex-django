"""Unit tests for :class:`codex_django.cache.values.CacheCoder`."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import uuid4

import pytest
from django.utils.translation import gettext_lazy

from codex_django.cache.values import CacheCoder

pytestmark = [pytest.mark.unit]


def test_datetime_roundtrip() -> None:
    value = datetime(2026, 4, 17, 12, 30, 45, tzinfo=UTC)
    assert CacheCoder.load_datetime(CacheCoder.dump_datetime(value)) == value


def test_date_roundtrip() -> None:
    value = date(2026, 4, 17)
    assert CacheCoder.load_date(CacheCoder.dump_date(value)) == value


def test_time_roundtrip() -> None:
    value = time(12, 30, 45)
    assert CacheCoder.load_time(CacheCoder.dump_time(value)) == value


def test_timedelta_roundtrip() -> None:
    value = timedelta(days=1, hours=2, minutes=3)
    assert CacheCoder.load_timedelta(CacheCoder.dump_timedelta(value)) == value


def test_decimal_roundtrip_preserves_precision() -> None:
    value = Decimal("3.14159265358979323846")
    assert CacheCoder.load_decimal(CacheCoder.dump_decimal(value)) == value


def test_uuid_roundtrip() -> None:
    value = uuid4()
    assert CacheCoder.load_uuid(CacheCoder.dump_uuid(value)) == value


def test_set_roundtrip() -> None:
    value = {1, 2, 3}
    assert CacheCoder.load_set(CacheCoder.dump_set(value)) == value


def test_bytes_roundtrip() -> None:
    value = b"\x00\x01hello"
    assert CacheCoder.load_bytes(CacheCoder.dump_bytes(value)) == value


def test_bool_none_enum_path_and_lazy_dump() -> None:
    class Status(Enum):
        ACTIVE = "active"

    assert CacheCoder.dump(True) == "1"
    assert CacheCoder.dump(False) == "0"
    assert CacheCoder.load_bool("1") is True
    assert CacheCoder.load_bool("0") is False
    assert CacheCoder.dump(None) == ""
    assert CacheCoder.dump(Status.ACTIVE) == "active"
    path = Path("docs/readme.md")
    assert CacheCoder.dump(path) == str(path)
    assert CacheCoder.dump(gettext_lazy("Hello")) == "Hello"


def test_dump_recurses_into_nested_structures() -> None:
    dt = datetime(2026, 4, 17, tzinfo=UTC)
    uid = uuid4()
    payload = {"when": dt, "who": uid, "items": [{"price": Decimal("1.5")}, {1, 2}]}
    dumped = CacheCoder.dump(payload)
    assert dumped == {
        "when": dt.isoformat(),
        "who": str(uid),
        "items": [{"price": "1.5"}, [1, 2]],
    }


def test_dump_leaves_unknown_types_as_is() -> None:
    class Opaque:
        pass

    obj = Opaque()
    # Unknown types are returned untouched — json.dumps will raise later,
    # which is the intended strict-mode signal.
    assert CacheCoder.dump(obj) is obj


def test_dump_primitives_passthrough() -> None:
    for v in ("x", 1, 1.5):
        assert CacheCoder.dump(v) == v
