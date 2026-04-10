"""Base classes and helpers for content update and fixture import commands.

These command abstractions encapsulate two recurring patterns:

- running several update commands as one orchestration step
- skipping fixture imports when the input files have not changed
- importing Django-style JSON fixture payloads into configurable models
"""

import json
from argparse import ArgumentParser
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from loguru import logger as log

from codex_django.system.redis.managers.fixtures import get_fixture_hash_manager
from codex_django.system.utils.fixture_hash import compute_paths_hash


@dataclass(frozen=True)
class JsonFixtureLoadResult:
    """Loaded Django-style fixture rows plus parsing diagnostics."""

    rows: list[dict[str, Any]] = field(default_factory=list)
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return whether the fixture file was parsed successfully."""
        return not self.errors


@dataclass(frozen=True)
class FixtureImportResult:
    """Summary of model rows created, updated, or skipped by an importer."""

    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return whether the import completed without fatal errors."""
        return not self.errors


def load_json_fixture_rows(path: Path, fields_key: str = "fields") -> JsonFixtureLoadResult:
    """Load a Django-style JSON fixture and return each item's ``fields`` mapping.

    Args:
        path: Fixture file path.
        fields_key: Item key containing model field values.

    Returns:
        Parsed row mappings plus skipped-item and error diagnostics. Invalid
        JSON, unreadable files, and non-list payloads are fatal errors. Items
        without a usable fields mapping are skipped.
    """
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        return JsonFixtureLoadResult(errors=[f"Error decoding JSON fixture {path}: {exc}"])
    except OSError as exc:
        return JsonFixtureLoadResult(errors=[f"Error reading JSON fixture {path}: {exc}"])

    if not isinstance(payload, list):
        return JsonFixtureLoadResult(errors=[f"Invalid fixture format in {path}: expected a list."])

    rows: list[dict[str, Any]] = []
    skipped = 0
    for item in payload:
        if not isinstance(item, Mapping):
            skipped += 1
            continue
        fields_value = item.get(fields_key)
        if not isinstance(fields_value, Mapping):
            skipped += 1
            continue
        rows.append(dict(fields_value))

    return JsonFixtureLoadResult(rows=rows, skipped=skipped)


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

    def get_command_label(self, command_name: str) -> str:
        """Return a display label for a subcommand.

        Args:
            command_name: Django management command name.

        Returns:
            Human-readable label. Subclasses may override this to print
            project-specific section headings.
        """
        return command_name

    def before_subcommand(self, command_name: str) -> None:
        """Hook called before each subcommand runs."""

    def after_subcommand(self, command_name: str) -> None:
        """Hook called after each successful subcommand runs."""

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
                label = self.get_command_label(cmd)
                log.debug(f"Action: SubCommand | name={cmd} label={label}")
                self.before_subcommand(cmd)
                log.debug(f"Action: SubCommand | name={cmd}")
                call_command(cmd, force=force)
                self.after_subcommand(cmd)
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


class JsonFixtureUpsertCommand(BaseHashProtectedCommand):
    """Import Django-style JSON fixture rows with ``update_or_create``.

    Subclasses usually set ``fixture_path``, ``fixture_key``, ``model_path``
    or ``model_class``, and ``lookup_field``.
    """

    fixture_path: str | Path | None = None
    fixture_paths: ClassVar[list[str | Path]] = []
    model_path: str = ""
    model_class: Any = None
    lookup_field: str = "key"
    fields_key: str = "fields"

    def get_fixture_paths(self) -> list[Path]:
        """Return configured fixture paths as :class:`Path` objects."""
        configured = list(self.fixture_paths)
        if self.fixture_path is not None:
            configured.append(self.fixture_path)
        return [Path(path) for path in configured]

    def get_model_class(self) -> Any:
        """Return the model class that receives imported rows."""
        if self.model_class is not None:
            return self.model_class
        if not self.model_path:
            raise ValueError("model_path or model_class is required")
        return apps.get_model(self.model_path)

    def get_lookup_value(self, fields: dict[str, Any]) -> Any:
        """Return the lookup value for a fixture row."""
        return fields.get(self.lookup_field)

    def get_defaults(self, fields: dict[str, Any]) -> dict[str, Any]:
        """Return defaults passed to ``update_or_create``."""
        return fields

    def handle_import(self, *args: Any, **options: Any) -> bool:
        """Import configured JSON fixture rows into the target model."""
        model = self.get_model_class()
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors: list[str] = []

        for fixture_path in self.get_fixture_paths():
            load_result = load_json_fixture_rows(fixture_path, fields_key=self.fields_key)
            skipped_count += load_result.skipped
            if not load_result.success:
                errors.extend(load_result.errors)
                continue

            for fields in load_result.rows:
                lookup_value = self.get_lookup_value(fields)
                if lookup_value in (None, ""):
                    skipped_count += 1
                    continue

                _, created = model.objects.update_or_create(
                    **{self.lookup_field: lookup_value},
                    defaults=self.get_defaults(fields),
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        result = FixtureImportResult(
            created=created_count,
            updated=updated_count,
            skipped=skipped_count,
            errors=errors,
        )
        self.import_result = result

        if not result.success:
            for error in result.errors:
                self.stdout.write(self.style.ERROR(error))
            return False

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {self.fixture_key}: {result.created} created, "
                f"{result.updated} updated, {result.skipped} skipped"
            )
        )
        return True


