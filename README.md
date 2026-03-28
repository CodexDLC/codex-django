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
# Core package
pip install codex-django

# Notifications stack (ARQ + SMTP helpers)
pip install "codex-django[notifications]"

# Redis integration helpers
pip install "codex-django[django-redis]"

# All runtime extras
pip install "codex-django[all]"
```

Requires Python 3.12 or newer.

## Project Scaffolding

The `codex-django` runtime package no longer owns the CLI implementation.
Use the companion package when you want to scaffold or extend a project:

```bash
pip install codex-django-cli
codex-django init myproject
codex-django add-client-cabinet --project myproject
```

Temporary compatibility shims remain under `codex_django.cli`, but the real CLI code lives in `codex-django-cli`.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run mypy src/
uv run pre-commit run --all-files
uv build --no-sources
```

## Quick Start

### Runtime Example

```python
from datetime import date

from codex_django.booking import DjangoAvailabilityAdapter
from codex_django.booking.selectors import get_available_slots

adapter = DjangoAvailabilityAdapter(
    master_model=Master,
    appointment_model=Appointment,
    service_model=Service,
    working_day_model=MasterWorkingDay,
    day_off_model=MasterDayOff,
    booking_settings_model=BookingSettings,
    site_settings_model=SiteSettings,
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
- `notifications`: notification content models, service hooks, and ARQ client scaffolding.

## Modules

| Module | Extra | Description |
| :--- | :--- | :--- |
| `codex_django.core` | - | Shared Django infrastructure: mixins, SEO access path, i18n helpers, sitemap base, Redis managers. |
| `codex_django.system` | - | Project-state models and admin workflows: site settings, static content, integrations, fixture orchestration. |
| `codex_django.notifications` | `[notifications]` | Django notification orchestration: content selector, payload builder, queue/direct adapters. |
| `codex_django.booking` | - | Django adapter layer over `codex-services` booking engine: model mixins, availability adapter, booking selectors. |
| `codex_django.cabinet` | - | Reusable cabinet/dashboard framework with registry-based navigation, widgets, and cached settings. |
| `codex_django.cli` | compat only | Temporary forwarding layer to `codex-django-cli`; not part of the long-term runtime surface. |
| `codex_django.showcase` | - | DEBUG-only showcase layer for demo screens and generated-project previews backed by mock data. |

## Documentation

Full docs with architecture, API reference, and generated project structure:

**[https://codexdlc.github.io/codex-django/](https://codexdlc.github.io/codex-django/)**

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
