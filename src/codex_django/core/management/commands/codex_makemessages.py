"""Domain-aware wrapper around Django's ``makemessages`` command.

The command scans a Codex project for template-bearing domains, creates
centralized ``locale/<domain>/`` directories, and runs Django's
``makemessages`` command separately for each domain plus a shared
``common`` bucket.

Examples:
    Preview what would be generated without writing files::

        python manage.py codex_makemessages --dry-run
"""

import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, cast

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Generate modular translation catalogs for Codex project layouts.

    The command understands three common template layouts:

    - root-level ``templates/<domain>/``
    - app-local ``<app>/templates/``
    - feature-local ``features/<feature>/templates/``
    """

    help = (
        "Template-driven modular makemessages: creates locale files based on "
        "subfolders in the root templates directory."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Register command-line arguments for the management command.

        Args:
            parser: Django/argparse parser instance for this command.
        """
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be done without actual processing.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Discover domains and run ``makemessages`` for each one.

        Args:
            *args: Positional arguments forwarded by Django's command runner.
            **options: Parsed command-line options.
        """
        base_dir = Path(cast(str, settings.BASE_DIR))  # type: ignore[misc]
        languages = [lang[0] for lang in settings.LANGUAGES]
        dry_run = cast(bool, options["dry_run"])

        if not languages:
            self.stdout.write(self.style.ERROR("No LANGUAGES defined in settings."))
            return

        self.stdout.write(self.style.SUCCESS(f"Languages: {', '.join(languages)}"))

        # 1. Discover domains
        domains: dict[str, str] = {}  # domain -> source_desc

        # From root templates subfolders (modular features style)
        templates_dir = base_dir / "templates"
        if templates_dir.exists():
            for item in templates_dir.iterdir():
                if item.is_dir():
                    domains[item.name] = "root templates"

        # From autonomous apps in root (like 'cabinet/')
        excludes = {"venv", "node_modules", "static", "media", "locale", "templates", ".git", ".idea", "__pycache__"}
        for item in base_dir.iterdir():
            if (
                item.is_dir()
                and item.name not in excludes
                and not item.name.startswith(".")
                and (item / "templates").exists()
            ):
                if item.name in domains:
                    domains[item.name] = "hybrid (root + app)"
                else:
                    domains[item.name] = "app templates"

        # From features (features/home/templates/...)
        features_dir = base_dir / "features"
        if features_dir.exists():
            for item in features_dir.iterdir():
                if item.is_dir() and (item / "templates").exists():
                    if item.name in domains:
                        domains[item.name] = "hybrid (root + feature)"
                    else:
                        domains[item.name] = "feature templates"

        manage_py = base_dir / "manage.py"
        all_domain_names = sorted(domains.keys())

        # 2. Process each domain
        for domain, source in sorted(domains.items()):
            self.stdout.write(self.style.MIGRATE_HEADING(f"==> Domain: [{domain}] ({source})"))

            # Centralized locale folder
            locale_dir = base_dir / "locale" / domain
            if not dry_run:
                locale_dir.mkdir(exist_ok=True, parents=True)

            cmd = self._build_cmd(manage_py, languages, domain, base_dir, all_domain_names)

            self.stdout.write(f"  Scanning for {domain}...")
            self._run_makemessages(cmd, base_dir, domain, dry_run)

        # 3. Process Global/Common
        self.stdout.write(self.style.MIGRATE_HEADING("==> Domain: [common]"))
        common_locale_dir = base_dir / "locale" / "common"
        if not dry_run:
            common_locale_dir.mkdir(exist_ok=True, parents=True)

        common_cmd = self._build_cmd(manage_py, languages, "common", base_dir, all_domain_names)
        self.stdout.write("  Scanning for common strings...")
        self._run_makemessages(common_cmd, base_dir, "common", dry_run)

    def _build_cmd(
        self, manage_py: Path, languages: list[str], domain: str, base_dir: Path, all_domains: list[str]
    ) -> list[str]:
        """Build the concrete ``makemessages`` subprocess command.

        Args:
            manage_py: Path to the project's ``manage.py`` script.
            languages: Configured Django language codes.
            domain: Domain currently being processed.
            base_dir: Project root directory.
            all_domains: Every discovered domain name used to construct
                ignore patterns.

        Returns:
            A subprocess argument list ready to pass to ``subprocess.run``.
        """
        cmd = [sys.executable, str(manage_py), "makemessages"]
        for lang in languages:
            cmd.extend(["-l", lang])

        ignores = ["venv/*", "node_modules/*", "static/*", "media/*"]

        if domain == "common":
            # Ignore all modular folders
            for d in all_domains:
                ignores.append(f"templates/{d}/*")
                ignores.append(f"{d}/*")
                ignores.append(f"features/{d}/*")
                # Also ignore the output locale directories to avoid scanning .po files
                ignores.append(f"locale/{d}/*")
        else:
            # Domain-specific scan:
            # We want to scan only templates/<domain> and either <domain>/ or features/<domain>/
            # The easiest way with makemessages -i is to ignore everything else.

            for d in all_domains:
                if d != domain:
                    ignores.append(f"templates/{d}/*")
                    ignores.append(f"{d}/*")
                    ignores.append(f"features/{d}/*")

            # Also ignore the common locale directory
            ignores.append("locale/common/*")
            # And ignore other domains' locale directories
            for d in all_domains:
                if d != domain:
                    ignores.append(f"locale/{d}/*")

            # Also ignore root templates for specific domains
            templates_dir = base_dir / "templates"
            if templates_dir.exists():
                for item in templates_dir.iterdir():
                    if item.is_file():
                        ignores.append(f"templates/{item.name}")

        for ignore in ignores:
            cmd.extend(["-i", ignore])

        return cmd

    def _run_makemessages(self, cmd: list[str], base_dir: Path, domain: str, dry_run: bool) -> None:
        """Execute or preview a single ``makemessages`` subprocess call.

        Args:
            cmd: Fully constructed subprocess command.
            base_dir: Project root used as the subprocess working directory.
            domain: Domain label used for status output.
            dry_run: When ``True``, print the command instead of executing it.
        """
        if dry_run:
            self.stdout.write(f"  [DRY-RUN] Executing: {' '.join(cmd)}")
            return

        try:
            result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)  # nosec
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Updated locale for {domain}"))
            else:
                self.stdout.write(self.style.ERROR(f"  [ERROR] {result.stderr}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  [FATAL] {e}"))
