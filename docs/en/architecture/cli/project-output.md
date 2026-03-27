<!-- DOC_TYPE: CONCEPT -->

# CLI Project Output

## Purpose

This page describes the architectural shape of the project that `codex_django.cli` generates.
It is not about how the CLI works internally.
It is about what appears on disk after the main scaffold flow runs.

That distinction matters because the generated project is the actual product the CLI delivers.
If blueprints are the source material and `CLIEngine` is the executor, project output is the resulting architecture developers will live inside.

## Two Output Levels

The CLI produces output on two different levels:

- repository level
- Django project level

These should not be confused.

### Repository Level

At the repository root, CLI can generate the outer project shell:

- `pyproject.toml`
- `README.md`
- `.env.example`
- `.gitignore`
- repo docs and tools
- deployment files under `deploy/<project_name>/`

This is the operational and packaging layer around the generated application.

### Django Project Level

Inside `src/<project_name>/`, CLI generates the runtime Django project itself.
This is the codebase that actually becomes the application's backend structure.

## Base Generated Runtime Structure

The base project blueprint currently generates a structure centered around these main areas:

- `manage.py`
- `core/`
- `system/`
- `cabinet/`
- `features/`
- `templates/`
- `static/`

This already tells us something important:
the generated project is not a blank Django app.
It is opinionated from the start.

## Meaning Of The Main Output Folders

### `core/`

`core/` is the project's framework and settings layer.
It contains:

- settings packages
- urls
- wsgi/asgi entrypoints
- logging/redis helpers
- sitemap wiring

This is the runtime control center of the generated project.

### `system/`

`system/` is the project-state and administrative data layer.
In the generated output it is responsible for:

- site settings
- SEO models/admin
- static content
- management command support
- error view support

This matches the reusable `system` concepts already present in the library itself.

### `cabinet/`

`cabinet/` appears in the generated project as a minimal shell around the reusable cabinet framework.
It does not duplicate the full library implementation.
Instead, it provides project-local glue and customization points such as:

- local cabinet registration
- minimal selectors/views
- theme and override surface

This is important because cabinet is meant to stay library-driven while still allowing project-level adaptation.

### `features/`

`features/` is the extensibility area of the generated project.
The base project already includes `features/main/`, which acts as the starter feature module for public pages like home and contacts.

Later CLI commands can grow this area with:

- standard apps
- feature bundles

So `features/` is the main growth surface of the scaffolded project.

### `templates/`

`templates/` contains shared project templates such as:

- the base layout
- includes
- public pages
- error pages

This layer defines the shared rendering surface of the generated project.
It is distinct from the library-owned `cabinet` templates and from showcase templates.

### `static/`

`static/` contains the front-end asset structure for the generated project.
Notably, it already has a layered CSS setup and compiler configuration, which means front-end organization is also scaffolded as an architectural choice rather than left entirely ad hoc.

## Optional Output Expansion

The base project can be expanded at generation time with optional modules such as:

- cabinet
- booking
- notifications

These do not simply add one folder each.
They may inject files into multiple target areas.

Examples:

- booking expands runtime code, templates, cabinet integration, and system configuration
- notifications adds feature code and ARQ-related infrastructure
- client cabinet extends cabinet and system-side user profile handling

So generated output is layered:

1. base project shell
2. optional feature bundles
3. later incremental scaffold commands

## Generated Project As Architecture

The key architectural point is this:
the CLI does not generate a neutral Django skeleton.
It generates a codex-django-shaped project with explicit assumptions about:

- where core settings live
- where admin/system state lives
- how features are organized
- how public templates are separated from cabinet UI
- how deploy support is layered around the project

That is why project output deserves its own documentation page.

## Runtime Flow

```mermaid
flowchart TD
    A["CLI init command"] --> B["repo blueprints"]
    A --> C["project blueprints"]
    A --> D["optional feature blueprints"]
    B --> E["repository shell"]
    C --> F["src/<project_name>/ runtime structure"]
    D --> F
    F --> G["core/system/cabinet/features/templates/static"]
```

## Relationship To Other CLI Pages

- `blueprints.md` explains the source families that define this output
- `engine.md` explains how the output is materialized
- `commands.md` explains which actions create or extend this output

This page is the "what you end up with" view of the CLI architecture.

## See Also

- [CLI index](/C:/install/projects/codex_tools/codex-django/docs/en/architecture/cli/index.md)
- [CLI blueprints](/C:/install/projects/codex_tools/codex-django/docs/en/architecture/cli/blueprints.md)
- [CLI commands](/C:/install/projects/codex_tools/codex-django/docs/en/architecture/cli/commands.md)
