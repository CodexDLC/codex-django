<!-- DOC_TYPE: RUNBOOK -->

# PyPI Release Playbook

These shell commands target Linux/macOS; the publishing and docs workflows run on Ubuntu.

## Preconditions

Before cutting a release tag, make sure:

1. Choose the next release version from the changelog and repository tags. Do not reuse a tag.
2. The target branch is green and the working tree is clean.
3. Documentation and `CHANGELOG.md` describe the intended release.
4. The version comes from the Git tag through `hatch-vcs`.

## Local Verification

Run the same checks used by CI, then build and inspect the distribution:

```bash
uv sync --locked --extra maintainer --extra docs
uv run pre-commit run --all-files
uv run python tools/dev/check.py --security
uv run mypy src/
uv run pytest tests/ -m unit -v --tb=short
uv run mkdocs build --strict
uv build --no-sources
uvx twine check dist/*
```

Use a fresh output directory for each candidate so old artifacts cannot be mistaken for the current build. The sdist must contain only project sources, tests, documentation, and build configuration, without local virtual environments or generated graph files.

For a release containing the optional agent skill, inspect the wheel and sdist to ensure `codex_django/agent_skills/resources/SKILL.md` and its `references/` files are present.

## Test Installation In A Clean Environment

Install the built wheel in a fresh environment and check the optional installer without touching a real project:

```bash
python -m venv .venv-release-check
.venv-release-check/bin/python -m pip install dist/codex_django-*.whl
mkdir -p .release-skill-smoke
.venv-release-check/bin/python -m codex_django.agent_skills install --project .release-skill-smoke
.venv-release-check/bin/python -m codex_django.agent_skills status --project .release-skill-smoke
.venv-release-check/bin/python -m codex_django.agent_skills delete --project .release-skill-smoke
```

The `status` command must print `Installed and up to date.` and exit with code `0`. Confirm that published sibling `codex-*` dependencies resolve in this environment.

## Tag And Publish

The `publish.yml` and `docs.yml` workflows run on pushed `v*` tags. Create the selected tag locally, rebuild from that tag, and verify that the artifact version matches it before pushing:

```bash
git tag vX.Y.Z
uv build --no-sources
uvx twine check dist/*
# Inspect the names in dist/ and confirm they contain X.Y.Z.
git push origin vX.Y.Z
```

Replace `X.Y.Z` with the chosen version. If the build or artifact checks fail, correct the release locally before publishing the tag.

- `publish.yml` builds the wheel and sdist, runs `twine check`, and publishes to PyPI through trusted publishing.
- `docs.yml` deploys versioned documentation with `mike` and updates the `latest` alias.

## After Release

1. Confirm the expected package version and distribution files on PyPI.
2. Confirm the versioned docs and `latest` alias on GitHub Pages.
3. Smoke-test installation from PyPI in a fresh virtual environment.
