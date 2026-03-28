"""Singleton-like cabinet settings model and Redis synchronization hooks."""

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
        """Return the display name used in admin and debug output."""
        return self.cabinet_name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Persist the singleton settings row under primary key ``1``.

        Args:
            *args: Positional arguments forwarded to ``models.Model.save()``.
            **kwargs: Keyword arguments forwarded to ``models.Model.save()``.
        """
        self.pk = 1  # Enforce Singleton
        super().save(*args, **kwargs)  # type: ignore[no-untyped-call]

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Refuse deletion so the singleton settings row always remains available.

        Args:
            *args: Unused positional arguments accepted for API compatibility.
            **kwargs: Unused keyword arguments accepted for API compatibility.

        Returns:
            The tuple Django expects from ``delete()``, always indicating that
            no rows were removed.
        """
        return 0, {}  # Deletion is forbidden

    @classmethod
    def load(cls) -> "CabinetSettings":
        """Load or create the singleton settings instance from the database.

        Returns:
            The singleton :class:`CabinetSettings` instance.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def to_cabinet_dict(self) -> dict[str, Any]:
        """Serialize the model to a Redis-friendly flat mapping.

        Returns:
            A dictionary that can be stored in the cabinet settings Redis hash.
        """
        data: dict[str, Any] = {"cabinet_name": self.cabinet_name}
        if self.logo:
            try:
                data["logo"] = self.logo.url
            except ValueError:
                data["logo"] = None
        return data

    @hook(AFTER_SAVE)  # type: ignore[untyped-decorator]
    def sync_to_redis(self) -> None:
        """Persist the latest cabinet settings payload to Redis after save."""
        from django.conf import settings

        if settings.DEBUG and not getattr(settings, "CODEX_REDIS_ENABLED", False):
            return

        from ..redis.managers.settings import CabinetSettingsRedisManager

        CabinetSettingsRedisManager().save_instance(self)
