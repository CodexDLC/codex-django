from __future__ import annotations

import os
import sys

from rich.console import Console

from codex_django.cli import prompts

console = Console()


def main(args: list[str] | None = None, forced_project: str | None = None) -> int:
    """
    Main entry point for the codex-django CLI.
    """
    if args is None:
        args = sys.argv[1:]

    # Handle 'menu' subcommand (e.g. from manage.py menu)
    if args and args[0] == "menu":
        args = args[1:]
        if not args:
            return _interactive_menu(forced_project=forced_project)

    if args:
        return _handle_legacy_args(args)

    return _interactive_menu(forced_project=forced_project)


def _is_in_project() -> bool:
    """Check if the current directory is a codex-django scaffolded project root.

    Requires both pyproject.toml and a Django manage.py inside src/<project>/.
    This distinguishes a real user project from the library's own source tree.
    """
    if not os.path.exists("pyproject.toml") or not os.path.isdir("src"):
        return False
    src_path = os.path.join(os.getcwd(), "src")
    try:
        for item in os.listdir(src_path):
            if os.path.isfile(os.path.join(src_path, item, "manage.py")):
                return True
    except OSError:
        pass
    return False


def _interactive_menu(forced_project: str | None = None) -> int:
    if _is_in_project():
        return _project_menu(forced_project=forced_project)
    return _global_menu()


def _global_menu() -> int:
    action = prompts.ask_main_action(is_project=False)
    if action == "🚀  Init new project":
        return _init_wizard()
    return 0


def _init_wizard() -> int:
    """Interactive project init wizard."""
    name = prompts.ask_project_name()
    if not name:
        return 0
    name = name.strip()

    mode = prompts.ask_init_mode()
    if not mode or mode == "← Back":
        return 0

    overwrite = "Force" in mode
    is_custom = "Custom" in mode

    with_cabinet = False
    with_booking = False
    with_notifications = False

    if is_custom:
        modules = prompts.ask_init_modules()
        with_cabinet = "cabinet" in modules
        with_booking = "booking" in modules
        with_notifications = "notifications" in modules

    multilingual = prompts.ask_multilingual()

    from .commands.init import handle_init

    handle_init(
        name,
        os.getcwd(),
        overwrite=overwrite,
        multilingual=multilingual,
        with_cabinet=with_cabinet,
        with_booking=with_booking,
        with_notifications=with_notifications,
    )
    return 0


def _project_menu(forced_project: str | None = None) -> int:
    action = prompts.ask_project_action()

    if not action or action == "❌  Exit":
        return 0

    if action == "🚀  Standard Commands":
        return _handle_standard_commands()

    elif action == "🧩  Scaffolding (Apps/Modules)":
        return _handle_scaffolding(forced_project=forced_project)

    elif action == "🛡  Quality & Tools":
        return _handle_quality_tools()

    elif action == "🏁  Deployment Setup":
        return _handle_deployment_setup(forced_project=forced_project)

    elif action == "⚙️  Security":
        from secrets import token_urlsafe

        key = token_urlsafe(50)
        console.print(f"\n[green]Generated new SECRET_KEY:[/green]\n[bold]{key}[/bold]\n")

    return 0


def _handle_standard_commands() -> int:
    cmd = prompts.ask_standard_command()
    if not cmd or cmd == "← Back":
        return 0

    from .utils import run_django_command

    if cmd == "makemigrations":
        run_django_command(["makemigrations"])
    elif cmd == "migrate":
        run_django_command(["migrate"])
    elif cmd == "createsuperuser":
        run_django_command(["createsuperuser"])
    elif cmd == "shell":
        run_django_command(["shell"])
    elif cmd == "i18n: Generate":
        run_django_command(["makemessages", "-a"])
    elif cmd == "i18n: Compile":
        run_django_command(["compilemessages"])

    return 0


def _handle_scaffolding(forced_project: str | None = None) -> int:
    """Handle choice of what feature to scaffold."""
    src_path = os.path.join(os.getcwd(), "src")

    if forced_project:
        target = forced_project
    else:
        projects = [d for d in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, d))]
        if not projects:
            console.print("[red]❌ No projects found in src/[/red]")
            return 1

        if len(projects) == 1:
            target = projects[0]
        else:
            selected_target = prompts.ask_target_project(projects)
            if not selected_target:
                return 0
            target = selected_target

    feature = prompts.ask_feature()
    if not feature or feature == "← Back":
        return 0

    if feature == "Basic app":
        app_name = prompts.ask_app_name()
        if not app_name:
            return 0
        from .commands.add_app import handle_add_app

        handle_add_app(app_name.strip(), os.path.join(src_path, target))

    elif feature == "Notifications":
        app_name = prompts.ask_app_name("App name for notifications (default: system):", default="system")
        if not app_name:
            return 0
        from .commands.notifications import handle_add_notifications

        handle_add_notifications(
            app_name.strip(),
            os.path.join(src_path, target),
        )

    elif feature == "Client Cabinet":
        from .commands.client_cabinet import handle_add_client_cabinet

        handle_add_client_cabinet(os.path.join(src_path, target))

    elif feature == "Booking (Advanced)":
        from .commands.booking import handle_add_booking

        handle_add_booking(os.path.join(src_path, target))

    return 0


