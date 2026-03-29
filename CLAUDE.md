# CLAUDE.md — codex-django

> Читать в начале каждой сессии. Содержит ориентацию по проекту, памяти и ветках.

---

## Расположение проекта

```
C:\install\projects\codex_tools\codex-django\
```

Все codex-* библиотеки — соседи на одном уровне:
```
C:\install\projects\codex_tools\
  codex-core\
  codex-platform\
  codex-services\
  codex-django\      ← этот проект
  codex-bot\
```

---

## Файлы памяти (локальные)

```
C:\Users\prime\.claude\projects\C--install-projects-codex-tools-codex-django\memory\
```

| Файл | Содержимое |
|------|-----------|
| `MEMORY.md` | Мастер-индекс. Читать первым. |
| `claude_context.md` | Стиль работы, частые ошибки, активные проекты |
| `roadmap_overview.md` | 8 блоков доделки, порядок, статусы |
| `roadmap_block1.md` | ✅ Git hygiene + стабы |
| `roadmap_block2.md` | Тесты: booking + notifications |
| `roadmap_block3.md` | Тесты: system + core |
| `roadmap_block4.md` | Cabinet: widget adapter + client cabinet |
| `roadmap_block5.md` | i18n валидация |
| `roadmap_block6.md` | Booking: мульти-сервис |
| `roadmap_block7.md` | Docs + PyPI alpha |
| `roadmap_block8.md` | Deploy blueprints + Showcase |
| `cabinet_index.md` | Архитектура кабинета |
| `cabinet_css_js.md` | CSS/JS стек |
| `cabinet_dashboard_architecture.md` | DashboardSelector, Redis, adapter pattern |
| `project_ecosystem.md` | Экосистема codex-*, lily_website |
| `project_test_conventions.md` | Уровни тестов, команды запуска |

---

## MCP граф памяти (полная версия)

Сервер: `memory` (MCP)

```python
# Старт навигации всегда с:
search_nodes("MASTER_INDEX")
```

### Ключевые ноды по проекту:

| Нода | Тип | Содержит |
|------|-----|---------|
| `MASTER_INDEX` | Index | 7 секций (SEC:*) |
| `SEC:Architecture` | IndexSection | Архитектурные решения |
| `codex-django:architecture:project` | Architecture | Структура, ветки, пути |
| `codex-django:architecture:cabinet` | Architecture | CabinetApp дизайн |
| `codex-django:architecture:cli-blueprint` | Architecture | Blueprint система |
| `codex-django:cabinet:index` | project-index | Кабинет: подход и принципы |
| `codex-django:cabinet:css-js` | conventions | CSS/JS стек, компилер |
| `Claude:Index` | PersonalNotes | Стиль работы, уроки |
| `Graph:ConventionStandard` | Standard | Правила именования нод |

---

## Git ветки

| Ветка | Назначение |
|-------|-----------|
| `main` | Стабильный релиз (PyPI) |
| `develop` | Активная разработка — **все коммиты сюда** |

> **Важно:** merge в `main` только перед релизом (Block 7 — PyPI alpha).
> Сейчас работаем в `develop`. Не пушим (`git push` запрещён без явного запроса).

---

## Quality gate

```bash
# Полная проверка (интерактивный — спросит про integration тесты):
python tools/dev/check.py --all

# Только lint:
python tools/dev/check.py --lint

# Только типы:
python tools/dev/check.py --types

# Только тесты:
python tools/dev/check.py --tests unit
```

**Текущий статус gate (после Block 1):**
- Lint (ruff + bandit) ✅
- Mypy ✅ (93 файла, 0 ошибок)
- pip-audit ✅ (CVE-2026-4539 pygments — no fix, ignored)
- Unit tests ✅ 153 passed, coverage ~35%

---

## Roadmap статус

| # | Блок | Статус |
|---|------|--------|
| 1 | Git hygiene + стабы | ✅ |
| 2 | Тесты: booking + notifications | ⬜ |
| 3 | Тесты: system + core | ⬜ |
| 4 | Cabinet: widget adapter | ⬜ |
| 5 | i18n валидация | ⬜ |
| 6 | Booking мульти-сервис | ⬜ |
| 7 | Docs + PyPI | ⬜ |
| 8 | Deploy + Showcase | ⬜ |

---

## Как стартовать новую сессию

1. Прочитай этот файл
2. Прочитай `memory/roadmap_overview.md`
3. Прочитай нужный `memory/roadmap_blockN.md`
4. По необходимости: `search_nodes("MASTER_INDEX")` для полного контекста
