# codex-django

Django utilities, mixins, adapters and CLI scaffolding for Codex projects.

## Installation

```bash
pip install codex-django
```

With optional extras:

```bash
pip install codex-django[platform]       # + codex-platform integration
pip install codex-django[notifications]  # + async SMTP
pip install codex-django[all]            # everything
```

## Structure

- `codex_django.cli` — project scaffolding CLI (`codex-django startproject`)
- `codex_django.mixins` — reusable Django model mixins
- `codex_django.notifications` — DjangoMailChannel and notification helpers
- `codex_django.adapters` — bridges to codex-platform, codex-booking, etc.
