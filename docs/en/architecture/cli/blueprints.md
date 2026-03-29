<!-- DOC_TYPE: CONCEPT -->

# CLI Blueprints Moved

Blueprint trees are now owned by `codex-django-cli`.

They remain conceptually tied to `codex-django`, because generated code intentionally imports runtime modules such as `codex_django.system`, `codex_django.booking`, and `codex_django.notifications`.

## Runtime-Side Takeaway

From the runtime repository perspective, blueprints matter because they define how generated projects wire runtime modules together.
The actual blueprint source of truth now lives in `codex-django-cli`.
