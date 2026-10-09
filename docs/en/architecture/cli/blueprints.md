<!-- DOC_TYPE: CONCEPT -->

# CLI Blueprints Moved

Blueprint trees are now owned by `codex-django-cli`.

They remain conceptually tied to `codex-django`, because generated code intentionally imports runtime modules such as `codex_django.system`, `codex_django.booking`, and `codex_django.messaging`. Older generated notification code may still import `codex_django.notifications` during the compatibility window.

## Runtime-Side Takeaway

From the runtime repository perspective, blueprints matter because they define how generated projects wire runtime modules together.
The actual blueprint source of truth now lives in `codex-django-cli`.
