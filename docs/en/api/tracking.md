<!-- DOC_TYPE: API -->

# Tracking Public API

The tracking package exposes a reusable page-analytics runtime for Django projects that want cabinet-ready traffic reporting without rebuilding the middleware and selector stack from scratch.

## Start here

- `codex_django.tracking.settings` for normalized tracking configuration via `get_tracking_settings()`.
- `codex_django.tracking.middleware` for `PageTrackingMiddleware`.
- `codex_django.tracking.selector` for `TrackingSelector` and dashboard-ready analytics payloads.
- `codex_django.tracking.providers` for cabinet dashboard provider registration.
- `codex_django.tracking.flush` and `codex_django.tracking.management.commands.flush_page_views` for moving Redis counters into ORM snapshots.

## Example

```python
from codex_django.tracking.middleware import PageTrackingMiddleware
from codex_django.tracking.selector import TrackingSelector
from codex_django.tracking.settings import get_tracking_settings
```

For the full generated module documentation, open [Tracking internals](internal/tracking.md).
