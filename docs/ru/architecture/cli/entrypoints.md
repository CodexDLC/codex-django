<!-- DOC_TYPE: CONCEPT -->

# Entrypoints CLI Переехали

Реализация CLI entrypoints теперь живет в `codex-django-cli`.

В этом runtime-репозитории от entrypoint-слоя остались только временные compatibility forwarding shims под `codex_django.cli`.

## Направление Миграции

- использовать command entrypoint, установленный из `codex-django-cli`
- считать `codex_django.cli.main` здесь shim-слоем, а не домом реализации
