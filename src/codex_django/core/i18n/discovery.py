from pathlib import Path


def discover_locale_paths(base_dir: Path, include_features: bool = True) -> list[str]:
    """
    Dynamically discovers all locale directories in the project.
    Scans:
    1. Top-level apps (directories with locale/ in base_dir).
    2. Features (directories with locale/ in base_dir/features/).

    Usage in settings.py:
    LOCALE_PATHS = discover_locale_paths(BASE_DIR)
    """
    paths = []

    # 1. Check centralized locale directory (for modular domains)
    central_locale = base_dir / "locale"
    if central_locale.exists():
        for item in central_locale.iterdir():
            if item.is_dir() and (item / "LC_MESSAGES").exists():
                paths.append(str(item))
            elif item.name == "common" and (item / "LC_MESSAGES").exists():
                # Explicitly add common if it exists and has messages
                paths.append(str(item))

    # 2. Backward compatibility / alternative structure:
    # Check top-level directories and features for their own locale/ folders
    for item in base_dir.iterdir():
        if item.is_dir() and (item / "locale").exists() and str(item / "locale") not in paths:
            paths.append(str(item / "locale"))

    features_dir = base_dir / "features"
    if include_features and features_dir.exists():
        for item in features_dir.iterdir():
            if item.is_dir() and (item / "locale").exists() and str(item / "locale") not in paths:
                paths.append(str(item / "locale"))

    return paths
