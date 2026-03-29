<!-- DOC_TYPE: GUIDE -->

# Booking Guide

## Когда использовать

Используйте `booking`, когда Django-проекту нужны ORM-backed расписания, поиск слотов, создание записей и при необходимости multi-service chains поверх движка из `codex-services`.

## Добавление scaffold

```bash
codex-django add-booking --project myproject
```

## Что будет создано

- файлы приложения `booking/`
- файлы booking settings внутри `system/`
- cabinet booking views и templates
- booking page templates и partials

## Что нужно подключить после генерации

1. Добавить `booking` в `INSTALLED_APPS` или `LOCAL_APPS`.
2. Экспортировать `BookingSettings` из `system/models/__init__.py`.
3. Зарегистрировать generated admin integration для booking settings.
4. Выполнить миграции для `booking` и `system`.
5. Подключить `booking.urls` в корневом URL configuration.
6. Если используете cabinet pages, добавить generated cabinet booking URLs.

## Основные точки входа

- `codex_django.booking`
- `codex_django.booking.selectors`
- `codex_django.booking.adapters`
- `codex_django.booking.mixins`

## Связанные разделы

- Architecture: `booking`
- API reference: `codex_django.booking`
