<!-- DOC_TYPE: GUIDE -->

# Agent Skills Integration

## Overview

`codex-django` bundles an optional, offline agent skill installer and payload within the runtime package under `codex_django.agent_skills`.

This integration targets Codex in a consuming Django project. It provides a compact router and focused references directly in the project workspace, pointing the agent to existing library mechanisms. Other agent integrations have not been verified.

Key design characteristics:

- **Runtime-owned and offline**: Shipped inside the core `codex-django` runtime package. It requires neither the `[cli]` companion extra nor an initialized or booted Django environment (`DJANGO_SETTINGS_MODULE` is not needed).
- **Target location**: Installs into `.agents/skills/codex-django/` in the consuming project, along with a bounded, delimited reference block in the project's root `AGENTS.md`.
- **Manifest-driven ownership**: Tracks managed files and SHA-256 digests in `.agents/skills/codex-django/.manifest.json`.
- **Safe mutations**: Update replaces only files and blocks owned by the installed package version. Custom project rules belong in separate skills, preserving separation of concerns.
- **Filesystem checks**: Refuses unowned file collisions and corrupt markers, rejects symlinks and reparse points, and stages changes with best-effort rollback. Backups are retained if recovery fails.

> [!NOTE]
> The installer currently writes `.agents/skills/` and `AGENTS.md`. It does not modify `CLAUDE.md` or other agent configuration files.

---

## Commands

Run the installer via the Python module entrypoint using the Python environment where `codex-django` is installed:

The `--project` argument is required and must point to an existing project directory. Normal use of the Python library does not require skill installation.

### Windows (PowerShell / Command Prompt)

```powershell
# Check current installation status
python -m codex_django.agent_skills status --project D:\path\to\project

# Install into a target project
python -m codex_django.agent_skills install --project D:\path\to\project

# Update after upgrading codex-django
python -m codex_django.agent_skills update --project D:\path\to\project

# Uninstall and clean up managed files
python -m codex_django.agent_skills delete --project D:\path\to\project
```

### POSIX (Linux / macOS)

```bash
# Check current installation status
python -m codex_django.agent_skills status --project /path/to/project

# Install into a target project
python -m codex_django.agent_skills install --project /path/to/project

# Update after upgrading codex-django
python -m codex_django.agent_skills update --project /path/to/project

# Uninstall and clean up managed files
python -m codex_django.agent_skills delete --project /path/to/project
```

---

## Exit Codes and Status Semantics

The `status` command provides programmatic inspection of the skill state in the project:

- **Exit code `0`**: Only returned when the skill is **healthy, fully verified, and up to date** with the currently installed `codex-django` package version and content payload.
- **Exit code `1`**: Returned if the skill is **absent** (not installed), **stale** (package upgraded or files modified), or **corrupt** (missing files, hash mismatches, broken `AGENTS.md` markers, or unmanaged directory collisions).

Sample status outputs:

- Healthy: `Installed and up to date.` (exit code `0`)
- Not installed: `Not installed.` (exit code `1`)
- Out of date: `Installed package version differs. Needs update.` (exit code `1`)
- Modified/corrupted: `File on disk modified or corrupt: SKILL.md` (exit code `1`)
- Broken instruction marker: `AGENTS.md instruction missing.` or `Orphan AGENTS.md block without ownership manifest.` (exit code `1`)

---

## Upgrade Lifecycle

Updating the library and refreshing agent instructions are distinct two-step operations:

1. **Upgrade the Python runtime package**:
   ```bash
   python -m pip install --upgrade codex-django
   ```
2. **Refresh the project skill from the newly installed package**:
   ```bash
   python -m codex_django.agent_skills update --project /path/to/project
   ```

Running `update` synchronizes `.agents/skills/codex-django/` with the upgraded package payload, prunes files removed in the new version, updates hashes in `.manifest.json`, and ensures the root `AGENTS.md` block is intact.

---

## Compact Router and References vs. Full Documentation

The installed skill is specifically optimized for coding agents:

- **Compact Router (`SKILL.md`)**: Acts as a lightweight index mapping user tasks (such as cabinet navigation, booking availability, messaging, or Redis caching) to specific topic references. Agents read `SKILL.md` first without blowing context limits.
- **Focused References (`references/*.md`)**: Describe relevant APIs, template locations, extension points, and library/project ownership boundaries. Agents read the references relevant to the task and inspect installed source for exact signatures.
- **Full Documentation (`docs/` and MkDocs site)**: Comprehensive narrative guides, tutorials, architectural explanations, and deep API references intended for human developers browsing the documentation site or repository.

---

## Ownership, Safety, and Rollback Guarantees

### Bounded Root `AGENTS.md` Block

The installer manages a delimited section in the project's root `AGENTS.md`:

```markdown
<!-- codex-django:skill:start -->
<!-- codex-django:skill:separator=1 -->
Use [codex-django](.agents/skills/codex-django/SKILL.md) for codex_django work.
<!-- codex-django:skill:end -->
```

- When installing into a project with existing `AGENTS.md` content, the block is appended cleanly with separator metadata.
- If `AGENTS.md` was created from scratch by `install`, `delete` removes `AGENTS.md` entirely when no user content was added. If existing content was present, `delete` excises only the bounded block, preserving user instructions.
- If markers are corrupted, manually altered, or mismatched, mutations (`update`/`delete`) **refuse to run** to avoid destroying developer modifications.

### Clean Ownership Separation

- The managed payload files are listed with SHA-256 digests in `.manifest.json`; additional unowned files are not added to the manifest.
- `update` overwrites only library-owned files.
- `delete` removes managed files even if edited, and prunes empty directories derived from their paths within the skill directory. It preserves unowned files and the project's `.agents/skills` parent directory.
- If an unowned file collides with a new payload filename during installation, the operation halts immediately.
- Custom project rules and business requirements must be kept in separate project skills or outside the managed block, never edited directly into the library's `SKILL.md`.

### Filesystem Transaction and Failure Recovery

- **Symlink protection**: Every path component is verified using `lstat`. Any symlinks or Windows NTFS reparse points trigger an immediate rejection to prevent path traversal attacks.
- **Staged writes**: Files are staged in a temporary directory on the same filesystem volume (`.codex-django-tx-*`).
- **No multi-file atomicity or crash guarantees**: The filesystem transaction does not promise ACID guarantees across crashes, power loss, or concurrent runner processes.
- **Ordinary rollback and retained backups**:
  - Before files are modified or deleted, snapshots of all destination files are copied into a temporary backup directory.
  - If an ordinary I/O error or failure occurs during staging or applying changes, an automatic in-process rollback restores the pre-existing state.
  - If recovery itself encounters an unexpected failure, the temporary directory containing intact backups is **deliberately retained** on disk, and the exact path is reported in the error message for manual inspection and recovery.

---

## Related Pages

- [Installation Modes](./installation-modes.md)
- [Runtime vs CLI](./runtime-vs-cli.md)
- [Project Structure](./project-structure.md)
