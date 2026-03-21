from __future__ import annotations

import os
import sys

from rich.console import Console

from codex_django.cli import prompts

console = Console()


def main(args: list[str] | None = None) -> int:
    """
    Main entry point for the codex-django CLI.
    """
    # Allow legacy argparse-style invocation: codex-django init <name>
    if args is None:
        args = sys.argv[1:]

    if args:
        return _handle_legacy_args(args)

    return _interactive_menu()


def _interactive_menu() -> int:
    action = prompts.ask_main_action()

    if not action or action == "❌  Exit":
        return 0

    if action == "🚀  Init new project":
        name = prompts.ask_project_name()
        if not name:
            return 0
        from .commands.init import handle_init

        handle_init(name.strip(), os.getcwd())

    elif action == "🧩  Add feature/extension":
        if not os.path.exists("pyproject.toml"):
            console.print("[red]❌ Run from project root (where pyproject.toml is)[/red]")
            return 1

        src_path = os.path.join(os.getcwd(), "src")
        if not os.path.isdir(src_path):
            console.print("[red]❌ No src/ directory found[/red]")
            return 1

        projects = [d for d in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, d))]
        if not projects:
            console.print("[red]❌ No projects found in src/[/red]")
            return 1

        target = prompts.ask_target_project(projects)
        if not target:
            return 0

        feature = prompts.ask_feature()
        if not feature or feature == "← Back":
            return 0

        if feature == "Basic app":
            app_name = prompts.ask_app_name()
            if not app_name:
                return 0
            from .commands.add_app import handle_add_app

            handle_add_app(app_name.strip(), os.path.join(os.getcwd(), "src", target))

        elif feature == "Notifications":
            app_name = prompts.ask_app_name("App name for notifications (default: system):", default="system")
            if not app_name:
                return 0
            from .commands.notifications import handle_add_notifications

            handle_add_notifications(
                app_name.strip(),
                os.path.join(os.getcwd(), "src", target),
            )

    return 0


def _handle_legacy_args(args: list[str]) -> int:
    """Handle legacy argparse-style invocation for scripting/CI."""
    import argparse

    parser = argparse.ArgumentParser(prog="codex-django")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("name")
    init_parser.add_argument("--dir", default=None, dest="target_dir", help="Custom output dir (default: src/<name>)")

    app_parser = subparsers.add_parser("add-app")
    app_parser.add_argument("name")
    app_parser.add_argument("--project", default=None)

    notif_parser = subparsers.add_parser("add-notifications")
    notif_parser.add_argument("--app", default="system")
    notif_parser.add_argument("--arq-dir", default=None, dest="arq_dir")
    notif_parser.add_argument("--project", default=None)

    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    base_dir = os.getcwd()

    if parsed.command == "init":
        from .commands.init import handle_init

        handle_init(parsed.name, base_dir, target_dir=parsed.target_dir)

    elif parsed.command == "add-app":
        project_dir = os.path.join(base_dir, "src", parsed.project) if parsed.project else base_dir
        from .commands.add_app import handle_add_app

        handle_add_app(parsed.name, project_dir)

    elif parsed.command == "add-notifications":
        project_dir = os.path.join(base_dir, "src", parsed.project) if parsed.project else base_dir
        from .commands.notifications import handle_add_notifications

        handle_add_notifications(parsed.app, project_dir, arq_dir=parsed.arq_dir)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
