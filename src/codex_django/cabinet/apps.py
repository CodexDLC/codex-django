from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CabinetConfig(AppConfig):
    name = "codex_django.cabinet"
    label = "codex_cabinet"
    verbose_name = "Codex Cabinet"

    def ready(self) -> None:
        # Django finds and executes cabinet.py in all INSTALLED_APPS.
        # This populates cabinet_registry in memory — safe, runs after all apps are loaded.
        autodiscover_modules("cabinet")
