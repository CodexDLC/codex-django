<!-- DOC_TYPE: CONCEPT -->

# Blueprints CLI Переехали

Деревья blueprints теперь принадлежат `codex-django-cli`.

При этом они по-прежнему концептуально связаны с `codex-django`, потому что generated code намеренно импортирует runtime-модули вроде `codex_django.system`, `codex_django.booking` и `codex_django.messaging`. Старый generated notification code может временно импортировать `codex_django.notifications` в compatibility window.

## Что Важно Со Стороны Runtime

Для runtime-репозитория blueprints важны тем, что именно через них generated projects связывают reusable runtime-модули в рабочую проектную структуру.
Но сам source of truth для blueprints теперь находится в `codex-django-cli`.
