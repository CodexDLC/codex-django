"""Template tags for multilingual navigation helpers.

The tags in this module are intentionally small wrappers around Django's i18n
utilities so templates can stay declarative.
"""

from typing import Any

from django import template

from codex_django.core.i18n import translate_current_url

register = template.Library()


@register.simple_tag(takes_context=True)
def translate_url(context: dict[str, Any], lang_code: str) -> str:
    """Translate the current request path into another active language.

    Args:
        context: Template context expected to contain the current ``request``.
        lang_code: Target Django language code.

    Returns:
        The translated URL path for the current request, or an empty string
        when the request is unavailable.
    """
    return translate_current_url(context, lang_code)
