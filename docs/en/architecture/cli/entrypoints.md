<!-- DOC_TYPE: CONCEPT -->

# CLI Entrypoints

## Purpose

This page explains how users actually enter the CLI system.
If `commands` define the semantic operations and `engine` performs generation, entrypoints define how control reaches those layers in the first place.

In `codex_django.cli`, entrypoints are more important than they first appear because the tool supports multiple interaction modes:

- direct CLI invocation
- interactive menu mode
- scripted subcommand mode
- project-local invocation through generated `manage.py`

So the entrypoint layer is not just a thin wrapper.
It defines the CLI's operating modes.

## Main Entry Gateway

`main.py` is the central gateway of the CLI.
Its top-level `main()` function decides which path to take based on the incoming arguments and the current working context.

At a high level it distinguishes between:

- no args: launch interactive behavior
- `menu`: force interactive menu behavior
- legacy args: parse subcommands

This already tells us something architectural:
the CLI is designed to be usable both as a guided interactive tool and as a scriptable command-line utility.

## Context-Sensitive Entry

One of the most important pieces in the entrypoint layer is `_is_in_project()`.
This function checks whether the current working directory looks like a scaffolded codex-django project.

That means the same CLI binary can change behavior depending on where it is launched:

- outside a project: global menu
- inside a generated project: project menu

This creates a dual operating model:

- global project creation mode
- local project maintenance and extension mode

## Interactive Entrypoints

When the CLI enters interactive mode, `main.py` routes into menu-based flows such as:

- global initialization
- project commands
- scaffolding menus
- quality/deploy/security menus

The important point is that menus are not the CLI itself.
They are one entry mode into the command system.

This design keeps the interaction layer replaceable while leaving command semantics stable underneath.

## Legacy / Scripted Entrypoints

The `_handle_legacy_args()` branch exposes classic argparse-driven command access.
This path supports direct subcommands such as:

- `init`
- `add-app`
- `add-notifications`
- `add-client-cabinet`
- `add-booking`

This matters for automation and CI-style usage.
It means the CLI is not locked into human-driven menu flows.

Architecturally, this makes the tool hybrid:

- human-friendly in interactive mode
- automation-friendly in scripted mode

## Project-Local Entry Through Generated `manage.py`

One of the most interesting entrypoints is not in the CLI package itself, but in the generated project output.

The scaffolded `manage.py` intercepts:

- empty invocation
- `menu`

and redirects those cases into `codex_django.cli.main`.

This effectively embeds the CLI into the generated project lifecycle.
The project is not only created by the CLI; it can continue to expose the CLI as a local maintenance surface after generation.

That is a strong architectural choice.
It turns the CLI into an ongoing project companion, not just a one-time bootstrap tool.

## Operating Model

Putting these pieces together, the entrypoint system follows this model:

1. determine invocation mode
2. determine whether current context is global or project-local
3. route into menu or scripted command handling
4. hand control to command handlers

This means entrypoints are responsible for mode selection, not for business logic.

## Runtime Flow

```mermaid
flowchart TD
    A["User runs codex-django or manage.py"] --> B["main.py or generated manage.py bridge"]
    B --> C["detect args and context"]
    C --> D["interactive menu path"]
    C --> E["legacy subcommand path"]
    D --> F["project menu or global menu"]
    F --> G["command handlers"]
    E --> G
```

## Why Entrypoints Deserve Separate Documentation

Without documenting entrypoints, the CLI can look simpler than it really is.
But the entrypoint layer is where several key architectural promises are enforced:

- one tool can work globally and inside a project
- interactive UX and scripted UX can coexist
- generated projects stay connected to the CLI after scaffold

Those are not implementation details.
They are part of the CLI's product design.

## Relationship To Other CLI Layers

- `prompts.py` supports the interactive branch once an entrypoint selects menu mode
- `commands/` takes over after the entrypoint has decided which action should run
- `engine.py` is reached only after entry routing is complete

So entrypoints sit above all the other CLI layers:
they do not perform generation, but they decide how generation becomes reachable.

## See Also

- [CLI index](/C:/install/projects/codex_tools/codex-django/docs/en/architecture/cli/index.md)
- [CLI commands](/C:/install/projects/codex_tools/codex-django/docs/en/architecture/cli/commands.md)
- [CLI project output](/C:/install/projects/codex_tools/codex-django/docs/en/architecture/cli/project-output.md)
