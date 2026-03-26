"""
handle_add_client_cabinet
=========================
CLI handler for the ``codex-django add-client-cabinet`` command.

Scaffolds client cabinet infrastructure into the target project:

  cabinet/
    adapters.py
    views/client.py
    templates/cabinet/client/
      profile.html
      my_appointments.html
      settings.html
      settings_notifications.html
      settings_privacy.html

  system/models/
    user_profile.py

Usage (from project root)::

    codex-django add-client-cabinet --project myapp
"""

from __future__ import annotations

from typing import Any

from rich.console import Console

console = Console()


def handle_add_client_cabinet(project_dir: str) -> None:
    from codex_django.cli.engine import CLIEngine

    engine = CLIEngine()
    context: dict[str, Any] = {}

    engine.scaffold("features/client_cabinet", target_dir=project_dir, context=context)
    console.print("[green]✓[/green] Client cabinet scaffolded → [bold]cabinet/ + system/[/bold]")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. In [cyan]core/settings/modules/codex.py[/cyan] uncomment the 3 client cabinet lines:")
    console.print('       [green]ACCOUNT_ADAPTER = "cabinet.adapters.CabinetAccountAdapter"[/green]')
    console.print('       [green]CABINET_DEFAULT_URL = "/cabinet/"[/green]')
    console.print('       [green]CABINET_CLIENT_URL  = "/cabinet/my/"[/green]')
    console.print("  2. Add client URL patterns to [cyan]cabinet/urls.py[/cyan]:")
    console.print('       [dim]path("my/", my_appointments_view, name="my_appointments"),[/dim]')
    console.print('       [dim]path("my/profile/", profile_view, name="profile"),[/dim]')
    console.print('       [dim]path("my/settings/", settings_view, name="settings"),[/dim]')
    console.print(
        '       [dim]path("my/settings/notifications/", '
        'settings_notifications_view, name="settings_notifications"),[/dim]'
    )
    console.print('       [dim]path("my/settings/privacy/", settings_privacy_view, name="settings_privacy"),[/dim]')
    console.print("  3. Add to [cyan]system/models/__init__.py[/cyan]:")
    console.print("       [dim]from .user_profile import UserProfile[/dim]")
    console.print("  4. Run [cyan]python manage.py makemigrations && migrate[/cyan]")
