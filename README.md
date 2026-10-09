<!-- Type: LANDING -->
# codex-django

[![PyPI](https://img.shields.io/pypi/v/codex-django)](https://pypi.org/project/codex-django/)
[![Python](https://img.shields.io/pypi/pyversions/codex-django)](https://pypi.org/project/codex-django/)
[![CI](https://github.com/codexdlc/codex-django/actions/workflows/ci.yml/badge.svg)](https://github.com/codexdlc/codex-django/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](https://github.com/codexdlc/codex-django/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-codexdlc.github.io-blue)](https://codexdlc.github.io/codex-django/)

Django runtime integration layer for the Codex ecosystem: reusable modules, cabinet UI building blocks, and shared adapters for Codex-shaped Django projects.
Project scaffolding now lives in the companion package `codex-django-cli`, while this repository focuses on installable runtime code.

---

## Install

```bash
# Runtime library only
pip install codex-django

# Runtime + companion CLI package
pip install "codex-django[cli]"

# Optional admin theme and Prometheus integration
pip install "codex-django[admin,observability]"

# Runtime + CLI + day-to-day development toolchain
pip install "codex-django[dev]"
```

Requires Python 3.12 or newer.

## Project Scaffolding

The `codex-django` runtime package no longer owns the CLI implementation.
Use the companion package when you want to scaffold or extend a project:

```bash
pip install "codex-django[cli]"
# or: pip install codex-django-cli
codex-django init myproject
codex-django add-client-cabinet --project myproject
```

Temporary compatibility shims remain under `codex_django.cli`, but the real CLI code lives in `codex-django-cli`.

## Development

```bash
uv sync --extra maintainer
uv run pytest
uv run mypy src/
uv run pre-commit run --all-files
uv run python tools/dev/check.py --ci
uv build --no-sources
```

## Quick Start

### Runtime Example

```python
from datetime import date

from codex_django.booking import DjangoAvailabilityAdapter
from codex_django.booking.selectors import get_available_slots

adapter = DjangoAvailabilityAdapter(
    resource_model=Master,
    appointment_model=Appointment,
    service_model=Service,
    working_day_model=MasterWorkingDay,
    day_off_model=MasterDayOff,
    booking_settings_model=BookingSettings,
    timezone="UTC",
)

result = get_available_slots(
    adapter=adapter,
    service_ids=[1],
    target_date=date.today(),
)

print(result.get_unique_start_times())
```

### What Each Optional Module Adds

- `cabinet`: user-facing dashboard pages, profile/settings views, and cabinet adapters.
- `booking`: booking app scaffolds, booking settings, cabinet booking pages, and booking templates.
- `messaging`: content models, dispatch hooks, campaign primitives, and queue/direct delivery adapters.
- `notifications`: deprecated compatibility import path for older notification integrations.

## Modules

| Module | Extra | Description |
| :--- | :--- | :--- |
| `codex_django.core` | - | Shared Django infrastructure: mixins, SEO access path, i18n helpers, sitemap base, Redis managers. |
| `codex_django.system` | - | Project-state models and admin workflows: site settings, static content, integrations, fixture orchestration. |
| `codex_django.messaging` | - | Canonical Django messaging orchestration: selectors, payload builders, queue/direct adapters, campaigns, and cabinet contracts. |
| `codex_django.notifications` | compat only | Deprecated forwarding layer to `codex_django.messaging`; old imports continue during the migration window. |
| `codex_django.booking` | - | Django adapter layer over `codex-services` booking engine: model mixins, availability adapter, booking selectors. |
| `codex_django.cabinet` | - | Reusable cabinet/dashboard framework with registry-based navigation, widgets, and cached settings. |
| `codex_django.cli` | compat only | Temporary forwarding layer to `codex-django-cli`; not part of the long-term runtime surface. |
| `codex_django.showcase` | - | DEBUG-only showcase layer for demo screens and generated-project previews backed by mock data. |

## Agent Skills

`codex-django` includes an optional, offline agent skill installer. From the consuming project's root, use the Python environment where `codex-django` is installed:

```bash
python -m codex_django.agent_skills install --project .
python -m codex_django.agent_skills status --project .
```

After upgrading the package, refresh the installed instructions separately:

```bash
python -m pip install --upgrade codex-django
python -m codex_django.agent_skills update --project .
```

The installer manages `.agents/skills/codex-django/` and a bounded block in the project's root `AGENTS.md`. Skill installation is optional for normal Python use and requires neither Django configuration nor the `[cli]` extra. The [Agent Skills Guide](https://codexdlc.github.io/codex-django/en/guides/agent-skills/) covers removal, ownership, and recovery.

## Documentation

Full docs with architecture, API reference, and generated project structure:

**[https://codexdlc.github.io/codex-django/](https://codexdlc.github.io/codex-django/)**

- [Agent Skills Guide (EN)](https://codexdlc.github.io/codex-django/en/guides/agent-skills/) | [Руководство по агентским навыкам (RU)](https://codexdlc.github.io/codex-django/ru/guides/agent-skills/)

## Part of the Codex ecosystem

| Package | Role |
| :--- | :--- |
| [codex-core](https://github.com/codexdlc/codex-core) | Foundation — immutable DTOs, PII masking, env settings |
| [codex-platform](https://github.com/codexdlc/codex-platform) | Infrastructure — Redis, Streams, ARQ workers, Notifications |
| [codex-ai](https://github.com/codexdlc/codex-ai) | LLM layer — unified async interface for OpenAI, Gemini, Anthropic |
| [codex-services](https://github.com/codexdlc/codex-services) | Business logic — Booking engine, CRM, Calendar |

Each library is **fully standalone** — install only what your project needs.
Together they form the backbone of **[codex-bot](https://github.com/codexdlc/codex-bot)**
(Telegram AI-agent infrastructure built on aiogram) and
**codex-django** (Django integration layer and scaffolding toolkit).
