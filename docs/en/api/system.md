<!-- DOC_TYPE: API -->

# System Public API

The `system` package contains the model mixins and infrastructure that back project-level settings, static content, and shared operational commands.

## Start here

- `codex_django.system.mixins` for public re-exports of site settings, SEO, translation, integration, and user-profile mixins.
- `codex_django.system.context_processors` for template access to cached settings and static content.
- `codex_django.system.management.base_commands` for reusable content update command bases.
- `codex_django.system.management` for public command seams such as `JsonFixtureUpsertCommand` and `SingletonFixtureUpdateCommand`.
- `codex_django.system.redis.managers` for fixture hash tracking and `JsonActionTokenRedisManager`.

## Example

```python
from codex_django.system.mixins import AbstractSiteSettings, SiteContactSettingsMixin
from codex_django.system.management import JsonFixtureUpsertCommand, SingletonFixtureUpdateCommand
from codex_django.system.redis.managers import JsonActionTokenRedisManager
```

For the full generated module documentation, open [System internals](internal/system.md).
