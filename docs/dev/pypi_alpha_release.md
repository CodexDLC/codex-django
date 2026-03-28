<!-- DOC_TYPE: RUNBOOK -->

# PyPI Alpha Release Playbook

## Preconditions

Before cutting an alpha tag, make sure:

1. The target branch is green.
2. Docs content is up to date.
3. The version should come from a Git tag through `hatch-vcs`.
4. The package builds without local source hacks.

## Local Verification

Run the release checks from a clean working tree:

```bash
uv sync --locked --extra dev --extra docs
python tools/dev/check.py --lint
python tools/dev/check.py --types
python tools/dev/check.py --tests unit
uv build --no-sources
uvx twine check dist/*
```

## Test Installation In A Clean Environment

Validate the built wheel before tagging:

```bash
python -m venv .venv-release-check
.venv-release-check\Scripts\activate
pip install dist/codex_django-*.whl
python -c "import codex_django; print(codex_django.__doc__)"
deactivate
```

If your release depends on sibling `codex-*` libraries, also verify that their published versions resolve correctly in the clean environment.

## Cut The Alpha Release

The repository is configured so that `v*` tags trigger both documentation deployment and PyPI publishing workflows.

Typical alpha tags:

- `v0.1.0a1`
- `v0.1.0a2`

After local verification:

```bash
git tag v0.1.0a1
git push origin v0.1.0a1
```

## Expected Automation

- `publish.yml` builds the wheel and sdist, runs `twine check`, and publishes to PyPI through trusted publishing.
- `docs.yml` deploys versioned documentation with `mike` and updates the `latest` alias.

## After Release

1. Confirm the new package version on PyPI.
2. Confirm the docs version on GitHub Pages.
3. Smoke-test installation from PyPI in a fresh virtual environment.
