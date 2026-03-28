<!-- DOC_TYPE: GUIDE -->

# Getting Started

## Install The Library

Choose the smallest dependency set that matches your project:

```bash
pip install codex-django
pip install "codex-django[notifications]"
pip install "codex-django[django-redis]"
pip install "codex-django[all]"
```

`codex-django` requires Python 3.12+ and Django 5+.

## Scaffold A New Project

Project scaffolding lives in the companion package `codex-django-cli`:

```bash
pip install codex-django-cli
codex-django init myproject
cd myproject
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python src/myproject/manage.py migrate
python src/myproject/manage.py runserver
```

The interactive entrypoint is also available through that companion package:

```bash
codex-django
```

That menu is useful when you want to choose i18n mode, language codes, or optional modules without memorizing flags.

## Add Optional Modules Later

If you already have a scaffolded project, extend it incrementally through `codex-django-cli`:

```bash
codex-django add-client-cabinet --project myproject
codex-django add-booking --project myproject
codex-django add-notifications --app system --project myproject
```

Each command scaffolds files and then prints the project-specific follow-up steps you need to wire into settings, admin, migrations, and URLs.

## Typical Development Loop

```bash
uv sync --extra dev
uv run pytest
uv run mypy src/
uv run python tools/dev/check.py --lint
uv build --no-sources
```

## Where To Go Next

- Read the architecture section if you need module boundaries and design rationale.
- Read the module guides if you want practical setup checklists.
- Read the API reference if you already know which package you need to import.
