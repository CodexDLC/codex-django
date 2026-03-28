<!-- DOC_TYPE: GUIDE -->

# Cabinet Guide

## Когда использовать

Используйте `cabinet`, если нужен переиспользуемый client-facing dashboard layer с navigation widgets, cached settings и profile-oriented страницами.

## Добавление scaffold

```bash
codex-django add-client-cabinet --project myproject
```

## Что будет создано

- cabinet adapters и client views
- cabinet client templates
- модель `UserProfile` в `system/models/`

## Что нужно подключить после генерации

1. Включить generated cabinet adapter settings в scaffolded settings module.
2. Добавить generated client cabinet URL patterns в `cabinet/urls.py`.
3. Экспортировать `UserProfile` из `system/models/__init__.py`.
4. Выполнить миграции.

## Основные точки входа

- `codex_django.cabinet`
- `codex_django.cabinet.selector`
- `codex_django.cabinet.redis`

## Связанные разделы

- Architecture: `cabinet`
- API reference: `codex_django.cabinet`
