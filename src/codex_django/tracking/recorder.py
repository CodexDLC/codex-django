"""Request recorder used by the tracking middleware."""

from __future__ import annotations

from typing import Any

from django.utils import timezone


class TrackingRecorder:
    """Convert a Django request into a tracking counter update."""

    @staticmethod
    def record(request: Any) -> None:
        """Record one page view for the current request."""

        from .manager import get_tracking_manager

        today = timezone.localdate().isoformat()
        user = getattr(request, "user", None)
        user_id: str | None = None
        if user is not None and getattr(user, "is_authenticated", False):
            user_pk = getattr(user, "pk", None)
            if user_pk is not None:
                user_id = str(user_pk)
        path = getattr(request, "path", "") or "/"
        get_tracking_manager().record(path, today, user_id)
