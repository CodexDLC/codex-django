from argparse import ArgumentParser
from pathlib import Path
from typing import Any, ClassVar

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from loguru import logger as log

from codex_django.system.redis.managers.fixtures import get_fixture_hash_manager
from codex_django.system.utils.fixture_hash import compute_paths_hash


class BaseUpdateAllContentCommand(BaseCommand):
    """
    Base command to run multiple specific content update subcommands.
    Subclasses should define `commands_to_run`.
    """

    help = "Run multiple content update commands"
    commands_to_run: ClassVar[list[str]] = []

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--force", action="store_true", help="Ignore hash checks and force all updates")

    def handle(self, *args: Any, **options: Any) -> None:
        log.info(f"Command: {self.__class__.__module__.split('.')[-1]} | Action: Start")
        force = options.get("force", False)
        errors = []

        if not self.commands_to_run:
            self.stdout.write(self.style.WARNING("No commands defined in `commands_to_run`."))
            return

        for cmd in self.commands_to_run:
            try:
                log.debug(f"Action: SubCommand | name={cmd}")
                call_command(cmd, force=force)
            except Exception as e:
                msg = f"Subcommand {cmd} failed: {e}"
                log.error(f"Action: SubError | error={msg}")
                errors.append(msg)

        if errors:
            self.stdout.write(self.style.ERROR(f"Update completed with {len(errors)} errors."))
            for err in errors:
                self.stdout.write(self.style.ERROR(f" - {err}"))
            raise CommandError("One or more subcommands failed.")

        log.info("Action: Success")
        self.stdout.write(self.style.SUCCESS("\nAll updates completed. Cache invalidated selectively per change."))


class BaseHashProtectedCommand(BaseCommand):
    """
    Base command for fixture loading.
    Checks file hashes against Redis to prevent redundant loading.
    """

    fixture_key: str = ""

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--force", action="store_true", help="Ignore hash check and force update")

    def get_fixture_paths(self) -> list[Path]:
        """Returns a list of Path objects for the fixtures."""
        raise NotImplementedError("Subclasses must implement get_fixture_paths().")

    def handle_import(self, *args: Any, **options: Any) -> bool:
        """
        The main import logic.
        Should return True if successful, to allow the hash to be updated.
        """
        raise NotImplementedError("Subclasses must implement handle_import().")

    def handle(self, *args: Any, **options: Any) -> None:
        if not self.fixture_key:
            raise ValueError("fixture_key is not set on the command class")

        paths = [p for p in self.get_fixture_paths() if p.is_file()]
        if not paths:
            self.stdout.write(self.style.WARNING(f"Skipped {self.fixture_key}: No fixtures found."))
            return

        current_hash = compute_paths_hash(paths)
        force = options.get("force", False)

        manager = get_fixture_hash_manager()
        stored_hash = manager.get_hash(self.fixture_key)

        if not force and stored_hash == current_hash:
            self.stdout.write(f"Skipped {self.fixture_key}: fixture hash unchanged.")
            return

        # Execute the actual import logic
        success = self.handle_import(*args, **options)

        # Update hash if import succeeded (or if it doesn't return anything)
        if success is not False:
            manager.set_hash(self.fixture_key, current_hash)
            log.debug(f"Action: UpdateHash | fixture={self.fixture_key} hash={current_hash}")
