<!-- DOC_TYPE: GUIDE -->

# Runtime vs CLI

## The Two Packages In The Split

The Codex Django tooling now lives in two related packages:

- `codex-django` for runtime modules imported by Django projects after installation.
- `codex-django-cli` for CLI/scaffolding tooling that creates or extends those projects.

Understanding that split keeps production dependencies smaller and makes the repository boundary easier to reason about.

## Runtime Layer

The runtime layer is what your Django app imports and executes:

- `codex_django.core`
- `codex_django.system`
- `codex_django.notifications`
- `codex_django.booking`
- `codex_django.cabinet`

These modules define reusable models, mixins, selectors, adapters, Redis helpers, templates, and integration points.

## CLI Package

The CLI package is what developers use to create and evolve project structure:

- `codex_django_cli.main`
- command handlers under `codex_django_cli.commands`
- blueprint trees under `codex_django_cli.blueprints`
- rendering logic in `codex_django_cli.engine`

This package is about generation, orchestration, and project assembly.
Generated code may still import `codex_django.*`, which is expected because blueprints target the runtime package.

## How To Think About The Boundary

- Runtime code stays in the long-lived application path of the generated project.
- CLI code runs before or around that runtime path to create files, wiring, and defaults.
- Generated output becomes your project's codebase and can then evolve independently.
- Temporary compatibility shims remain under `codex_django.cli`, but they are not the long-term implementation home of the CLI.

## Practical Rule

If the question is "what does my Django app import at runtime?", stay in the runtime modules.
If the question is "what command creates or extends this structure?", move into `codex-django-cli` documentation and source.

## Related Pages

- [Getting Started](../getting-started.md)
- [Installation Modes](./installation-modes.md)
- [Project Structure](./project-structure.md)
