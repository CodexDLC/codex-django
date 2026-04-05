from unittest.mock import MagicMock

import pytest

from codex_django.cabinet.templatetags.cabinet_tags import (
    cab_initials,
    cab_trans,
    cab_url,
    get_item,
    jsonify,
    sidebar_badge,
)


@pytest.mark.unit
def test_get_item():
    assert get_item({"a": 1}, "a") == 1
    assert get_item({"a": 1}, "b") == ""
    assert get_item(None, "a") == ""


@pytest.mark.unit
def test_cab_initials():
    user = MagicMock()
    user.first_name = "Ivan"
    user.last_name = "Petrov"
    assert cab_initials(user) == "IP"

    user.first_name = ""
    user.last_name = ""
    user.username = "admin"
    assert cab_initials(user) == "AD"


@pytest.mark.unit
def test_cab_trans():
    # Simple test without setting up i18n
    assert cab_trans("Hello") == "Hello"


@pytest.mark.unit
def test_cab_url():
    # Defensive reversal test
    assert cab_url("nonexistent") == "#"


@pytest.mark.unit
def test_sidebar_badge():
    ctx = {"unread": 5}
    assert sidebar_badge(ctx, "unread") == "5"
    assert sidebar_badge(ctx, "") == ""
    assert sidebar_badge(ctx, "missing") == ""


@pytest.mark.unit
def test_jsonify():
    from dataclasses import dataclass

    @dataclass
    class D:
        a: int

    assert '{"a": 1}' in jsonify(D(a=1))
