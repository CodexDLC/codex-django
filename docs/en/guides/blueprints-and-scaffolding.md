<!-- DOC_TYPE: GUIDE -->

# Blueprint Workflow

## How Scaffold Commands Work

Every major `codex-django-cli` command translates a developer intention into one or more blueprint renders.

Typical flow:

1. Choose a command such as `init`, `add-client-cabinet`, `add-booking`, or `add-notifications`.
2. The command resolves the relevant blueprint family.
3. `CLIEngine` renders templates and copies static assets into the target project.
4. The command prints follow-up integration steps you still need to apply manually.

## Blueprint Families

The CLI blueprint tree in `codex-django-cli` is organized by the kind of output it creates:

- `repo` for repository shell files
- `project` for the base Django project layout
- `apps` for app-level building blocks
- `features` for cross-cutting functional bundles
- `deploy` for operational and deployment-oriented output

## Safe Working Pattern

Use this order whenever you scaffold new functionality:

1. Generate the files.
2. Read the printed follow-up instructions.
3. Wire settings, admin, URLs, and migrations.
4. Run local checks before continuing.

## Why This Matters

`codex-django` is the runtime package consumed by generated projects.
`codex-django-cli` owns project construction, but the blueprint workflow still matters here because generated code intentionally imports `codex_django.*` modules from the runtime package.

## Related Pages

- [Getting Started](../getting-started.md)
- [Project Structure](./project-structure.md)
