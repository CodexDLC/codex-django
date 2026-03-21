"""
Thin wrappers around questionary prompts.

Isolated here so tests can mock `codex_django.cli.prompts.*`
instead of patching questionary directly.
"""

from __future__ import annotations

from typing import cast

import questionary


def ask_main_action() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Codex Django CLI",
            choices=[
                "🚀  Init new project",
                "🧩  Add feature/extension",
                "❌  Exit",
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
            choices=["Basic app", "Notifications", "← Back"],
        ).ask(),
    )


def ask_app_name(prompt: str = "App name (snake_case):", default: str = "") -> str | None:
    return cast(str | None, questionary.text(prompt, default=default).ask())
