"""
handle_add_booking
==================
CLI handler for the ``codex-django add-booking`` command.

Scaffolds booking infrastructure into the target project:

  booking/
    __init__.py
    apps.py
    admin.py
    models.py
    selectors.py
    views.py
    urls.py
    wiki.md

  system/
    models/booking_settings.py
    admin/booking_settings.py

  cabinet/
    views/booking.py
    templates/cabinet/booking/my_bookings.html

  templates/booking/
    booking_page.html
    partials/
      step_service.html
      step_date.html
      step_time.html
      step_confirm.html

Usage (from project root)::

    codex-django add-booking --project myapp
"""

from __future__ import annotations

from typing import Any

from rich.console import Console

console = Console()


def handle_add_booking(project_dir: str) -> None:
    from codex_django.cli.engine import CLIEngine

    engine = CLIEngine()
    context: dict[str, Any] = {}

    engine.scaffold("features/booking", target_dir=project_dir, context=context)
    console.print("[green]✓[/green] Booking scaffolded → [bold]booking/ + system/ + cabinet/ + templates/[/bold]")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print()

    console.print("[bold yellow]  ─── If you use codex-django project blueprint ───[/bold yellow]")
    console.print("  1. В [cyan]core/settings/modules/apps.py[/cyan] добавь в [cyan]LOCAL_APPS[/cyan]:")
    console.print('       [dim]"booking",[/dim]')
    console.print("  2. В [cyan]system/models/__init__.py[/cyan] добавь:")
    console.print("       [dim]from .booking_settings import BookingSettings[/dim]")
    console.print("  3. В [cyan]system/admin/__init__.py[/cyan] добавь:")
    console.print("       [dim]from . import booking_settings  # noqa[/dim]")
    console.print()

    console.print("[bold yellow]  ─── If you have your own project ───[/bold yellow]")
    console.print("  1. В [cyan]settings.py[/cyan] добавь в [cyan]INSTALLED_APPS[/cyan]:")
    console.print('       [dim]"booking",[/dim]')
    console.print("  2. В [cyan]system/models/__init__.py[/cyan] добавь:")
    console.print("       [dim]from .booking_settings import BookingSettings[/dim]")
    console.print("  3. Зарегистрируй admin из [cyan]system/admin/booking_settings.py[/cyan] в своём admin")
    console.print()

    console.print("[bold]  ─── Обязательно для всех ───[/bold]")
    console.print("  4. Миграции:")
    console.print("       [dim]python manage.py makemigrations booking system[/dim]")
    console.print("       [dim]python manage.py migrate[/dim]")
    console.print("  5. URLs в корневом [cyan]urls.py[/cyan]:")
    console.print('       [dim]path("booking/", include("booking.urls")),[/dim]')
    console.print("  6. Cabinet URL в [cyan]cabinet/urls.py[/cyan]:")
    console.print("       [dim]from cabinet.views.booking import my_bookings_view, cancel_booking_view[/dim]")
    console.print('       [dim]path("my/bookings/", my_bookings_view, name="my_bookings"),[/dim]')
    console.print('       [dim]path("my/bookings/<int:pk>/cancel/", cancel_booking_view, name="cancel_booking"),[/dim]')
