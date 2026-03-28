<!-- DOC_TYPE: CONCEPT -->

# CLI Entrypoints Moved

CLI entrypoint implementation now lives in `codex-django-cli`.

In this runtime repository, the only remaining entrypoint-related surface is the temporary compatibility forwarding under `codex_django.cli`.

## Migration Direction

- prefer the command entrypoint installed from `codex-django-cli`
- treat `codex_django.cli.main` here as a shim, not as the implementation home
