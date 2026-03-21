"""Quality gate for codex-django."""

import sys
from pathlib import Path

from codex_core.dev.check_runner import BaseCheckRunner


class CheckRunner(BaseCheckRunner):
    PROJECT_NAME = "codex-django"
    INTEGRATION_REQUIRES = "Redis (optional, in-memory mock available)"

    def run_tests(self, marker: str = "unit") -> bool:
        self.print_step(f"Running {marker.capitalize()} Tests")
        # integration/e2e: skip coverage threshold to avoid fail on partial runs
        no_cov = "--no-cov" if marker != "unit" else ""
        cmd = f'"{sys.executable}" -m pytest {self.tests_dir} -m {marker} -v --tb=short {no_cov}'.strip()
        success, _ = self.run_command(cmd)
        if success:
            self.print_success(f"{marker.capitalize()} tests passed.")
        else:
            self.print_error(f"{marker.capitalize()} tests failed.")
        return success

    def extra_checks(self) -> bool:
        return True


if __name__ == "__main__":
    CheckRunner(Path(__file__).parent.parent.parent).main()
