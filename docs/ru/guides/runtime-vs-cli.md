<!-- DOC_TYPE: GUIDE -->

# Runtime И CLI

## Два Пакета После Split

Теперь Codex Django tooling живет в двух связанных пакетах:

- `codex-django` для runtime modules, которые импортируются Django-проектом после установки;
- `codex-django-cli` для CLI/scaffolding tooling, которое создает или расширяет этот проект.

Это разделение помогает и в навигации по документации, и в понимании того, что действительно должно жить в production.

## Runtime Layer

Runtime-слой это то, что Django-приложение реально импортирует и исполняет:

- `codex_django.core`
- `codex_django.system`
- `codex_django.messaging`
- `codex_django.notifications`
- `codex_django.booking`
- `codex_django.cabinet`

Здесь находятся переиспользуемые модели, mixins, selectors, adapters, Redis helpers, templates и integration points. `codex_django.notifications` теперь compatibility-only; новые messaging integrations должны импортировать `codex_django.messaging`.

## CLI Package

CLI-пакет это то, чем разработчик создает и развивает структуру проекта:

- `codex_django_cli.main`
- command handlers в `codex_django_cli.commands`
- blueprint trees в `codex_django_cli.blueprints`
- rendering logic в `codex_django_cli.engine`

Этот пакет отвечает за generation, orchestration и project assembly.
Generated code при этом может продолжать импортировать `codex_django.*`, и это ожидаемо, потому что blueprints нацелены на runtime package.

## Как Проводить Границу

- runtime code живет в долгой жизни приложения;
- CLI code работает до или вокруг runtime path, создавая файлы, wiring и стартовые defaults;
- generated output становится уже вашим проектным кодом и дальше может эволюционировать независимо.
- временные compatibility shims под `codex_django.cli` еще существуют, но это не долгосрочный дом для CLI-реализации.

## Практическое Правило

Если вопрос звучит как "что мой Django app импортирует в runtime?", оставайтесь в runtime modules.
Если вопрос звучит как "какая команда создает или расширяет эту структуру?", переходите в документацию и исходники `codex-django-cli`.

Обратите внимание, что установщик агентских навыков (`python -m codex_django.agent_skills`) входит в сам runtime-пакет `codex-django`; он полностью автономен (offline) и не требует ни companion-пакета CLI, ни настройки Django. См. [Гайд по агентским навыкам](./agent-skills.md).

## Связанные Страницы

- [Getting Started](../getting-started.md)
- [Режимы установки](./installation-modes.md)
- [Структура проекта](./project-structure.md)
