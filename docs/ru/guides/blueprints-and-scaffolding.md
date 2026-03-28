<!-- DOC_TYPE: GUIDE -->

# Blueprint Workflow

## Как Работают Scaffold-Команды

Каждая крупная команда из `codex-django-cli` переводит намерение разработчика в один или несколько blueprint renders.

Типичный flow:

1. Вы выбираете команду вроде `init`, `add-client-cabinet`, `add-booking` или `add-notifications`.
2. Команда определяет нужное blueprint family.
3. `CLIEngine` рендерит шаблоны и копирует static assets в target project.
4. Команда печатает follow-up шаги, которые еще нужно применить вручную.

## Семейства Blueprints

Blueprint tree в `codex-django-cli` организован по типу результата:

- `repo` для repository shell files;
- `project` для базовой Django project layout;
- `apps` для app-level building blocks;
- `features` для cross-cutting functional bundles;
- `deploy` для operational и deployment-oriented output.

## Безопасный Рабочий Паттерн

Используйте такой порядок при добавлении новой функциональности:

1. Сгенерировать файлы.
2. Прочитать follow-up instructions.
3. Довести wiring в settings, admin, URLs и migrations.
4. Прогнать локальные проверки.

## Почему Это Важно

`codex-django` теперь отвечает за runtime-слой, который использует generated project.
`codex-django-cli` владеет project construction, но blueprint workflow все равно важен здесь, потому что generated code целенаправленно импортирует runtime-модули `codex_django.*`.

## Связанные Страницы

- [Getting Started](../getting-started.md)
- [Структура проекта](./project-structure.md)
