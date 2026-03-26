from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook


class CabinetSettings(LifecycleModelMixin, models.Model):
    """Cabinet settings — Singleton (always one instance, pk=1).

    Stores cabinet-level configuration: name, logo, theme overrides.
    Auto-syncs to Redis on save via django_lifecycle hook.
    Skips Redis sync in DEBUG mode unless CODEX_REDIS_ENABLED=True.
    """

    cabinet_name = models.CharField(_("Cabinet name"), max_length=100, default="Кабинет")
    logo = models.ImageField(_("Logo"), upload_to="cabinet/", blank=True)

    class Meta:
        verbose_name = _("Cabinet settings")
        verbose_name_plural = _("Cabinet settings")

    def __str__(self) -> str:
        return self.cabinet_name

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.pk = 1  # Enforce Singleton
        super().save(*args, **kwargs)  # type: ignore[no-untyped-call]

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        return 0, {}  # Deletion is forbidden

    @classmethod
    def load(cls) -> "CabinetSettings":
        """Load from DB. Caching is handled by CabinetSettingsRedisManager."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def to_cabinet_dict(self) -> dict[str, Any]:
        """Serialise to dict for Redis hash storage."""
        data: dict[str, Any] = {"cabinet_name": self.cabinet_name}
        if self.logo:
            try:
                data["logo"] = self.logo.url
            except ValueError:
                data["logo"] = None
        return data

    @hook(AFTER_SAVE)  # type: ignore[untyped-decorator]
    def sync_to_redis(self) -> None:
        from django.conf import settings

        if settings.DEBUG and not getattr(settings, "CODEX_REDIS_ENABLED", False):
            return

        from ..redis.managers.settings import CabinetSettingsRedisManager

        CabinetSettingsRedisManager().save_instance(self)
