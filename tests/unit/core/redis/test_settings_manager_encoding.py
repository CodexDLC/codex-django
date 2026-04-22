from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import UTC, date, datetime, time
from decimal import Decimal
from types import TracebackType
from typing import Any
from uuid import uuid4

import pytest
from django.db import models

from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager

pytestmark = [pytest.mark.unit]


class TypedSettingsModel(models.Model):
    enabled = models.BooleanField(default=False)
    nullable_enabled = models.BooleanField(null=True, default=None)
    title = models.CharField(max_length=64, blank=True)
    optional_count = models.IntegerField(null=True, default=None)
    launched_at = models.DateTimeField(null=True, default=None)
    launch_date = models.DateField(null=True, default=None)
    launch_time = models.TimeField(null=True, default=None)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)
    public_id = models.UUIDField(null=True, default=None)
    payload = models.JSONField(null=True, default=None)

    class Meta:
        app_label = "tests"

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "nullable_enabled": self.nullable_enabled,
            "title": self.title,
            "optional_count": self.optional_count,
            "launched_at": self.launched_at,
            "launch_date": self.launch_date,
            "launch_time": self.launch_time,
            "price": self.price,
            "public_id": self.public_id,
            "payload": self.payload,
        }


def test_site_settings_decode_fields_restores_model_types() -> None:
    manager = DjangoSiteSettingsManager()
    uid = uuid4()
    raw = {
        "enabled": "1",
        "nullable_enabled": "",
        "title": "",
        "optional_count": "",
        "launched_at": "2026-04-22T12:30:45+00:00",
        "launch_date": "2026-04-22",
        "launch_time": "12:30:45",
        "price": "10.50",
        "public_id": str(uid),
        "payload": '{"flags":["a"],"enabled":true}',
    }

    decoded = manager._decode_fields(raw, TypedSettingsModel)

    assert decoded == {
        "enabled": True,
        "nullable_enabled": None,
        "title": "",
        "optional_count": None,
        "launched_at": datetime(2026, 4, 22, 12, 30, 45, tzinfo=UTC),
        "launch_date": date(2026, 4, 22),
        "launch_time": time(12, 30, 45),
        "price": Decimal("10.50"),
        "public_id": uid,
        "payload": {"flags": ["a"], "enabled": True},
    }


def test_site_settings_save_instance_uses_cache_coder(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = DjangoSiteSettingsManager()
    uid = uuid4()
    instance = TypedSettingsModel(
        enabled=True,
        nullable_enabled=None,
        title="Site",
        optional_count=None,
        launched_at=datetime(2026, 4, 22, 12, 30, 45, tzinfo=UTC),
        launch_date=date(2026, 4, 22),
        launch_time=time(12, 30, 45),
        price=Decimal("10.50"),
        public_id=uid,
        payload={"flags": ["a"], "enabled": True},
    )

    class SyncHashContext(AbstractContextManager[object]):
        def __enter__(self) -> object:
            return hash_ops

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            return None

    class HashOps:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict[str, Any]]] = []

        def set_fields(self, key: str, data: dict[str, Any]) -> None:
            self.calls.append((key, data))

    hash_ops = HashOps()
    monkeypatch.setattr(manager, "sync_hash", lambda: SyncHashContext())

    manager.save_instance(instance)

    assert hash_ops.calls == [
        (
            manager.make_key("site_settings"),
            {
                "enabled": "1",
                "nullable_enabled": "",
                "title": "Site",
                "optional_count": "",
                "launched_at": "2026-04-22T12:30:45+00:00",
                "launch_date": "2026-04-22",
                "launch_time": "12:30:45",
                "price": "10.50",
                "public_id": str(uid),
                "payload": '{"flags": ["a"], "enabled": true}',
            },
        )
    ]
