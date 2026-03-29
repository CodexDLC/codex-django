<!-- DOC_TYPE: CONCEPT -->

# Модуль CLI Переехал

`codex_django.cli` больше не реализуется внутри этого runtime-репозитория.

Реальный CLI-модуль теперь живет в `codex-django-cli`, а в `codex-django` остались только compatibility shims под `codex_django.cli` на период миграции.

## Что Важно Со Стороны Runtime

Generated projects по-прежнему импортируют runtime-модули из `codex_django.*`.
Именно поэтому CLI и runtime все еще концептуально связаны даже после split-а.

## См. Также

- [CLI Архитектура Переехала](./README.md)
- [Runtime и CLI](../../guides/runtime-vs-cli.md)
