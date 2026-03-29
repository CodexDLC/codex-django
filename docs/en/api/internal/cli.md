<!-- DOC_TYPE: API -->

# CLI Internal Modules Moved

Internal CLI modules are intentionally no longer autodocumented from the `codex-django` runtime repository.
The real implementation lives in `codex-django-cli`.

## Why This Page Is A Stub

- `codex_django` should remain buildable and documentable as a standalone runtime package.
- Depending on a sibling checkout of `codex-django-cli` makes docs and CI brittle.
- Compatibility shims under `codex_django.cli` remain for migration only.

## Where To Look Instead

- `codex_django_cli.main`
- `codex_django_cli.engine`
- `codex_django_cli.prompts`
- `codex_django_cli.commands.*`
