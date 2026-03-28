"""Core building blocks for codex-django projects.

The :mod:`codex_django.core` package groups lightweight primitives that are
shared across the rest of the library:

- reusable model mixins
- sitemap helpers
- SEO selectors
- Redis-backed support utilities
- template-level helpers such as context processors and tags

Examples:
    Use the mixins module in a project model::

        from codex_django.core.mixins.models import TimestampMixin, SeoMixin

        class Article(TimestampMixin, SeoMixin):
            ...

    Register the SEO context processor in Django settings::

        TEMPLATES[0]["OPTIONS"]["context_processors"].append(
            "codex_django.core.context_processors.seo_settings"
        )
"""
