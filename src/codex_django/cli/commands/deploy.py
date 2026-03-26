"""
handle_generate_deploy
======================
Generates Docker infrastructure files for a project.
"""

import os
from secrets import token_urlsafe

from rich.console import Console

from codex_django.cli.engine import CLIEngine

console = Console()


def handle_generate_deploy(name: str, project_root: str) -> None:
    engine = CLIEngine()
    context = {
        "project_name": name,
        "secret_key": token_urlsafe(50),
    }

    # We place it in the project root's 'deploy' folder
    # but we follow the original logic where it's deploy/<name>/
    deploy_target = os.path.join(project_root, "deploy", name)

    engine.scaffold("deploy", target_dir=deploy_target, context=context, overwrite=True)

    console.print(f"[green]✓[/green] Deployment files generated in [bold]{deploy_target}[/bold]")
    console.print("\n[bold]Docker Compose snippet (add to your docker-compose.yaml):[/bold]")
    console.print("-" * 40)
    console.print(f"""
  {name}:
    build:
      context: .
      dockerfile: deploy/{name}/django.Dockerfile
    env_file: .env
    depends_on:
      - db
      - redis
""")
    console.print("-" * 40)
