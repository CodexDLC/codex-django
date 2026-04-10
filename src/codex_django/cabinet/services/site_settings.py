import os
from collections.abc import Iterable
from typing import Any, cast

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from ..quick_access import get_staff_quick_access_candidates, parse_selected_keys

"""
SiteSettingsService
===================
Мост между view настроек сайта и частичными шаблонами вкладок.
"""


class SiteSettingsService:
    # Конфигурация известных вкладок (иконка и название)
    TABS_CONFIG = {
        "contact": {"label": _("Contacts"), "icon": "bi-telephone"},
        "geo": {"label": _("Geo Data"), "icon": "bi-geo-alt"},
        "social": {"label": _("Social Networks"), "icon": "bi-share"},
        "marketing": {"label": _("Marketing"), "icon": "bi-graph-up"},
        "technical": {"label": _("Technical"), "icon": "bi-gear-wide"},
        "email": {"label": _("Email / SMTP"), "icon": "bi-envelope"},
        "quick_access": {"label": _("Quick Access"), "icon": "bi-lightning-charge"},
    }
    model_setting_name = "CODEX_SITE_SETTINGS_MODEL"
    excluded_post_fields = ("csrfmiddlewaretoken", "btn-save")

    @classmethod
    def get_model_path(cls) -> str | None:
        """Return the configured site-settings model path."""
        from django.conf import settings

        return getattr(settings, cls.model_setting_name, None)

    @classmethod
    def get_model(cls) -> type[Any] | None:
        """Return the configured site-settings model, if configured."""
        from django.apps import apps

        model_path = cls.get_model_path()
        if not model_path:
            return None
        return apps.get_model(model_path)

    @classmethod
    def user_can_access(cls, user: Any) -> bool:
        """Permission hook for projects that need stricter settings access."""
        return bool(getattr(user, "is_authenticated", False))

    @classmethod
    def iter_tab_template_dirs(cls) -> list[str]:
        """Return template directories scanned for settings partials."""
        from django.conf import settings
        from django.template.utils import get_app_template_dirs

        template_dirs: list[str] = []

        templates = cast(list[dict[str, Any]], settings.TEMPLATES)
        for t_conf in templates:
            if not isinstance(t_conf, dict):
                continue
            for d in t_conf.get("DIRS", []):
                template_dirs.append(os.path.join(d, "cabinet/site_settings/partials"))

        app_template_dirs = cast(Iterable[Any], get_app_template_dirs("templates"))
        for app_dir in app_template_dirs:
            template_dirs.append(os.path.join(app_dir, "cabinet/site_settings/partials"))

        return template_dirs

    @classmethod
    def get_tab_config(cls, slug: str) -> dict[str, Any]:
        """Return configured label/icon metadata for a settings tab."""
        return cls.TABS_CONFIG.get(slug, {})

    @classmethod
    def get_excluded_post_fields(cls) -> tuple[str, ...]:
        """Return POST field names that must not be persisted."""
        return cls.excluded_post_fields

    @classmethod
    def get_tabs(cls) -> list[dict[str, Any]]:
        """Возвращает список всех зарегистрированных вкладок (сегментов).

        Сканирует как библиотеку, так и проект на наличие файлов _*.html в папке
        cabinet/site_settings/partials/.
        """
        found_files = set()
        for d in cls.iter_tab_template_dirs():
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.startswith("_") and f.endswith(".html"):
                        found_files.add(f)

        tabs = []
        for f in sorted(found_files):
            slug = f[1:-5]
            config = cls.get_tab_config(slug)
            label = config.get("label", slug.replace("_", " ").capitalize())
            icon = config.get("icon", "bi-gear")

            tabs.append(
                {
                    "slug": slug,
                    "label": label,
                    "icon": icon,
                    "partial_path": f"cabinet/site_settings/partials/{f}",
                    "url": f"#{slug}",
                }
            )
        return tabs

    @classmethod
    def get_context(cls, request: HttpRequest) -> dict[str, Any]:
        """Формирует полный контекст для одой общей страницы настроек."""
        from codex_django.cabinet.redis.managers.settings import CabinetSettingsRedisManager

        tabs = cls.get_tabs()
        settings_data = CabinetSettingsRedisManager().get() or {}
        selected_keys = parse_selected_keys(settings_data.get("staff_quick_access_links"))

        return {
            "tabs": tabs,
            "settings_data": settings_data,
            "quick_access_groups": get_staff_quick_access_candidates(),
            "selected_staff_quick_access": sorted(selected_keys),
        }

    @classmethod
    def save_context(cls, request: HttpRequest) -> tuple[bool, str]:
        """Сохраняет данные из POST-запроса в модель SiteSettings."""
        from django.db import models

        SiteSettings = cls.get_model()
        if SiteSettings is None:
            return False, f"Параметр {cls.model_setting_name} не задан в settings.py"

        try:
            instance = SiteSettings.objects.first()
            if not instance:
                instance = SiteSettings()

            # Обновляем все поля, которые есть в POST
            # Исключаем служебные поля Django
            exclude = cls.get_excluded_post_fields()

            # Собираем данные. Обработка чекбоксов (отсутствие в POST = False)
            data = request.POST.dict()

            for field in instance._meta.get_fields():
                if field.name in exclude or not field.concrete:
                    continue

                if field.name in data:
                    raw_value = data[field.name]
                    # Преобразование типов для Boolean
                    if isinstance(field, models.BooleanField | models.NullBooleanField):
                        final_value: Any = raw_value.lower() in ["true", "on", "1"]
                    else:
                        final_value = raw_value
                    setattr(instance, field.name, final_value)
                elif isinstance(field, models.BooleanField | models.NullBooleanField):
                    # Если чекбокса нет в POST — значит он выключен
                    setattr(instance, field.name, False)

            instance.save()
            return True, str(_("Settings saved successfully"))

        except Exception as e:
            return False, f"Ошибка при сохранении: {str(e)}"
