"""Flush Redis tracking counters into database snapshots."""

from __future__ import annotations

from django.utils import timezone


def flush_page_views(date_str: str | None = None) -> int:
    """Upsert one day's Redis page counters into ``PageView`` rows."""

    from .manager import get_tracking_manager
    from .models import PageView

    day = date_str or timezone.localdate().isoformat()
    raw = get_tracking_manager().get_daily(day)
    if not raw:
        return 0

    PageView.objects.bulk_create(
        [PageView(path=path, date=day, views=int(views)) for path, views in raw.items()],
        update_conflicts=True,
        update_fields=["views"],
        unique_fields=["path", "date"],
    )
    return len(raw)
