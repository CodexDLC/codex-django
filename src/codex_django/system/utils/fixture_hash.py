"""Hash helpers for content and fixture synchronization workflows."""

import hashlib
from pathlib import Path


def compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute a SHA-256 digest for a single file.

    Args:
        path: Filesystem path to the file that should be hashed.
        chunk_size: Read size used while streaming file contents.

    Returns:
        Hex-encoded SHA-256 digest for the file contents.
    """
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_paths_hash(paths: list[Path]) -> str:
    """Compute a combined SHA-256 digest for multiple fixture files.

    The digest incorporates both file names and file contents so that renames
    and content changes invalidate the stored value. Non-file paths are
    ignored.

    Args:
        paths: Candidate filesystem paths to include in the combined hash.

    Returns:
        Hex-encoded SHA-256 digest for the ordered set of existing files.
    """
    sha256 = hashlib.sha256()
    for p in sorted(paths, key=lambda x: x.name):
        if not p.is_file():
            continue
        sha256.update(p.name.encode("utf-8"))
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
    return sha256.hexdigest()
