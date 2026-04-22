"""Quality gate for codex-django."""

from pathlib import Path

from codex_core.dev.check_runner import BaseCheckRunner


class CheckRunner(BaseCheckRunner):
    """Thin launcher; project policy lives in pyproject.toml."""

    def run_ci(self) -> None:
        self._clear_screen()
        super().run_ci()


if __name__ == "__main__":
    CheckRunner(Path(__file__).parent.parent.parent).main()
