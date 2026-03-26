"""
Thin wrappers around questionary prompts.

Isolated here so tests can mock `codex_django.cli.prompts.*`
instead of patching questionary directly.
"""

from __future__ import annotations

from typing import cast

import questionary


def ask_main_action(is_project: bool = False) -> str | None:
    choices = [
        "🚀  Init new project",
        "🧩  Add feature/extension",
        "❌  Exit",
    ]
    if is_project:
        # In a project, we don't usually need to 'init' a new one from the same root
        # but we'll use a better sub-menu instead
        pass

    return cast(
        str | None,
        questionary.select(
            "Codex Django CLI",
            choices=choices,
        ).ask(),
    )


def ask_project_action() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Codex Project Menu",
            choices=[
                "🚀  Standard Commands",
                "🧩  Scaffolding (Apps/Modules)",
                "🛡  Quality & Tools",
                "🏁  Deployment Setup",
                "⚙️  Security",
                "❌  Exit",
            ],
        ).ask(),
    )


def ask_standard_command() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Standard Commands",
            choices=[
                "makemigrations",
                "migrate",
                "createsuperuser",
                "shell",
                "i18n: Generate",
                "i18n: Compile",
                "← Back",
            ],
        ).ask(),
    )


def ask_quality_tool() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Quality & Tools",
            choices=[
                "Configure pre-commit",
                "Run Project Checker",
                "← Back",
            ],
        ).ask(),
    )


def ask_deploy_option() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Deployment Setup",
            choices=[
                "Generate Docker files",
                "← Back",
            ],
        ).ask(),
    )


def ask_project_name() -> str | None:
    return cast(str | None, questionary.text("Project name (snake_case):").ask())


def ask_target_project(projects: list[str]) -> str | None:
    return cast(str | None, questionary.select("Select target project:", choices=projects).ask())


def ask_feature() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Add feature:",
            choices=["Basic app", "Notifications", "Client Cabinet", "Booking (Advanced)", "← Back"],
        ).ask(),
    )


def ask_app_name(prompt: str = "App name (snake_case):", default: str = "") -> str | None:
    return cast(str | None, questionary.text(prompt, default=default).ask())


def ask_init_mode() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Init type:",
            choices=[
                "⚡  Standard",
                "🧩  Custom (choose modules)",
                questionary.Separator(),
                "🔄  Force reinit — Standard",
                "🔄  Force reinit — Custom",
                questionary.Separator(),
                "← Back",
            ],
        ).ask(),
    )


def ask_init_modules() -> list[str]:
    result = questionary.checkbox(
        "Modules to include:",
        choices=[
            questionary.Choice("Client Cabinet (user portal)", value="cabinet", checked=True),
            questionary.Choice("Booking (Advanced)", value="booking", checked=False),
            questionary.Choice("Notifications (email / ARQ)", value="notifications", checked=False),
        ],
    ).ask()
    return result or []


def ask_multilingual() -> bool:
    result = questionary.confirm("Enable multilingual support?", default=False).ask()
    return bool(result)