def _handle_quality_tools() -> int:
    opt = prompts.ask_quality_tool()
    if not opt or opt == "← Back":
        return 0

    if opt == "Configure pre-commit":
        from .commands.quality import handle_configure_precommit

        handle_configure_precommit(os.getcwd())
    elif opt == "Run Project Checker":
        console.print("[yellow]Running Project Checker...[/yellow]")
        import subprocess

        # Using --all as it's a developer-friendly interactive default in BaseCheckRunner
        subprocess.run([sys.executable, "tools/dev/check.py", "--all"])  # nosec B603
    return 0


def _handle_deployment_setup(forced_project: str | None = None) -> int:
    opt = prompts.ask_deploy_option()
    if not opt or opt == "← Back":
        return 0

    if opt == "Generate Docker files":
        src_path = os.path.join(os.getcwd(), "src")

        if forced_project:
            target = forced_project
        else:
            projects = [d for d in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, d))]
            if not projects:
                console.print("[red]No projects found in src/ directory.[/red]")
                return 0

            if len(projects) == 1:
                target = projects[0]
            else:
                selected_target = prompts.ask_target_project(projects)
                if not selected_target:
                    return 0
                target = selected_target

        from .commands.deploy import handle_generate_deploy

        handle_generate_deploy(target, os.getcwd())
    return 0


def _handle_legacy_args(args: list[str]) -> int:
    """Handle legacy argparse-style invocation for scripting/CI."""
    import argparse

    from .commands.add_app import handle_add_app
    from .commands.booking import handle_add_booking
    from .commands.client_cabinet import handle_add_client_cabinet
    from .commands.init import handle_init
    from .commands.notifications import handle_add_notifications

    parser = argparse.ArgumentParser(prog="codex-django")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project.")
    subparsers.add_parser("menu", help="Launch interactive menu.")
    init_parser.add_argument("name", help="Name of the project (folder inside src/)")
    init_parser.add_argument(
        "target_dir",
        nargs="?",
        default=None,
        help="Target directory for the project (default: <name>)",
    )
    init_parser.add_argument(
        "--code",
        action="store_true",
        help="Only scaffold the core code (no repo/wrapper files)",
    )
    init_parser.add_argument(
        "--dev",
        action="store_true",
        help="Dev mode: scaffold into sandbox/ inside the library",
    )
    init_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    init_parser.add_argument(
        "--multilingual",
        dest="multilingual",
        action="store_true",
        default=False,
        help="Enable multilingual support",
    )
    init_parser.add_argument(
        "--no-multilingual",
        dest="multilingual",
        action="store_false",
        help="Disable multilingual support (default)",
    )
    init_parser.add_argument("--with-cabinet", action="store_true", default=False)
    init_parser.add_argument("--with-booking", action="store_true", default=False)
    init_parser.add_argument("--with-notifications", action="store_true", default=False)
    init_parser.set_defaults(
        func=lambda args: handle_init(
            name=args.name,
            base_dir=os.getcwd(),
            target_dir=args.target_dir,
            code_only=args.code,
            dev_mode=args.dev,
            overwrite=args.overwrite,
            multilingual=args.multilingual,
            with_cabinet=args.with_cabinet,
            with_booking=args.with_booking,
            with_notifications=args.with_notifications,
        )
    )

    app_parser = subparsers.add_parser("add-app")
    app_parser.add_argument("name")
    app_parser.add_argument("--project", default=None)
    app_parser.set_defaults(
        func=lambda args: handle_add_app(
            args.name,
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
        )
    )

    notif_parser = subparsers.add_parser("add-notifications")
    notif_parser.add_argument("--app", default="system")
    notif_parser.add_argument("--arq-dir", default=None, dest="arq_dir")
    notif_parser.add_argument("--project", default=None)
    notif_parser.set_defaults(
        func=lambda args: handle_add_notifications(
            args.app,
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
            arq_dir=args.arq_dir,
        )
    )

    cab_parser = subparsers.add_parser("add-client-cabinet")
    cab_parser.add_argument("--project", default=None)
    cab_parser.set_defaults(
        func=lambda args: handle_add_client_cabinet(
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
        )
    )

    booking_parser = subparsers.add_parser("add-booking")
    booking_parser.add_argument("--project", default=None)
    booking_parser.set_defaults(
        func=lambda args: handle_add_booking(
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
        )
    )

    parsed = parser.parse_args(args)

    if hasattr(parsed, "func"):
        parsed.func(parsed)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
