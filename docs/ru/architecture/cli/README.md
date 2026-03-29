<!-- DOC_TYPE: INDEX -->

# CLI Архитектура Переехала

Полная документация по архитектуре CLI теперь живет в companion package `codex-django-cli`.

В runtime-репозитории эти страницы остаются только как migration stubs, чтобы старые ссылки не ломались мгновенно.

## Что Еще Есть Здесь

- временные compatibility shims под `codex_django.cli`
- runtime-модули, которые импортируют generated projects
- guide-страницы, объясняющие границу между runtime и CLI

## Куда Смотреть Дальше

- исходники `codex-django-cli` для реальной реализации
- документация `codex-django-cli` для commands, engine, blueprints и project generation
- [Runtime и CLI](../../guides/runtime-vs-cli.md) для объяснения границы со стороны runtime-пакета
