<!-- DOC_TYPE: CONCEPT -->

# CLI Module Moved

`codex_django.cli` is no longer implemented in this runtime repository.

The real CLI module now lives in `codex-django-cli`, while `codex-django` only keeps compatibility shims under `codex_django.cli` for migration.

## Runtime-Side Takeaway

Generated projects still import runtime modules from `codex_django.*`.
That runtime dependency is why CLI and runtime remain related even after the split.

## See Also

- [CLI Architecture Moved](./README.md)
- [Runtime vs CLI](../../guides/runtime-vs-cli.md)
