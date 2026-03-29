<!-- DOC_TYPE: CONCEPT -->

# CLI Commands Moved

Command handlers such as `init`, `deploy`, `add_app`, `booking`, and `notifications` now live in `codex-django-cli`.

`codex-django` keeps only compatibility forwarding under `codex_django.cli.commands.*` during the migration period.
