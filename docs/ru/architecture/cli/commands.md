<!-- DOC_TYPE: CONCEPT -->

# Команды CLI Переехали

Handlers команд вроде `init`, `deploy`, `add_app`, `booking` и `notifications` теперь живут в `codex-django-cli`.

В `codex-django` остаются только compatibility forwarding shims под `codex_django.cli.commands.*` на время миграции.
