<!-- DOC_TYPE: GUIDE -->

# Project Structure

## What The CLI Produces

After `codex-django init` via `codex-django-cli`, you work in a generated Django project that has two major layers:

1. Repository-level files such as dependency metadata, CI, docs, and deployment assets.
2. Runtime project code under `src/<project_name>/`.

## Runtime Project Layout

Inside `src/<project_name>/`, the generated project usually grows around these zones:

- project settings and entrypoints
- shared system/state apps
- feature apps added later through scaffold commands
- templates, static assets, and cabinet integration
- operational helpers such as admin wiring, URLs, and background-task integration

## How Feature Scaffolds Fit In

Incremental commands such as booking, notifications, and cabinet do not just add one file.
They usually touch several layers together:

- app registration
- models or settings models
- admin wiring
- URLs and templates
- cabinet integration or selectors

That is why the follow-up checklist printed by each CLI command matters.

## How To Read The Docs Alongside The Structure

- Use the guide layer for "where should I put this next?" questions.
- Use architecture pages for "why is the project split this way?" questions.
- Use API reference only when you already know which package or module you need.

## Related Pages

- [Blueprint Workflow](./blueprints-and-scaffolding.md)
- [Booking Guide](./booking.md)
- [Cabinet Guide](./cabinet.md)
