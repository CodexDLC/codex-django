<!-- DOC_TYPE: CONCEPT -->

# CLI Blueprints

## Назначение

Директория `blueprints/` это база знаний генерации для CLI.
Если `CLIEngine` выступает как renderer, то blueprints это тот архитектурный материал, который он рендерит.

Они задают не только содержимое файлов, но и саму топологию выходного проекта.
Поэтому blueprints ближе к декларативной системе сборки, чем к обычной папке с шаблонами.

## Почему Blueprints Так Важны

Самое важное в CLI это не само меню.
Самое важное то, что структура проекта, подключение feature-сценариев и deploy-файлы строятся из переиспользуемых blueprint-деревьев.

Это означает, что архитектура CLI по своей сути template-centric:

- commands выбирают blueprint
- engine рендерит его с context
- сгенерированное дерево становится частью целевого проекта

Поэтому понять CLI значит понять, как разделены blueprints.

## Верхнеуровневые Семейства Blueprints

Сейчас пространство blueprints разделено на пять основных семейств:

- `repo`
- `project`
- `apps`
- `features`
- `deploy`

Это не случайные папки.
Они соответствуют разным уровням ответственности в выходной структуре.

### `repo`

`repo/` содержит repository-level scaffolding.
Это внешняя оболочка сгенерированного проекта, в которую входят файлы вроде:

- `pyproject.toml`
- `README.md`
- `.env.example`
- `.gitignore`
- repo-level docs и tools

Этот слой отвечает на вопрос:
"Какие файлы относятся ко всему репозиторию в целом, независимо от внутреннего Django app tree?"

### `project`

`project/` содержит базовый Django project scaffold, который попадает в `src/<project_name>/`.
Сюда входят стартовые структуры для:

- `core`
- `system`
- `cabinet`
- `features`
- `templates`
- `static`
- `manage.py`

Это центральное семейство blueprints, потому что именно оно задает исходную runtime-архитектуру нового codex-django проекта.

### `apps`

`apps/` содержит переиспользуемые blueprints для добавления обычного feature app в уже существующий проект.
Текущий default app blueprint создает структуру `features/<app_name>/` с ожидаемой внутренней раскладкой для admin, forms, models, services, templates, tests и views.

Этот слой отвечает на вопрос:
"Как добавить один обычный app в канонической форме codex-django?"

### `features`

`features/` содержит advanced или compound feature scaffolds, например:

- `booking`
- `client_cabinet`
- `notifications`

Эти blueprints архитектурно шире, чем `apps/default`, потому что часто затрагивают сразу несколько целевых зон.

Например:

- booking изменяет `booking/`, `system/`, `cabinet/` и public templates
- notifications делит вывод между feature-слоем и ARQ-инфраструктурой
- client cabinet внедряет код и в `cabinet`, и в `system`

Поэтому `features/` это слой, где CLI выражает не отдельные приложения, а cross-cutting feature bundles.

### `deploy`

`deploy/` содержит scaffolding для deployment-инфраструктуры, например Docker-файлы.
Этот слой вынесен отдельно от `project/`, потому что operational output живет по другому lifecycle, чем runtime application code.

Он отвечает на вопрос:
"Какая эксплуатационная инфраструктура должна быть сгенерирована вокруг проекта?"

## Архитектурный Паттерн

Иерархия blueprints показывает скрытую модель генерации:

1. сгенерировать repository shell
2. сгенерировать базовый project
3. при необходимости добавить cross-cutting features
4. при необходимости добавить стандартные apps
5. при необходимости сгенерировать deploy-support

Это не просто pipeline копирования файлов.
Это staged project-construction model.

## Jinja И Структурная Семантика

Blueprints это не просто набор файлов:

- `.j2` файлы рендерятся по context
- обычные файлы копируются как есть
- расположение папок кодирует, куда generated code должен попасть

Это значит, что дерево blueprints одновременно несет два вида смысла:

- content semantics: что должно быть внутри файла
- placement semantics: где этот файл должен оказаться в итоговой архитектуре

## Runtime Flow

```mermaid
flowchart TD
    A["CLI command"] --> B["select blueprint family"]
    B --> C["CLIEngine.scaffold(...)"]
    C --> D["walk blueprint tree"]
    D --> E["render .j2 files with context"]
    D --> F["copy static files"]
    E --> G["target project structure"]
    F --> G
```

## Роль В CLI

Blueprints это самая долговечная часть CLI-архитектуры.
Menus, commands и prompts могут меняться, но именно blueprint families задают долгосрочный контракт того, что инструмент умеет генерировать.

Поэтому документация по blueprints важна даже в случае, если CLI позже станет отдельным пакетом:
именно blueprints кодируют реальную форму генерируемой экосистемы.

## См. Также

- [CLI index](/C:/install/projects/codex_tools/codex-django/docs/ru/architecture/cli/index.md)
- [обзор cabinet](/C:/install/projects/codex_tools/codex-django/docs/ru/architecture/cabinet.md)
- [обзор booking](/C:/install/projects/codex_tools/codex-django/docs/ru/architecture/booking.md)
