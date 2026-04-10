"""Unit tests for BaseEmailContentSelector."""

import pytest

from codex_django.notifications.selector import BaseEmailContentSelector

pytestmark = pytest.mark.unit


@pytest.fixture
def selector(mock_model, mock_cache_adapter, mock_i18n_adapter):
    return BaseEmailContentSelector(
        model=mock_model,
        cache_adapter=mock_cache_adapter,
        i18n_adapter=mock_i18n_adapter,
    )


# ---------------------------------------------------------------------------
# Cache hit
# ---------------------------------------------------------------------------


class TestBaseEmailContentSelectorCacheHit:
    def test_returns_cached_value_without_db_query(self, selector, mock_model, mock_cache_adapter):
        mock_cache_adapter.get.return_value = "Booking Confirmed"
        result = selector.get("booking_subject", "de")
        assert result == "Booking Confirmed"
        mock_model.objects.get.assert_not_called()

    def test_cache_key_format(self, selector, mock_cache_adapter):
        mock_cache_adapter.get.return_value = "cached"
        selector.get("booking_subject", "de")
        mock_cache_adapter.get.assert_called_once_with("booking_subject:de")

    def test_cache_key_includes_language(self, selector, mock_cache_adapter):
        mock_cache_adapter.get.return_value = "Buchung"
        selector.get("my_key", "ru")
        mock_cache_adapter.get.assert_called_once_with("my_key:ru")


# ---------------------------------------------------------------------------
# Cache miss — DB lookup
# ---------------------------------------------------------------------------


class TestBaseEmailContentSelectorCacheMiss:
    def test_queries_db_on_cache_miss(self, selector, mock_model, mock_cache_adapter):
        mock_cache_adapter.get.return_value = None
        mock_obj = type("Obj", (), {"text": "Subject text"})()
        mock_model.objects.get.return_value = mock_obj
        result = selector.get("booking_subject", "de")
        mock_model.objects.get.assert_called_once_with(key="booking_subject")
        assert result == "Subject text"

    def test_stores_db_result_in_cache(self, selector, mock_model, mock_cache_adapter):
        mock_cache_adapter.get.return_value = None
        mock_obj = type("Obj", (), {"text": "Subject text"})()
        mock_model.objects.get.return_value = mock_obj
        selector.get("booking_subject", "de")
        mock_cache_adapter.set.assert_called_once_with("booking_subject:de", "Subject text", 3600)

    def test_translation_override_called_with_language(
        self, selector, mock_model, mock_cache_adapter, mock_i18n_adapter
    ):
        mock_cache_adapter.get.return_value = None
        mock_obj = type("Obj", (), {"text": "val"})()
        mock_model.objects.get.return_value = mock_obj
        selector.get("key", "ru")
        mock_i18n_adapter.translation_override.assert_called_once_with("ru")

    def test_returns_none_when_key_not_in_db(self, selector, mock_model, mock_cache_adapter):
        mock_cache_adapter.get.return_value = None
        mock_model.objects.get.side_effect = mock_model.DoesNotExist
        result = selector.get("missing_key", "de")
        assert result is None

    def test_does_not_cache_none_result(self, selector, mock_model, mock_cache_adapter):
        mock_cache_adapter.get.return_value = None
        mock_model.objects.get.side_effect = mock_model.DoesNotExist
        selector.get("missing_key", "de")
        mock_cache_adapter.set.assert_not_called()

    def test_cache_timeout_is_3600(self, selector, mock_model, mock_cache_adapter):
        mock_cache_adapter.get.return_value = None
        mock_obj = type("Obj", (), {"text": "val"})()
        mock_model.objects.get.return_value = mock_obj
        selector.get("key", "de")
        _, args, _ = mock_cache_adapter.set.mock_calls[0]
        # set(cache_key, value, timeout) — positional
        assert args[2] == 3600


# ---------------------------------------------------------------------------
# Invalidate
# ---------------------------------------------------------------------------


class TestBaseEmailContentSelectorInvalidate:
    def test_invalidate_sets_empty_string_with_zero_timeout(self, selector, mock_cache_adapter):
        selector.invalidate("booking_subject", "de")
        mock_cache_adapter.set.assert_called_once_with("booking_subject:de", "", timeout=0)

    def test_cache_key_used_in_invalidate(self, selector, mock_cache_adapter):
        selector.invalidate("my_key", "ru")
        mock_cache_adapter.set.assert_called_once_with("my_key:ru", "", timeout=0)

    def test_invalidate_different_languages_independent(self, selector, mock_cache_adapter):
        selector.invalidate("key", "de")
        selector.invalidate("key", "ru")
        calls = [c[0][0] for c in mock_cache_adapter.set.call_args_list]
        assert "key:de" in calls
        assert "key:ru" in calls


# ---------------------------------------------------------------------------
# Custom subclass — cache_key_prefix
# ---------------------------------------------------------------------------


class TestBaseEmailContentSelectorCustomPrefix:
    def test_custom_prefix_in_cache_key(self, mock_model, mock_cache_adapter, mock_i18n_adapter):
        class PrefixedSelector(BaseEmailContentSelector):
            cache_key_prefix = "notif:"

        sel = PrefixedSelector(
            model=mock_model,
            cache_adapter=mock_cache_adapter,
            i18n_adapter=mock_i18n_adapter,
        )
        # cache_key_prefix is prepended verbatim — include a separator in the
        # prefix itself (e.g. "notif:") to produce "notif:booking_subject:de".
        mock_cache_adapter.get.return_value = "hit"
        sel.get("booking_subject", "de")
        mock_cache_adapter.get.assert_called_once_with("notif:booking_subject:de")
