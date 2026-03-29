from pathlib import Path

import pytest

from codex_django.system.utils.fixture_hash import compute_file_hash, compute_paths_hash

pytestmark = pytest.mark.unit


def test_compute_file_hash_changes_with_file_contents(tmp_path: Path):
    file_path = tmp_path / "data.json"
    file_path.write_text('{"hello":"world"}', encoding="utf-8")

    digest1 = compute_file_hash(file_path)

    file_path.write_text('{"hello":"codex"}', encoding="utf-8")
    digest2 = compute_file_hash(file_path)

    assert digest1 != digest2
    assert len(digest1) == 64


def test_compute_paths_hash_ignores_non_files_and_is_name_order_stable(tmp_path: Path):
    alpha = tmp_path / "alpha.json"
    beta = tmp_path / "beta.json"
    nested_dir = tmp_path / "folder"

    alpha.write_text("A", encoding="utf-8")
    beta.write_text("B", encoding="utf-8")
    nested_dir.mkdir()

    digest1 = compute_paths_hash([beta, nested_dir, alpha])
    digest2 = compute_paths_hash([alpha, beta])

    assert digest1 == digest2


def test_compute_paths_hash_changes_when_filename_changes(tmp_path: Path):
    original = tmp_path / "one.json"
    renamed = tmp_path / "two.json"
    original.write_text("same-content", encoding="utf-8")
    renamed.write_text("same-content", encoding="utf-8")

    assert compute_paths_hash([original]) != compute_paths_hash([renamed])
