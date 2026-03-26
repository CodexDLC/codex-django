"""
Unit tests for codex_django.core.i18n.discovery.discover_locale_paths
=======================================================================
Pure filesystem tests — no mocks needed, uses pytest tmp_path.
"""
import pytest

from codex_django.core.i18n.discovery import discover_locale_paths


def _make_locale_dir(base: "Path", lang: str = "en") -> None:
    """Create a minimal locale structure: base/LC_MESSAGES/."""
    lc = base / "LC_MESSAGES"
    lc.mkdir(parents=True, exist_ok=True)
    (lc / "django.po").write_text("")


from pathlib import Path  # noqa: E402 (after the helper)


@pytest.mark.unit
class TestDiscoverLocalePaths:
    def test_empty_directory_returns_empty_list(self, tmp_path: Path):
        result = discover_locale_paths(tmp_path)
        assert result == []

    def test_modular_central_locale_discovered(self, tmp_path: Path):
        """locale/<domain>/<lang>/LC_MESSAGES/ is discovered."""
        domain_dir = tmp_path / "locale" / "cabinet"
        lang_dir = domain_dir / "en"
        _make_locale_dir(lang_dir)

        result = discover_locale_paths(tmp_path)
        assert str(domain_dir) in result

    def test_multiple_modular_domains_discovered(self, tmp_path: Path):
        """Multiple domains in locale/ are all discovered."""
        for domain in ["cabinet", "common", "main"]:
            domain_dir = tmp_path / "locale" / domain
            _make_locale_dir(domain_dir / "en")

        result = discover_locale_paths(tmp_path)
        for domain in ["cabinet", "common", "main"]:
            assert str(tmp_path / "locale" / domain) in result

    def test_top_level_app_locale_discovered(self, tmp_path: Path):
        """An app directory with its own locale/ folder is discovered."""
        app_locale = tmp_path / "myapp" / "locale"
        app_locale.mkdir(parents=True)

        result = discover_locale_paths(tmp_path)
        assert str(app_locale) in result

    def test_features_dir_discovered_when_include_features_true(self, tmp_path: Path):
        """features/<feature>/locale/ is discovered when include_features=True."""
        feat_locale = tmp_path / "features" / "booking" / "locale"
        feat_locale.mkdir(parents=True)

        result = discover_locale_paths(tmp_path, include_features=True)
        assert str(feat_locale) in result

    def test_features_dir_skipped_when_include_features_false(self, tmp_path: Path):
        """features/<feature>/locale/ is NOT discovered when include_features=False."""
        feat_locale = tmp_path / "features" / "booking" / "locale"
        feat_locale.mkdir(parents=True)

        result = discover_locale_paths(tmp_path, include_features=False)
        assert str(feat_locale) not in result

    def test_no_duplicate_paths(self, tmp_path: Path):
        """No path appears more than once in the result."""
        app_locale = tmp_path / "myapp" / "locale"
        app_locale.mkdir(parents=True)

        result = discover_locale_paths(tmp_path)
        assert len(result) == len(set(result))

    def test_multiple_apps_all_discovered(self, tmp_path: Path):
        """Multiple apps with locale dirs are all included."""
        for name in ["app_a", "app_b", "app_c"]:
            (tmp_path / name / "locale").mkdir(parents=True)

        result = discover_locale_paths(tmp_path)
        for name in ["app_a", "app_b", "app_c"]:
            assert str(tmp_path / name / "locale") in result
