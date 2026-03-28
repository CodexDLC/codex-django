<!-- DOC_TYPE: API -->

# CLI Public API Moved

The public CLI API is no longer documented from the `codex-django` runtime repository.
It now lives in the companion package `codex-django-cli`.

## What Remains Here

- Temporary compatibility shims still exist under `codex_django.cli`.
- Those shims are provided only to ease migration for callers that have not yet switched imports.
- The long-term implementation home of the CLI is `codex_django_cli.*`.

## Migration Direction

- Prefer the package-level command entrypoint from `codex-django-cli`.
- Prefer source and docs in the `codex-django-cli` repository for engine, prompts, commands, and blueprint details.
- Treat `codex_django.cli.*` in this repository as compatibility surface, not runtime API.
