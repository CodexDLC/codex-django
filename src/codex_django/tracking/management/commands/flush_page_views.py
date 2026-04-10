"""Management command for flushing tracking counters."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    """Flush Redis page-view counters into the database."""

    help = "Flush codex tracking page-view counters into PageView rows."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--date", dest="date_str", help="Date to flush in YYYY-MM-DD format.")

    def handle(self, *args: object, **options: object) -> None:
        from codex_django.tracking.flush import flush_page_views

        date_str = options.get("date_str")
        count = flush_page_views(str(date_str) if date_str else None)
        self.stdout.write(self.style.SUCCESS(f"[codex-tracking] flushed {count} paths"))
