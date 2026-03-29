"""Django app configuration for the reusable cabinet package."""

from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CabinetConfig(AppConfig):
    """Register the cabinet package and auto-discover feature declarations."""

    name = "codex_django.cabinet"
    label = "codex_cabinet"
    verbose_name = "Codex Cabinet"

    def ready(self) -> None:
        """Load ``cabinet.py`` modules from installed apps after startup."""
        # Django finds and executes cabinet.py in all INSTALLED_APPS.
        # This populates cabinet_registry in memory — safe, runs after all apps are loaded.
        autodiscover_modules("cabinet")
