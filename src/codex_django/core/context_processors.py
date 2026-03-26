import logging
from typing import Any

from django.http import HttpRequest

from codex_django.core.seo.selectors import get_static_page_seo

log = logging.getLogger(__name__)


def seo_settings(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor for accessing SEO settings for the current page.
    The object {{ seo }} is available in templates.

    Requires setting CODEX_STATIC_PAGE_SEO_MODEL = 'app.ModelName' in settings.py.
    """
    # Try to determine page key from URL name
    url_name = request.resolver_match.url_name if request.resolver_match else None
    if not url_name:
        return {"seo": {}}

    # get_static_page_seo handles all exceptions internally and returns None on failure
    data = get_static_page_seo(url_name)
    return {"seo": data or {}}
