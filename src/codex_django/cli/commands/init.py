"""
handle_init
===========
CLI handler for the ``codex-django init <name>`` command.

Scaffolds a new Django project into ./src/<name>/:

  src/<name>/
    manage.py
    core/             – settings, urls, wsgi, asgi, redis, sitemaps
    system/           – SiteSettings, SEO, management commands
    cabinet/          – user dashboard skeleton (theme.css only)
    features/
      main/           – home & contacts views
    templates/        – base.html, includes/, main/, errors/
    static/
      css/            – @import chain + compiler_config.json
      css/cabinet/    – theme.css (white-labeling overrides)
      js/vendor/      – HTMX 2.x, Alpine.js placeholders
      js/app/         – main.js

Usage::

    codex-django init myproject
    codex-django init myproject --dir sandbox   # custom output path
    # or via interactive menu: codex-django → Init new project
"""

from __future__ import annotations

import os

from rich.console import Console

console = Console()


def handle_init(
    name: str,
    base_dir: str,
    target_dir: str | None = None,
    code_only: bool = False,
    dev_mode: bool = False,
    overwrite: bool = False,
    multilingual: bool = False,
    with_cabinet: bool = False,
    with_booking: bool = False,
    with_notifications: bool = False,
) -> None:
    from secrets import token_urlsafe

    from codex_django.cli.engine import CLIEngine

    # 1. Determine project_root and backend_dir
    if dev_mode:
        # Safety check: are we in the library's source?
        # __file__ is in src/codex_django/cli/commands/init.py
        # lib_root should be 4 levels up
        lib_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        pyproject_path = os.path.join(lib_root, "pyproject.toml")
        is_lib_source = False
        if os.path.exists(pyproject_path):
            with open(pyproject_path, encoding="utf-8") as f:
                if 'name = "codex-django"' in f.read():
                    is_lib_source = True

        if not is_lib_source:
            console.print("[red]❌ --dev mode is only available when running from the library's source.[/red]")
            return

        project_root = os.path.join(lib_root, "sandbox")
        backend_dir = os.path.join(project_root, "src", name)
    elif target_dir:
        project_root = os.path.abspath(target_dir)
        backend_dir = os.path.join(project_root, "src", name)
    else:
        # Default: create a new folder with the name
        project_root = os.path.join(base_dir, name)
        backend_dir = os.path.join(project_root, "src", name)

    # 2. Conflict check (look for manage.py)
    if os.path.exists(os.path.join(backend_dir, "manage.py")) and not overwrite:
        console.print(f"[yellow]⚠ Django project already exists in:[/yellow] [bold]{backend_dir}[/bold]")
        console.print("[yellow]  Use --overwrite to re-scaffold.[/yellow]")
        return

    engine = CLIEngine()
    context = {
        "project_name": name,
        "secret_key": token_urlsafe(50),
        "multilingual": multilingual,
        "with_cabinet": with_cabinet,
        "with_booking": with_booking,
        "with_notifications": with_notifications,
    }

    # 3. Scaffolding logic
    if not code_only:
        # Repo-level files (.gitignore, pyproject, README, .env.example, etc.)
        engine.scaffold("repo", target_dir=project_root, context=context, overwrite=overwrite)
        # Deploy files go into deploy/<name>/ so multiple projects can share one repo
        deploy_dir = os.path.join(project_root, "deploy", name)
        engine.scaffold("deploy", target_dir=deploy_dir, context=context, overwrite=overwrite)

    # Scaffolding the Django core (project blueprint) into backend_dir
    engine.scaffold("project", target_dir=backend_dir, context=context, overwrite=overwrite)

    # 3b. Feature blueprints
    if with_cabinet:
        engine.scaffold("features/client_cabinet", target_dir=backend_dir, context=context)
        console.print("[green]  ✓[/green] Client Cabinet scaffolded")

    if with_booking:
        engine.scaffold("features/booking", target_dir=backend_dir, context=context)
        console.print("[green]  ✓[/green] Booking (Advanced) scaffolded")

    if with_notifications:
        engine.scaffold(
            "features/notifications/feature", target_dir=backend_dir, context={**context, "app_name": "system"}
        )
        engine.scaffold("features/notifications/arq", target_dir=backend_dir, context={**context, "app_name": "system"})
        console.print("[green]  ✓[/green] Notifications scaffolded")

    # 4. Success message and instructions
    console.print()
    if dev_mode:
        console.print(f"[green]✓[/green] [bold]DEV MODE:[/bold] Scaffolded into [bold]{project_root}[/bold]")
    elif code_only:
        console.print(f"[green]✓[/green] Core code [bold]{name}[/bold] injected into [bold]{backend_dir}[/bold]")
    else:
        modules = ["base project"]
        if with_cabinet:
            modules.append("cabinet")
        if with_booking:
            modules.append("booking")
        if with_notifications:
            modules.append("notifications")
        console.print(f"[green]✓[/green] Project [bold]{name}[/bold] initialized in [bold]{project_root}[/bold]")
        console.print(f"  Modules: [cyan]{', '.join(modules)}[/cyan]")

    console.print()
    console.print("[bold]Next steps:[/bold]")

    step = 1
    curr_dir_abs = os.path.abspath(os.getcwd())
    proj_root_abs = os.path.abspath(project_root)

    if not dev_mode and proj_root_abs != curr_dir_abs:
        console.print(f"  {step}. [cyan]cd {os.path.basename(proj_root_abs)}[/cyan]")
        step += 1

    if not code_only and not dev_mode:
        console.print(f"  {step}. [cyan]python -m venv .venv[/cyan]")
        step += 1
        console.print(f"  {step}. [cyan]source .venv/bin/activate[/cyan] (or .venv\\Scripts\\activate)")
        step += 1
        console.print(f"  {step}. [cyan]pip install -e .[/cyan]")
        step += 1
        console.print(f"  {step}. [cyan]cp .env.example .env[/cyan]")
        step += 1

    if not dev_mode:
        # Use relative path for manage.py if possible
        target = project_root if proj_root_abs != curr_dir_abs else "."
        manage_py_rel = os.path.relpath(os.path.join(backend_dir, "manage.py"), target)
        console.print(f"  {step}. [cyan]python {manage_py_rel} migrate[/cyan]")
        step += 1
        console.print(f"  {step}. [cyan]python {manage_py_rel} runserver[/cyan]")
    else:
        # Dev mode instructions are simpler
        console.print(f"  {step}. Run tests or check the structures in [bold]sandbox/[/bold]")
