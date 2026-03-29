<!-- DOC_TYPE: API -->

# Core Public API

The `core` package is a toolbox layer. It does not provide one large facade object, so the public API is better understood as a set of stable module entrypoints.

## Start here

- `codex_django.core.mixins.models` for reusable model mixins such as timestamps, slugs, UUIDs, SEO, and soft-delete helpers.
- `codex_django.core.context_processors` for template-level SEO injection.
- `codex_django.core.sitemaps` for multilingual sitemap base classes.
- `codex_django.core.seo.selectors` for cached static-page SEO lookups.
- `codex_django.core.i18n.discovery` for `LOCALE_PATHS` discovery in generated projects.

## Example

```python
from codex_django.core.mixins.models import TimestampMixin, SeoMixin
from codex_django.core.sitemaps import BaseSitemap
```

For the full generated module documentation, open [Core internals](internal/core.md).
