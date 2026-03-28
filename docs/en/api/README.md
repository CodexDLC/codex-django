<!-- DOC_TYPE: API -->

# API Reference

These pages are generated from the Python source tree via `mkdocstrings`.
They are the English-only technical reference layer of the documentation site.

## Structure

The API reference is split into two layers:

- `Public API` is a curated entrypoint map with stable import paths, examples, and guidance on where each package starts.
- `Internal Modules` contains the full `mkdocstrings` output for the implementation modules where the detailed selector, adapter, mixin, and Redis helper docstrings live.

This keeps the top-level API navigation usable while still making the real source-level documentation discoverable.

## Covered packages

- `codex_django.core`
- `codex_django.system`
- `codex_django.notifications`
- `codex_django.booking`
- `codex_django.cabinet`

The CLI API now lives in the companion package `codex-django-cli`, so it is intentionally not documented from this runtime repository.
Use the pages in this section when you need signatures, class members, and source docstrings instead of the bilingual guide and architecture pages.
