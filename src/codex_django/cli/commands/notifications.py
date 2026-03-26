"""
handle_add_notifications
========================
CLI handler for the ``codex-django add-notifications`` command.

Scaffolds notification infrastructure into the target project:

  features/{app_name}/
    models/email_content.py
    selectors/email_content.py
    services/notification.py
  core/arq/
    client.py

Usage (from project root)::

    codex-django add-notifications --app system
    codex-django add-notifications --app system --arq-dir myapp/arq
"""

from __future__ import annotations

import os

from rich.console import Console

console = Console()


def handle_add_notifications(app_name: str, base_dir: str, arq_dir: str | None = None) -> None:
    from codex_django.cli.engine import CLIEngine

    engine = CLIEngine()
    context = {"app_name": app_name}

    # --- Feature files ---
    feature_target = os.path.join(base_dir, "features", app_name)
    engine.scaffold("features/notifications/feature", target_dir=feature_target, context=context)
    console.print(f"[green]✓[/green] Notification feature scaffolded → [bold]features/{app_name}/[/bold]")

    # --- ARQ client ---
    arq_target = os.path.join(base_dir, arq_dir) if arq_dir else os.path.join(base_dir, "core", "arq")
    engine.scaffold("features/notifications/arq", target_dir=arq_target, context=context)
    arq_rel = arq_dir or "core/arq"
    console.print(f"[green]✓[/green] ARQ client scaffolded → [bold]{arq_rel}/[/bold]")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. Add [cyan]EmailContent[/cyan] to your admin in features/{app_name}/")
    console.print("  2. Run [cyan]python manage.py makemigrations[/cyan]")
    console.print("  3. Set [cyan]ARQ_REDIS_URL[/cyan] in your Django settings")
    console.print("  4. Add event methods to [cyan]NotificationService[/cyan]")
