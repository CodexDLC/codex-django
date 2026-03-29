"""Quality gate for codex-django."""

import os
import sys
from pathlib import Path

from codex_core.dev.check_runner import BaseCheckRunner, Colors


class CheckRunner(BaseCheckRunner):
    PROJECT_NAME = "codex-django"
    INTEGRATION_REQUIRES = "Redis (optional, in-memory mock available)"
    # CVE-2026-4539: pygments — no fix available yet (latest version)
    AUDIT_FLAGS = "--skip-editable --ignore-vuln CVE-2026-4539"

    @staticmethod
    def _is_empty_test_selection(output: str) -> bool:
        """Return True when pytest matched no tests for the requested marker."""
        normalized = output.lower()
        return "0 selected" in normalized or "no tests ran" in normalized

    def run_tests(self, marker: str = "unit") -> bool:
        self.print_step(f"Running {marker.capitalize()} Tests")
        # integration/e2e: skip coverage threshold to avoid fail on partial runs
        no_cov = "--no-cov" if marker != "unit" else ""
        cmd = f'"{sys.executable}" -m pytest {self.tests_dir} -m {marker} -v --tb=short {no_cov}'.strip()
        success, out = self.run_command(cmd, capture_output=marker != "unit")
        if marker != "unit" and not success and self._is_empty_test_selection(out):
            self.print_success(f"No {marker} tests collected; skipping.")
            return True
        if success:
            self.print_success(f"{marker.capitalize()} tests passed.")
        else:
            self.print_error(f"{marker.capitalize()} tests failed.")
        return success

    def check_security(self) -> bool:
        self.print_step("Security Audit (pip-audit)")
        success, out = self.run_command(
            f'"{sys.executable}" -m pip_audit {self.AUDIT_FLAGS}',
            capture_output=True,
        )
        if not success:
            self.print_error(f"Security audit failed:\n{out}")
        else:
            self.print_success("Security audit passed.")
        return success

    def extra_checks(self) -> bool:
        return True

    def run_all(self) -> None:
        """Developer mode: run checks and default integration prompt to 'no' when non-interactive."""
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        print(f"{Colors.HEADER}{Colors.BOLD}=== {self.PROJECT_NAME} quality gate ==={Colors.ENDC}")

        if not self.check_quality():
            sys.exit(1)
        if not self.check_types():
            sys.exit(1)
        if not self.check_security():
            sys.exit(1)
        if not self.extra_checks():
            sys.exit(1)
        if not self.run_tests("unit"):
            sys.exit(1)

        prompt = (
            f"\n{Colors.YELLOW}🚀 Run Integration Tests? (Requires: {self.INTEGRATION_REQUIRES}) [y/N]: {Colors.ENDC}"
        )
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            answer = "n"
            print("n")

        if answer == "y" and not self.run_tests("integration"):
            sys.exit(1)

        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED!{Colors.ENDC}")


if __name__ == "__main__":
    CheckRunner(Path(__file__).parent.parent.parent).main()
