"""
handle_init
===========
CLI handler for the ``codex-django init <name>`` command.

Scaffolds a new Django project into ./src/<name>/:

  src/<name>/
    manage.py
    core/           – settings, urls, wsgi, asgi, redis, sitemaps
    features/
      system/       – SiteSettings, SEO, management commands
      cabinet/      – user dashboard (skeleton)

Usage::

    codex-django init myproject
    # or via interactive menu: codex-django → Init new project
"""

from __future__ import annotations

import os

from rich.console import Console

console = Console()


def handle_init(name: str, base_dir: str, target_dir: str | None = None) -> None:
    from codex_django.cli.engine import CLIEngine

    if target_dir is None:
        target_dir = os.path.join(base_dir, "src", name)

    if os.path.exists(target_dir):
        console.print(f"[yellow]⚠ Directory already exists:[/yellow] [bold]{target_dir}[/bold]")
        console.print("[yellow]  Use --overwrite flag or remove the directory first.[/yellow]")
        return

    engine = CLIEngine()
    context = {"project_name": name}

    engine.scaffold("project", target_dir=target_dir, context=context)

    console.print()
    console.print(f"[green]✓[/green] Project [bold]{name}[/bold] scaffolded → [bold]src/{name}/[/bold]")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. [cyan]cd src/{name}[/cyan]")
    console.print("  2. [cyan]pip install -r requirements.txt[/cyan]  (if present)")
    console.print("  3. Copy [cyan].env.example[/cyan] → [cyan].env[/cyan] and fill in the values")
    console.print("  4. [cyan]python manage.py migrate[/cyan]")
    console.print("  5. [cyan]python manage.py menu[/cyan]  ← interactive management")
