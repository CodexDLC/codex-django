<!-- DOC_TYPE: GUIDE -->

# Installation Modes

## Choose The Smallest Install That Matches The Job

Use `codex-django` in one of three practical modes:

1. Runtime library mode for projects that only need reusable Django modules.
2. Scaffold mode for developers generating or extending a Codex-shaped project with `codex-django-cli`.
3. Full contributor mode for people changing the library itself.

## Runtime Library Mode

Install only the package and the extras your Django project actually uses:

```bash
pip install codex-django
pip install "codex-django[cli]"
pip install "codex-django[dev]"
```

This mode is for teams consuming the runtime modules such as `core`, `system`, `booking`, `notifications`, and `cabinet`.

## Scaffold Mode

Use the companion CLI package when you want to generate a new project or add feature scaffolds to an existing one:

```bash
pip install "codex-django[cli]"
# or: pip install codex-django-cli
codex-django init myproject
codex-django add-client-cabinet --project myproject
codex-django add-booking --project myproject
codex-django add-notifications --app system --project myproject
```

The CLI is no longer part of the runtime distribution.
Treat it as project-construction tooling that depends on `codex-django`, not as business runtime code bundled into the same package.

## Contributor Mode

When you are changing `codex-django` itself, sync the full development environment:

```bash
uv sync --extra dev
uv run pytest
uv run mypy src/
uv run pre-commit run --all-files
uv build --no-sources
```

## Production Guidance

- Put generated project code into your application repository.
- Treat scaffolding as a build-time or developer-time activity.
- Keep production images focused on the dependencies your runtime application actually needs.
- Avoid making the deployed app container depend on interactive CLI flows unless that is an explicit operational choice.

## Where To Go Next

- Read [Runtime vs CLI](./runtime-vs-cli.md) for the boundary between reusable modules and project-construction tooling.
- Read [Project Structure](./project-structure.md) for the layout of a scaffolded project.
- Read [Blueprint Workflow](./blueprints-and-scaffolding.md) for how CLI commands map to generated output.
