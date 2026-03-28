"""Base classes for content update and fixture import commands.

These command abstractions encapsulate two recurring patterns:

- running several update commands as one orchestration step
- skipping fixture imports when the input files have not changed
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Any, ClassVar

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from loguru import logger as log

from codex_django.system.redis.managers.fixtures import get_fixture_hash_manager
from codex_django.system.utils.fixture_hash import compute_paths_hash


class BaseUpdateAllContentCommand(BaseCommand):
    """Run a predefined sequence of content update subcommands.

    Subclasses are expected to populate ``commands_to_run`` with Django
    management command names. Each subcommand receives the ``--force`` flag
    when it is provided to the aggregate command.
    """

    help = "Run multiple content update commands"
    commands_to_run: ClassVar[list[str]] = []

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Register shared command-line arguments.

        Args:
            parser: Django/argparse parser instance for this command.
        """
        parser.add_argument("--force", action="store_true", help="Ignore hash checks and force all updates")

    def handle(self, *args: Any, **options: Any) -> None:
        """Run each configured subcommand and aggregate failures.

        Args:
            *args: Positional arguments forwarded by Django's command runner.
            **options: Parsed command-line options.

        Raises:
            django.core.management.base.CommandError: If one or more
                subcommands fail.
        """
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
    """Base class for fixture import commands guarded by a Redis hash check.

    The command computes a combined hash for the declared fixture files and
    skips the import when the stored hash matches the current one, unless the
    caller passes ``--force``.
    """

    fixture_key: str = ""

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Register shared command-line arguments.

        Args:
            parser: Django/argparse parser instance for this command.
        """
        parser.add_argument("--force", action="store_true", help="Ignore hash check and force update")

    def get_fixture_paths(self) -> list[Path]:
        """Return the fixture files that define the current content payload.

        Returns:
            A list of filesystem paths that should participate in the content
            hash calculation.
        """
        raise NotImplementedError("Subclasses must implement get_fixture_paths().")

    def handle_import(self, *args: Any, **options: Any) -> bool:
        """Execute the actual import operation for the selected fixtures.

        Args:
            *args: Positional arguments forwarded by Django's management
                command infrastructure.
            **options: Parsed command-line options.

        Returns:
            ``True`` when the import completed successfully. Returning
            ``False`` prevents the stored fixture hash from being updated.
        """
        raise NotImplementedError("Subclasses must implement handle_import().")

    def handle(self, *args: Any, **options: Any) -> None:
        """Skip or execute an import based on the computed fixture hash.

        Args:
            *args: Positional arguments forwarded by Django's command runner.
            **options: Parsed command-line options.

        Raises:
            ValueError: If the subclass did not set ``fixture_key``.
        """
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
