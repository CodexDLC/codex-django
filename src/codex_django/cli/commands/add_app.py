"""
handle_add_app
==============
CLI handler for adding a new feature/app to an existing project.

Scaffolds the default app blueprint into:

  <project_dir>/features/<app_name>/

Usage::

    codex-django add-app myfeature --project myproject
    # or via interactive menu: codex-django → Add feature/extension → Basic app
"""

from __future__ import annotations

import os

from rich.console import Console

console = Console()


def handle_add_app(app_name: str, project_dir: str) -> None:
    from codex_django.cli.engine import CLIEngine

    target_dir = os.path.join(project_dir, "features", app_name)

    if os.path.exists(target_dir):
        console.print(f"[yellow]⚠ App already exists:[/yellow] [bold]{target_dir}[/bold]")
        return

    engine = CLIEngine()
    context = {"app_name": app_name}

    engine.scaffold("apps/default", target_dir=target_dir, context=context)

    console.print()
    console.print(f"[green]✓[/green] App [bold]{app_name}[/bold] scaffolded → [bold]features/{app_name}/[/bold]")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(
        f'  1. Add [cyan]"features.{app_name}"[/cyan] to [cyan]LOCAL_APPS[/cyan] '
        f"in [cyan]core/settings/modules/apps.py[/cyan]"
    )
    console.print("  2. Add URL include to [cyan]core/urls.py[/cyan]:")
    console.print(f'     [cyan]path("{app_name}/", include("features.{app_name}.urls")),[/cyan]')
    console.print("  3. [cyan]python manage.py makemigrations[/cyan]")
    console.print("  4. [cyan]python manage.py migrate[/cyan]")
