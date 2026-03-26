"""
handle_configure_precommit
==========================
Generates a .pre-commit-config.yaml with standard quality checks.
"""

import os

from rich.console import Console

console = Console()

PRE_COMMIT_CONFIG = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=2000']
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.44.0
    hooks:
      - id: markdownlint
        args: ["--fix", "--disable", "MD013"]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

  # 1. Проверка библиотек на уязвимости (CVE)
  - repo: https://github.com/pypa/pip-audit
    rev: v2.10.0
    hooks:
      - id: pip-audit
        args: ["--local", "--timeout", "15"]
        additional_dependencies: ["pip-audit[toml]", "toml"]

  # 2. Поиск "забытых" секретов и паролей (усиленный)
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # 3. Листинг и проверка Docker-файлов (Linter)
  - repo: https://github.com/hadolint/hadolint
    rev: v2.12.0
    hooks:
      - id: hadolint-docker
        entry: hadolint/hadolint:v2.12.0 hadolint
        args: ["--ignore", "DL3008", "--ignore", "DL3013"]
"""


def handle_configure_precommit(project_root: str) -> None:
    config_path = os.path.join(project_root, ".pre-commit-config.yaml")

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(PRE_COMMIT_CONFIG)

    # Create empty .secrets.baseline if it doesn't exist to avoid hook errors
    baseline_path = os.path.join(project_root, ".secrets.baseline")
    if not os.path.exists(baseline_path):
        import json

        empty_baseline = {
            "version": "1.5.0",
            "plugins_used": [
                {"name": "ArtifactoryDetector"},
                {"name": "AWSKeyDetector"},
                {"name": "Base64HighEntropyString", "limit": 4.5},
                {"name": "BasicAuthDetector"},
                {"name": "CloudantDetector"},
                {"name": "HexHighEntropyString", "limit": 3.0},
                {"name": "IbmCloudIamDetector"},
                {"name": "IbmCosHmacDetector"},
                {"name": "JwtTokenDetector"},
                {"name": "KeywordDetector", "keyword_exclude": ""},
                {"name": "MailchimpDetector"},
                {"name": "NpmDetector"},
                {"name": "PrivateKeyDetector"},
                {"name": "SlackDetector"},
                {"name": "SoftlayerDetector"},
                {"name": "StripeDetector"},
                {"name": "TwilioKeyDetector"},
            ],
            "results": {},
            "exclude": {"files": ".*", "lines": None},
        }
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(empty_baseline, f, indent=2)

    console.print("[green]✓[/green] Created [bold].pre-commit-config.yaml[/bold]")
    console.print("\n[bold]To finish setup, run:[/bold]")
    console.print("  [cyan]pip install pre-commit[/cyan]")
    console.print("  [cyan]pre-commit install[/cyan]\n")