class SingletonFixtureUpdateCommand(BaseHashProtectedCommand):
    """Update a singleton model instance from the first row in a JSON fixture."""

    fixture_path: str | Path | None = None
    fixture_paths: ClassVar[list[str | Path]] = []
    model_path: str = ""
    model_class: Any = None
    singleton_pk: Any = 1
    fields_key: str = "fields"

    def get_fixture_paths(self) -> list[Path]:
        """Return configured fixture paths as :class:`Path` objects."""
        configured = list(self.fixture_paths)
        if self.fixture_path is not None:
            configured.append(self.fixture_path)
        return [Path(path) for path in configured]

    def get_model_class(self) -> Any:
        """Return the singleton model class."""
        if self.model_class is not None:
            return self.model_class
        if not self.model_path:
            raise ValueError("model_path or model_class is required")
        return apps.get_model(self.model_path)

    def get_singleton(self, model: Any) -> Any:
        """Return the singleton instance for the target model."""
        load = getattr(model, "load", None)
        if callable(load):
            return load()
        instance, _ = model.objects.get_or_create(pk=self.singleton_pk)
        return instance

    def normalize_current_value(self, field_name: str, value: Any) -> Any:
        """Normalize current model values before fixture comparison."""
        if hasattr(value, "__str__") and field_name in ["latitude", "longitude"]:
            return str(value)
        return value

    def get_update_fields(self, fixture_fields: dict[str, Any]) -> dict[str, Any]:
        """Return fixture fields eligible for singleton assignment."""
        return fixture_fields

    def sync_instance(self, instance: Any) -> None:
        """Synchronize the updated instance to Redis when a manager is available."""
        from codex_django.core.redis.managers.settings import get_site_settings_manager

        manager = get_site_settings_manager()
        manager.save_instance(instance)

    def handle_import(self, *args: Any, **options: Any) -> bool:
        """Apply the first fixture row to the configured singleton instance."""
        fixture_paths = self.get_fixture_paths()
        if not fixture_paths:
            self.stdout.write(self.style.ERROR(f"No fixture path configured for {self.fixture_key}."))
            return False

        load_result = load_json_fixture_rows(fixture_paths[0], fields_key=self.fields_key)
        if not load_result.success:
            for error in load_result.errors:
                self.stdout.write(self.style.ERROR(error))
            return False
        if not load_result.rows:
            self.stdout.write(self.style.ERROR(f"Invalid fixture format for {self.fixture_key}: no rows found."))
            return False

        model = self.get_model_class()
        instance = self.get_singleton(model)
        updated_fields: list[str] = []

        for field_name, new_value in self.get_update_fields(load_result.rows[0]).items():
            if not hasattr(instance, field_name):
                continue
            current_value = self.normalize_current_value(field_name, getattr(instance, field_name))
            if str(current_value) != str(new_value):
                setattr(instance, field_name, new_value)
                updated_fields.append(field_name)

        self.updated_fields = updated_fields
        if not updated_fields:
            self.stdout.write(self.style.SUCCESS(f"No changes needed for {self.fixture_key}."))
            return True

        instance.save()
        self.sync_instance(instance)
        self.stdout.write(self.style.SUCCESS(f"Updated {self.fixture_key}: {len(updated_fields)} fields changed"))
        return True
