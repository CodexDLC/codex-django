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
        'contact': {'label': _('Contacts'), 'icon': 'bi-telephone'},
        'geo': {'label': _('Geo Data'), 'icon': 'bi-geo-alt'},
        'social': {'label': _('Social Networks'), 'icon': 'bi-share'},
        'marketing': {'label': _('Marketing'), 'icon': 'bi-graph-up'},
        'technical': {'label': _('Technical'), 'icon': 'bi-gear-wide'},
        'email': {'label': _('Email / SMTP'), 'icon': 'bi-envelope'},
        'quick_access': {'label': _('Quick Access'), 'icon': 'bi-lightning-charge'},
    }

    @staticmethod
    def get_tabs() -> list[dict[str, Any]]:
        """Возвращает список всех зарегистрированных вкладок (сегментов).
        
        Сканирует как библиотеку, так и проект на наличие файлов _*.html в папке 
        cabinet/site_settings/partials/.
        """
        from django.template.utils import get_app_template_dirs

        # Собираем все директории шаблонов (из настроек и из приложений)
        template_dirs = []
        
        # 1. Проверяем пути из settings.TEMPLATES['DIRS']
        from django.conf import settings
        templates = cast(list[dict[str, Any]], settings.TEMPLATES)
        for t_conf in templates:
            if not isinstance(t_conf, dict):
                continue
            for d in t_conf.get('DIRS', []):
                template_dirs.append(os.path.join(d, 'cabinet/site_settings/partials'))

        # 2. Проверяем папки шаблонов во всех установленных приложениях
        app_template_dirs = cast(Iterable[Any], get_app_template_dirs('templates'))
        for app_dir in app_template_dirs:
            template_dirs.append(os.path.join(app_dir, 'cabinet/site_settings/partials'))

        found_files = set()
        for d in template_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.startswith('_') and f.endswith('.html'):
                        found_files.add(f)
        
        tabs = []
        for f in sorted(list(found_files)):
            slug = f[1:-5]
            config = SiteSettingsService.TABS_CONFIG.get(slug, {})
            label = config.get('label', slug.replace('_', ' ').capitalize())
            icon = config.get('icon', 'bi-gear')
            
            tabs.append({
                'slug': slug,
                'label': label,
                'icon': icon,
                'partial_path': f'cabinet/site_settings/partials/{f}',
                'url': f'#{slug}'
            })
        return tabs

    @staticmethod
    def get_context(request: HttpRequest) -> dict[str, Any]:
        """Формирует полный контекст для одой общей страницы настроек."""
        from codex_django.cabinet.redis.managers.settings import CabinetSettingsRedisManager
        
        tabs = SiteSettingsService.get_tabs()
        settings_data = CabinetSettingsRedisManager().get() or {}
        selected_keys = parse_selected_keys(settings_data.get("staff_quick_access_links"))

        return {
            "tabs": tabs,
            "settings_data": settings_data,
            "quick_access_groups": get_staff_quick_access_candidates(),
            "selected_staff_quick_access": sorted(selected_keys),
        }

    @staticmethod
    def save_context(request: HttpRequest) -> tuple[bool, str]:
        """Сохраняет данные из POST-запроса в модель SiteSettings."""
        from django.conf import settings
        from django.apps import apps
        from django.db import models
        
        # Получаем модель из настроек (например, 'system.SiteSettings')
        model_path = getattr(settings, 'CODEX_SITE_SETTINGS_MODEL', None)
        if not model_path:
            return False, "Параметр CODEX_SITE_SETTINGS_MODEL не задан в settings.py"
        
        try:
            SiteSettings = apps.get_model(model_path)
            instance = SiteSettings.objects.first()
            if not instance:
                instance = SiteSettings()
            
            # Обновляем все поля, которые есть в POST
            # Исключаем служебные поля Django
            exclude = ['csrfmiddlewaretoken', 'btn-save']
            
            # Собираем данные. Обработка чекбоксов (отсутствие в POST = False)
            data = request.POST.dict()
            
            for field in instance._meta.get_fields():
                if field.name in exclude or not field.concrete:
                    continue
                
                if field.name in data:
                    raw_value = data[field.name]
                    # Преобразование типов для Boolean
                    if isinstance(field, (models.BooleanField, models.NullBooleanField)):
                        final_value: Any = (raw_value.lower() in ['true', 'on', '1'])
                    else:
                        final_value = raw_value
                    setattr(instance, field.name, final_value)
                elif isinstance(field, (models.BooleanField, models.NullBooleanField)):
                    # Если чекбокса нет в POST — значит он выключен
                    setattr(instance, field.name, False)
            
            instance.save()
            return True, str(_("Settings saved successfully"))
            
        except Exception as e:
            return False, f"Ошибка при сохранении: {str(e)}"
