"""Context processors for cross-project core concerns.

Currently this module provides template access to resolved static-page SEO
metadata so frontend templates can render canonical titles and descriptions
without repeating selector logic in views.
"""

import logging
from typing import Any

from django.http import HttpRequest

from codex_django.core.seo.selectors import get_static_page_seo

log = logging.getLogger(__name__)


def seo_settings(request: HttpRequest) -> dict[str, Any]:
    """Expose SEO metadata for the current resolved page in templates.

    The returned mapping is injected into the template context as ``seo``.
    The processor expects ``CODEX_STATIC_PAGE_SEO_MODEL`` to point to a
    model that can be consumed by
    :func:`codex_django.core.seo.selectors.get_static_page_seo`.

    Args:
        request: Incoming Django request used to resolve the current URL name.

    Returns:
        A template context mapping with the ``seo`` key. Returns an empty
        dictionary payload when the current route cannot be resolved or when
        no SEO data is available for the page.
    """
    # Try to determine page key from URL name
    url_name = request.resolver_match.url_name if request.resolver_match else None
    if not url_name:
        return {"seo": {}}

    # get_static_page_seo handles all exceptions internally and returns None on failure
    data = get_static_page_seo(url_name)
    return {"seo": data or {}}
