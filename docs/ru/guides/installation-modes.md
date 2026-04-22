<!-- DOC_TYPE: GUIDE -->

# Режимы Установки

## Выбирайте Самый Узкий Режим Под Задачу

Практически `codex-django` используется в трех режимах:

1. Runtime library mode, когда проекту нужны только переиспользуемые Django-модули.
2. Scaffold mode, когда разработчик генерирует или расширяет Codex-shaped проект через `codex-django-cli`.
3. Contributor mode, когда меняется сама библиотека `codex-django`.

## Runtime Library Mode

Ставьте только пакет и те extras, которые реально нужны вашему Django-проекту:

```bash
pip install codex-django
pip install "codex-django[cli]"
pip install "codex-django[admin,observability]"
pip install "codex-django[dev]"
```

Этот режим нужен командам, которые используют runtime-модули `core`, `system`, `booking`, `notifications` и `cabinet`.
Базовая установка намеренно не тянет debug toolbar, admin theme и metrics-пакеты; ставьте `admin` для `django-unfold`,
`observability` для `django-prometheus`, а `dev` для contributor/debug tooling.

## Scaffold Mode

Используйте companion CLI package, когда нужно создать новый проект или добавить в него feature scaffolds:

```bash
pip install "codex-django[cli]"
# или: pip install codex-django-cli
codex-django init myproject
codex-django add-client-cabinet --project myproject
codex-django add-booking --project myproject
codex-django add-notifications --app system --project myproject
```

CLI больше не является частью runtime-дистрибутива.
Его лучше воспринимать как project-construction tooling, которое зависит от `codex-django`, а не как business runtime code внутри того же пакета.

## Contributor Mode

Если вы меняете сам `codex-django`, поднимайте полное development-окружение:

```bash
uv sync --extra maintainer
uv run pytest
uv run mypy src/
uv run pre-commit run --all-files
uv run python tools/dev/check.py --ci
uv build --no-sources
```

## Production Guidance

- generated project code должен жить в вашем application repository;
- scaffolding лучше считать developer-time или build-time активностью;
- production images должны тянуть только те зависимости, которые реально нужны runtime-приложению;
- не завязывайте production container на interactive CLI flows без явной операционной причины.

## Что Читать Дальше

- [Runtime и CLI](./runtime-vs-cli.md) для понимания границы между reusable modules и project-construction tooling.
- [Структура проекта](./project-structure.md) для карты scaffolded проекта.
- [Blueprint workflow](./blueprints-and-scaffolding.md) для связи между CLI-командами и generated output.
