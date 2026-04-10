"""Django app configuration for the reusable tracking package."""

from django.apps import AppConfig


class TrackingConfig(AppConfig):
    """Register the tracking runtime and optional cabinet declarations."""

    name = "codex_django.tracking"
    label = "codex_tracking"
    verbose_name = "Codex Tracking"

    def ready(self) -> None:
        """Import dashboard providers/declarations after Django app loading."""
        from . import cabinet as _cabinet  # noqa: F401
        from . import providers as _providers  # noqa: F401
