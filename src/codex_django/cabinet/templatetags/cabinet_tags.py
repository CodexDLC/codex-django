"""Cabinet template tags and filters.

Load this library in any cabinet template with::

    {% load cabinet_tags %}

Available tags and filters
--------------------------

**Filters:**

- :func:`get_item` — safe dict/object attribute access inside templates.
- :func:`cab_initials` — extract 1–2 character initials from a user object.

**Tags:**

- :func:`cab_trans` — defensive ``gettext`` wrapper; never raises even when
  ``USE_I18N = False`` or locale middleware is absent.
- :func:`cab_url` — defensive ``reverse``; returns ``"#"`` instead of raising
  ``NoReverseMatch`` when a URL name is not registered.

Design notes
------------
These helpers exist because library templates must not crash in projects
that have partial configurations (e.g. ``USE_I18N = False``, or a feature
URL not yet included in ``urls.py``). All functions degrade gracefully.
"""

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="jsonify")
def jsonify(obj: Any) -> str:
    """
    Converts a Python object (including dataclasses) to a JSON string.
    Useful for passing data to Alpine.js x-data attributes.
    """
    if is_dataclass(obj) and not isinstance(obj, type):
        obj = asdict(obj)
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))  # nosec


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


@register.filter(name="get_item")
def get_item(obj: object, key: str) -> object:
    """Return ``obj[key]`` for dicts or ``getattr(obj, key)`` for objects.

    Used in cabinet component templates to read dynamic column keys from
    row dicts without raising ``KeyError`` or ``AttributeError``.

    Args:
        obj: A dict-like object or any Python object.
        key: The key (for dicts) or attribute name (for objects) to look up.

    Returns:
        ``obj[key]`` if ``obj`` is a dict, otherwise ``getattr(obj, key)``.
        Returns ``""`` if ``obj`` is ``None`` or the key/attribute is absent.

    Example::

        {# In data_table.html — col.key is dynamic #}
        {{ row|get_item:col.key }}

        {# Equivalent Python #}
        row.get(col.key, "")
    """
    if obj is None:
        return ""
    if isinstance(obj, dict):
        return obj.get(key, "")
    return getattr(obj, key, "")


@register.filter(name="cab_initials")
def cab_initials(user: object) -> str:
    """Extract 1–2 character uppercase initials from a Django user object.

    Used by ``_avatar.html`` and card/list components to render avatar
    circles when no profile photo is available.

    Resolution order:

    1. ``first_name[0] + last_name[0]`` if either is set.
    2. ``username[:2]`` if username is set.
    3. ``"?"`` as final fallback.

    Args:
        user: Any object with optional ``first_name``, ``last_name``, and
            ``username`` attributes. Typically a Django ``AbstractUser``
            instance or ``request.user``.

    Returns:
        Uppercase initials string, 1–2 characters. Never raises.

    Example::

        {{ request.user|cab_initials }}  {# → "ИП" for "Иван Петров" #}
        {{ request.user|cab_initials }}  {# → "AD" for username "admin" #}
    """
    if user is None:
        return "?"
    first = getattr(user, "first_name", "") or ""
    last = getattr(user, "last_name", "") or ""
    if first or last:
        return (first[:1] + last[:1]).upper()
    username = getattr(user, "username", "") or ""
    return username[:2].upper() if username else "?"


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


@register.simple_tag
def cab_trans(text: str) -> str:
    """Translate a string defensively — never raises, even without i18n setup.

    Library templates use ``{% cab_trans "..." %}`` instead of Django's
    ``{% trans "..." %}`` because ``{% trans %}`` raises ``TemplateSyntaxError``
    when ``USE_I18N = False`` or ``LocaleMiddleware`` is absent.

    If ``USE_I18N = True`` and Django's translation machinery is available,
    the string is translated via ``gettext``. Otherwise the original string
    is returned as-is.

    Args:
        text: The string literal to translate.

    Returns:
        Translated string, or ``text`` unchanged if i18n is unavailable.
        Never raises.

    Example::

        {% load cabinet_tags %}
        {% cab_trans "Settings" %}        {# → "Настройки" with ru locale #}
        {% cab_trans "No data" %}         {# → "No data" if USE_I18N=False #}
    """
    try:
        from django.conf import settings

        if getattr(settings, "USE_I18N", False):
            from django.utils.translation import gettext

            return gettext(text)
    except Exception:
        return text
    return text


@register.simple_tag
def cab_url(url_name: str, *args: object, **kwargs: object) -> str:
    """Reverse a URL name defensively — returns ``"#"`` on ``NoReverseMatch``.

    Library templates use ``{% cab_url "..." %}`` instead of Django's
    ``{% url "..." %}`` because ``{% url %}`` raises ``NoReverseMatch``
    when a feature app's URLs are not included in the project's ``urls.py``.
    This allows library templates to render without crashing in projects
    where optional features are not yet installed.

    Args:
        url_name: Named URL to reverse, e.g. ``"cabinet:site_settings"``,
            ``"booking:schedule"``.
        *args: Positional arguments forwarded to ``django.urls.reverse``.
        **kwargs: Keyword arguments forwarded to ``django.urls.reverse``.

    Returns:
        Resolved URL string, e.g. ``"/cabinet/settings/"``.
        Returns ``"#"`` if the URL name is not registered or reversal fails
        for any reason.

    Example::

        {% load cabinet_tags %}
        <a href="{% cab_url 'booking:schedule' %}">Schedule</a>
        {# → href="/cabinet/booking/"  if booking URLs are installed  #}
        {# → href="#"                  if not installed yet            #}
    """
    try:
        from django.urls import reverse

        return reverse(url_name, args=args, kwargs=kwargs)
    except Exception:
        return "#"


@register.simple_tag(takes_context=True)
def sidebar_badge(context: dict[str, Any], badge_key: str) -> str:
    """Resolve a SidebarItem badge_key from the current template context.

    SidebarItem can declare ``badge_key="unread_messages_count"`` and the
    sidebar template calls ``{% sidebar_badge item.badge_key %}`` to look up
    the real value from the context.  If the key is absent or empty the tag
    returns an empty string so the badge is not rendered.

    Args:
        context: Template context (injected automatically by Django).
        badge_key: String key to look up in the context, e.g.
            ``"unread_messages_count"``.

    Returns:
        String representation of the value, or ``""`` if not found / falsy.

    Example::

        {# In _sidebar_staff.html #}
        {% sidebar_badge item.badge_key as badge_val %}
        {% include "_nav_item.html" with item=item badge=badge_val %}
    """
    if not badge_key:
        return ""
    val = context.get(badge_key, "")
    return str(val) if val else ""
