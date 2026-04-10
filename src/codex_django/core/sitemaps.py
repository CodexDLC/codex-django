"""Sitemap primitives with codex-django defaults.

The base sitemap centralizes canonical-domain handling, multilingual URL
generation, and namespace-aware reverse lookups so project sitemaps can stay
small and focused.
"""

from typing import Any

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import NoReverseMatch, reverse
from django.utils import translation


class BaseSitemap(Sitemap):  # type: ignore[type-arg]
    """Base sitemap with Codex defaults for multilingual canonical URLs.

    The implementation enables Django's i18n sitemap mode, forces canonical
    HTTPS URLs, and centralizes domain resolution through
    ``settings.CANONICAL_DOMAIN``.
    """

    i18n = True
    x_default = True

    @property
    def languages(self) -> list[str]:  # type: ignore[override]
        return [lang[0] for lang in settings.LANGUAGES]

    def get_domain(self, site: Any = None) -> str:
        # Always use the canonical domain from settings (strip protocol if present)
        domain = getattr(settings, "CANONICAL_DOMAIN", "localhost")
        if "://" in domain:
            return domain.split("://")[-1]
        return domain

    def get_x_default_language(self) -> str:
        """Return the language used for the sitemap ``x-default`` alternate."""
        return getattr(settings, "SITEMAP_DEFAULT_LANGUAGE", getattr(settings, "LANGUAGE_CODE", "en"))

    def build_alternates(self, item: Any, domain: str | None = None) -> list[dict[str, str]]:
        """Build alternate language URLs for a sitemap item.

        Args:
            item: Sitemap item to resolve for every configured language.
            domain: Optional already-resolved canonical domain.

        Returns:
            Alternate URL dictionaries in Django sitemap-compatible shape.
        """
        actual_item: Any = item[0] if isinstance(item, list | tuple) else item
        resolved_domain = domain or self.get_domain()
        alternates: list[dict[str, str]] = []

        for lang in self.languages:
            with translation.override(lang):
                loc = self.location(actual_item)
            alternates.append({"lang_code": lang, "location": f"https://{resolved_domain}{loc}"})

        with translation.override(self.get_x_default_language()):
            alternates.append(
                {"lang_code": "x-default", "location": f"https://{resolved_domain}{self.location(actual_item)}"}
            )

        return alternates

    def get_urls(self, page: int | str = 1, site: Any = None, protocol: str | None = None) -> list[dict[str, Any]]:
        # Force HTTPS and use our canonical domain
        domain = self.get_domain(site)
        # We pass protocol="https" to the original get_urls
        urls: list[dict[str, Any]] = super().get_urls(page=page, site=None, protocol="https")

        for url_info in urls:
            url_info["alternates"] = self.build_alternates(url_info["item"], domain=domain)

        return urls

    def location(self, item: Any) -> str:
        """Resolve sitemap items to absolute path components.

        String items are treated as URL pattern names and are first reversed
        directly, then retried against namespaces listed in
        ``settings.SITEMAP_LOOKUP_NAMESPACES``. Non-string items are expected
        to implement ``get_absolute_url()``.

        Args:
            item: Sitemap item emitted by Django. In i18n mode Django may pass
                either the raw item or an ``(item, language)`` pair.

        Returns:
            The resolved path component for the sitemap entry.

        Raises:
            django.urls.NoReverseMatch: If a string item cannot be reversed
                directly or through the configured namespace fallbacks.
        """
        actual_item: Any = item[0] if isinstance(item, list | tuple) else item
        if isinstance(actual_item, str):
            try:
                return reverse(actual_item)
            except NoReverseMatch:
                # Common pattern in Codex projects: check if it's in a namespace
                # You might want to customize this list in subclasses or settings
                namespaces: list[str] = getattr(settings, "SITEMAP_LOOKUP_NAMESPACES", [])
                for ns in namespaces:
                    try:
                        return reverse(f"{ns}:{actual_item}")
                    except NoReverseMatch:
                        continue
                # If still not found, let the final retry raise or return original attempt
                return reverse(actual_item)

        # Assuming actual_item has a get_absolute_url method if it's not a string
        return actual_item.get_absolute_url()  # type: ignore[no-any-return]


class StaticPagesSitemap(BaseSitemap):
    """Sitemap for static route-name pages configured through Django settings."""

    priority = 0.8
    changefreq = "monthly"
    setting_name = "SITEMAP_STATIC_PAGES"
    default_items = ("home",)

    def items(self) -> list[str]:
        """Return configured static page URL names."""
        return list(getattr(settings, self.setting_name, self.default_items))
