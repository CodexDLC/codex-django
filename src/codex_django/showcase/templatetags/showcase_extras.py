from typing import Any, Dict
from django import template

register = template.Library()

@register.filter
def get_item(dictionary: Dict[str, Any], key: str) -> Any:
    """{{ row|get_item:col.key }} — dict access with variable key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "—")
    return "—"
