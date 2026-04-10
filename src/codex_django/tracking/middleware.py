"""Middleware for page-view tracking."""

from __future__ import annotations

import logging
from typing import Any

from .settings import get_tracking_settings

logger = logging.getLogger(__name__)


class PageTrackingMiddleware:
    """Record eligible GET responses without affecting request handling."""

    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        response = self.get_response(request)
        try:
            if self._should_track(request, response):
                from .recorder import TrackingRecorder

                TrackingRecorder.record(request)
        except Exception:
            logger.exception("Tracking recording failed")
        return response

    def _should_track(self, request: Any, response: Any) -> bool:
        cfg = get_tracking_settings()
        if not cfg.enabled:
            return False
        if getattr(request, "method", "") != "GET":
            return False
        status_code = int(getattr(response, "status_code", 0) or 0)
        allowed_statuses = (200, 301, 302) if cfg.track_redirects else (200,)
        if status_code not in allowed_statuses:
            return False
        path = getattr(request, "path", "") or ""
        if any(path.startswith(prefix) for prefix in cfg.skip_prefixes):
            return False
        user = getattr(request, "user", None)
        return bool(cfg.track_anonymous or getattr(user, "is_authenticated", False))
