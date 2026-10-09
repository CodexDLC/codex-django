<!-- DOC_TYPE: GUIDE -->

# Быстрый старт

## Установка библиотеки

Выбирайте минимальный набор зависимостей под ваш проект:

```bash
pip install codex-django
pip install "codex-django[cli]"
pip install "codex-django[dev]"
```

`codex-django` требует Python 3.12+ и Django 5+.

## Создание нового проекта

Генерация проекта теперь живет в companion package `codex-django-cli`:

```bash
pip install "codex-django[cli]"
# или: pip install codex-django-cli
codex-django init myproject
cd myproject
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python src/myproject/manage.py migrate
python src/myproject/manage.py runserver
```

Интерактивный entrypoint также приходит из этого companion package:

```bash
codex-django
```

Меню особенно удобно, если вы хотите выбрать i18n-режим, коды языков и optional modules без запоминания флагов.

## Подключение модулей позже

Выбирайте дополнительные модули через интерактивное меню companion-пакета CLI:

```bash
codex-django menu
```

Для нового проекта можно выбрать модули командой `codex-django init myproject --with-booking --with-messaging`. Проверьте созданные файлы и инструкции перед подключением settings, admin, migrations и URLs. Существующие файлы пропускаются, если перезапись явно не выбрана.

## Типичный цикл разработки

```bash
uv sync --extra dev
uv run pytest
uv run mypy src/
uv run python tools/dev/check.py --lint
uv build --no-sources
```

## Что читать дальше

- Архитектурный раздел, если нужна карта модулей и их границ.
- Гайды по модулям, если нужны практические шаги подключения.
- API reference, если вы уже знаете, какой пакет хотите импортировать.
