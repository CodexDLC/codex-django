<!-- DOC_TYPE: INDEX -->

# CLI Architecture Moved

The full CLI architecture documentation now lives in the companion package `codex-django-cli`.

This runtime repository keeps these pages only as migration stubs so old links do not immediately break.

## What Still Exists Here

- temporary compatibility shims under `codex_django.cli`
- runtime modules imported by generated projects
- guide pages that explain how runtime and CLI fit together

## Where To Go Instead

- `codex-django-cli` source for the real implementation
- `codex-django-cli` docs for commands, engine, blueprints, and project generation details
- [Runtime vs CLI](../../guides/runtime-vs-cli.md) for the boundary from the runtime package side
