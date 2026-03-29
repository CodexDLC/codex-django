<!-- DOC_TYPE: GUIDE -->

# Структура Проекта

## Что Создает CLI

После `codex-django init`, вызванного через `codex-django-cli`, вы работаете уже внутри generated Django-проекта, у которого обычно есть два крупных слоя:

1. repository-level файлы: зависимости, CI, docs, deployment assets;
2. runtime project code внутри `src/<project_name>/`.

## Runtime Project Layout

Внутри `src/<project_name>/` проект обычно растет вокруг таких зон:

- project settings и entrypoints;
- shared system/state apps;
- feature apps, которые добавляются позже scaffold-командами;
- templates, static assets и cabinet integration;
- operational helpers для admin wiring, URLs и background-task integration.

## Как Встраиваются Feature Scaffolds

Инкрементальные команды вроде booking, notifications и cabinet обычно добавляют не один файл, а сразу несколько слоев:

- app registration;
- models или settings models;
- admin wiring;
- URLs и templates;
- cabinet integration или selectors.

Именно поэтому follow-up checklist после команды настолько важен.

## Как Читать Документацию Вместе Со Структурой

- guide-layer отвечает на вопросы "куда это класть дальше?";
- architecture pages объясняют "почему проект разделен именно так?";
- API reference нужен только тогда, когда вы уже знаете нужный пакет или модуль.

## Связанные Страницы

- [Blueprint workflow](./blueprints-and-scaffolding.md)
- [Гайд по Booking](./booking.md)
- [Гайд по Cabinet](./cabinet.md)
