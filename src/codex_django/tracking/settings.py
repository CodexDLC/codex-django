"""Settings helpers for the tracking runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.conf import settings


@dataclass(frozen=True)
class TrackingSettings:
    """Resolved tracking settings with conservative defaults."""

    enabled: bool = True
    redis_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"
    key_prefix: str = "tracking"
    ttl_seconds: int = 60 * 60 * 24 * 30
    skip_prefixes: tuple[str, ...] = (
        "/static/",
        "/media/",
        "/favicon",
        "/__debug__",
        "/admin/jsi18n",
    )
    track_anonymous: bool = False
    track_redirects: bool = True
    track_dashboard_widgets: bool = True
    analytics_url: str = "/cabinet/tracking/"
    analytics_days: int = 30


def get_tracking_settings() -> TrackingSettings:
    """Return normalized ``CODEX_TRACKING``/legacy ``CABINET_TRACKING`` settings."""

    raw: dict[str, Any] = {}
    legacy = getattr(settings, "CABINET_TRACKING", None)
    modern = getattr(settings, "CODEX_TRACKING", None)
    if isinstance(legacy, dict):
        raw.update(legacy)
    if isinstance(modern, dict):
        raw.update(modern)

    project_name = str(getattr(settings, "PROJECT_NAME", "") or "")
    key_prefix = str(raw.get("key_prefix") or (f"{project_name}:tracking" if project_name else "tracking"))
    redis_url = str(raw.get("redis_url") or getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
    redis_enabled = bool(raw.get("redis_enabled", getattr(settings, "CODEX_REDIS_ENABLED", False)))

    return TrackingSettings(
        enabled=bool(raw.get("enabled", True)),
        redis_enabled=redis_enabled,
        redis_url=redis_url,
        key_prefix=key_prefix,
        ttl_seconds=int(raw.get("ttl_seconds", 60 * 60 * 24 * 30)),
        skip_prefixes=tuple(str(prefix) for prefix in raw.get("skip_prefixes", TrackingSettings.skip_prefixes)),
        track_anonymous=bool(raw.get("track_anonymous", False)),
        track_redirects=bool(raw.get("track_redirects", True)),
        track_dashboard_widgets=bool(raw.get("track_dashboard_widgets", True)),
        analytics_url=str(raw.get("analytics_url", "/cabinet/tracking/")),
        analytics_days=int(raw.get("analytics_days", 30)),
    )
