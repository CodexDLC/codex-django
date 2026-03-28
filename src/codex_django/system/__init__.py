"""System-level abstractions for project configuration and shared content.

This package contains reusable model mixins and helpers for:

- site settings stored in the database and mirrored to Redis
- editable static translations
- static SEO metadata
- user profile extensions
- content update command infrastructure

Examples:
    Compose a concrete site settings model in a project app::

        from codex_django.system.mixins import (
            AbstractSiteSettings,
            SiteContactSettingsMixin,
            SiteSocialSettingsMixin,
        )

        class SiteSettings(
            AbstractSiteSettings,
            SiteContactSettingsMixin,
            SiteSocialSettingsMixin,
        ):
            pass
"""
