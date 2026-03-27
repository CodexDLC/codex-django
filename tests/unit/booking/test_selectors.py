"""Unit tests for booking selector functions."""

from datetime import UTC, date, datetime
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from codex_services.booking.slot_master.modes import BookingMode

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_adapter():
    """Mock DjangoAvailabilityAdapter with sensible defaults."""
    adapter = MagicMock()
    adapter.step_minutes = 30
    sr = MagicMock()
    sr.possible_resource_ids = ["1", "2"]
    request = MagicMock()
    request.service_requests = [sr]
    adapter.build_engine_request.return_value = request
    adapter.build_masters_availability.return_value = {"1": MagicMock(), "2": MagicMock()}
    adapter.lock_masters.return_value = None
    return adapter


@pytest.fixture
def mock_finder():
    """Patch ChainFinder and return the mock instance."""
    finder = MagicMock()
    engine_result = MagicMock()
    engine_result.get_unique_start_times.return_value = ["09:00", "09:30"]
    finder.find.return_value = engine_result
    finder.find_nearest.return_value = engine_result
    return finder, engine_result


# ---------------------------------------------------------------------------
# get_available_slots
# ---------------------------------------------------------------------------


class TestGetAvailableSlots:
    def test_calls_build_engine_request(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(mock_adapter, [1, 2], date(2025, 1, 6))
        mock_adapter.build_engine_request.assert_called_once_with(
            service_ids=[1, 2],
            target_date=date(2025, 1, 6),
            locked_master_id=None,
            master_selections=None,
            mode=BookingMode.SINGLE_DAY,
            overlap_allowed=False,
            parallel_groups=None,
        )

    def test_deduplicates_master_ids(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        sr = MagicMock()
        sr.possible_resource_ids = ["1", "1", "2"]
        mock_adapter.build_engine_request.return_value.service_requests = [sr]
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(mock_adapter, [1], date(2025, 1, 6))
        called_ids = mock_adapter.build_masters_availability.call_args[1]["master_ids"]
        assert sorted(called_ids) == [1, 2]
        assert len(called_ids) == len(set(called_ids))

    def test_calls_chain_finder_find(self, mock_adapter, mock_finder):
        finder, engine_result = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder) as finder_cls:
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(mock_adapter, [1], date(2025, 1, 6), max_solutions=10)
        finder_cls.assert_called_once_with(step_minutes=30)
        finder.find.assert_called_once()

    def test_returns_finder_result(self, mock_adapter, mock_finder):
        finder, engine_result = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            result = get_available_slots(mock_adapter, [1], date(2025, 1, 6))
        assert result is engine_result

    def test_passes_cache_ttl_to_availability(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(mock_adapter, [1], date(2025, 1, 6), cache_ttl=60)
        assert mock_adapter.build_masters_availability.call_args[1]["cache_ttl"] == 60

    def test_passes_locked_master_id(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(mock_adapter, [1], date(2025, 1, 6), locked_master_id=5)
        mock_adapter.build_engine_request.assert_called_once_with(
            service_ids=[1],
            target_date=date(2025, 1, 6),
            locked_master_id=5,
            master_selections=None,
            mode=BookingMode.SINGLE_DAY,
            overlap_allowed=False,
            parallel_groups=None,
        )

    def test_passes_max_solutions_to_finder(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(mock_adapter, [1], date(2025, 1, 6), max_solutions=5)
        call_kwargs = finder.find.call_args[1]
        assert call_kwargs["max_solutions"] == 5

    def test_passes_mode_overlap_and_parallel_groups(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_available_slots

            get_available_slots(
                mock_adapter,
                [5, 7],
                date(2026, 4, 1),
                mode=BookingMode.MULTI_DAY,
                overlap_allowed=True,
                parallel_groups={5: "A", 7: "B"},
            )

        mock_adapter.build_engine_request.assert_called_once_with(
            service_ids=[5, 7],
            target_date=date(2026, 4, 1),
            locked_master_id=None,
            master_selections=None,
            mode=BookingMode.MULTI_DAY,
            overlap_allowed=True,
            parallel_groups={5: "A", 7: "B"},
        )


# ---------------------------------------------------------------------------
# get_calendar_data
# ---------------------------------------------------------------------------


class TestGetCalendarData:
    def test_returns_matrix_from_calendar_engine(self):
        engine_module = ModuleType("codex_services.calendar.engine")
        engine_module.CalendarEngine = MagicMock()
        engine_module.CalendarEngine.get_month_matrix.return_value = [{"day": 1}]
        with patch.dict("sys.modules", {"codex_services.calendar.engine": engine_module}):
            from codex_django.booking.selectors import get_calendar_data

            result = get_calendar_data(2025, 1)
        assert result == [{"day": 1}]
        engine_module.CalendarEngine.get_month_matrix.assert_called_once()

    def test_uses_today_when_not_provided(self):
        engine_module = ModuleType("codex_services.calendar.engine")
        engine_module.CalendarEngine = MagicMock()
        engine_module.CalendarEngine.get_month_matrix.return_value = []
        with patch.dict("sys.modules", {"codex_services.calendar.engine": engine_module}):
            from codex_django.booking.selectors import get_calendar_data

            get_calendar_data(2025, 1)
        call_kwargs = engine_module.CalendarEngine.get_month_matrix.call_args[1]
        assert "today" in call_kwargs
        assert call_kwargs["today"] is not None

    def test_passes_selected_date(self):
        selected = date(2025, 1, 15)
        engine_module = ModuleType("codex_services.calendar.engine")
        engine_module.CalendarEngine = MagicMock()
        engine_module.CalendarEngine.get_month_matrix.return_value = []
        with patch.dict("sys.modules", {"codex_services.calendar.engine": engine_module}):
            from codex_django.booking.selectors import get_calendar_data

            get_calendar_data(2025, 1, selected_date=selected)
        call_kwargs = engine_module.CalendarEngine.get_month_matrix.call_args[1]
        assert call_kwargs["selected_date"] == selected

    def test_default_holidays_subdiv_ST(self):
        engine_module = ModuleType("codex_services.calendar.engine")
        engine_module.CalendarEngine = MagicMock()
        engine_module.CalendarEngine.get_month_matrix.return_value = []
        with patch.dict("sys.modules", {"codex_services.calendar.engine": engine_module}):
            from codex_django.booking.selectors import get_calendar_data

            get_calendar_data(2025, 1)
        call_kwargs = engine_module.CalendarEngine.get_month_matrix.call_args[1]
        assert call_kwargs["holidays_subdiv"] == "ST"

    def test_custom_holidays_subdiv(self):
        engine_module = ModuleType("codex_services.calendar.engine")
        engine_module.CalendarEngine = MagicMock()
        engine_module.CalendarEngine.get_month_matrix.return_value = []
        with patch.dict("sys.modules", {"codex_services.calendar.engine": engine_module}):
            from codex_django.booking.selectors import get_calendar_data

            get_calendar_data(2025, 1, holidays_subdiv="BY")
        call_kwargs = engine_module.CalendarEngine.get_month_matrix.call_args[1]
        assert call_kwargs["holidays_subdiv"] == "BY"


# ---------------------------------------------------------------------------
# get_nearest_slots
# ---------------------------------------------------------------------------


class TestGetNearestSlots:
    def test_calls_find_nearest(self, mock_adapter, mock_finder):
        finder, engine_result = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            get_nearest_slots(mock_adapter, [1], date(2025, 1, 6), search_days=30)
        finder.find_nearest.assert_called_once()

    def test_returns_finder_result(self, mock_adapter, mock_finder):
        finder, engine_result = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            result = get_nearest_slots(mock_adapter, [1], date(2025, 1, 6))
        assert result is engine_result

    def test_search_days_passed_to_finder(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            get_nearest_slots(mock_adapter, [1], date(2025, 1, 6), search_days=14)
        call_kwargs = finder.find_nearest.call_args[1]
        assert call_kwargs["search_days"] == 14

    def test_get_availability_callable_passed(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            get_nearest_slots(mock_adapter, [1], date(2025, 1, 6))
        call_kwargs = finder.find_nearest.call_args[1]
        assert callable(call_kwargs["get_availability_for_date"])

    def test_availability_callable_calls_adapter(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            get_nearest_slots(mock_adapter, [1], date(2025, 1, 6))
        fn = finder.find_nearest.call_args[1]["get_availability_for_date"]
        fn(date(2025, 1, 7))
        mock_adapter.build_masters_availability.assert_called()
        last_call_kwargs = mock_adapter.build_masters_availability.call_args[1]
        assert last_call_kwargs["target_date"] == date(2025, 1, 7)

    def test_search_from_passed_to_finder(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            get_nearest_slots(mock_adapter, [1], date(2025, 2, 1))
        call_kwargs = finder.find_nearest.call_args[1]
        assert call_kwargs["search_from"] == date(2025, 2, 1)

    def test_passes_mode_overlap_and_parallel_groups_to_engine_request(self, mock_adapter, mock_finder):
        finder, _ = mock_finder
        with patch("codex_django.booking.selectors.ChainFinder", return_value=finder):
            from codex_django.booking.selectors import get_nearest_slots

            get_nearest_slots(
                mock_adapter,
                [5, 7],
                date(2026, 4, 1),
                mode=BookingMode.MULTI_DAY,
                overlap_allowed=True,
                parallel_groups={5: "A", 7: "B"},
            )

        mock_adapter.build_engine_request.assert_called_once_with(
            service_ids=[5, 7],
            target_date=date(2026, 4, 1),
            locked_master_id=None,
            master_selections=None,
            mode=BookingMode.MULTI_DAY,
            overlap_allowed=True,
            parallel_groups={5: "A", 7: "B"},
        )


# ---------------------------------------------------------------------------
# create_booking — unit (fully mocked transaction)
# ---------------------------------------------------------------------------


class TestCreateBookingUnit:
    def _setup_mocks(self, available_times):
        """Return configured mocks for create_booking tests."""
        engine_result = MagicMock()
        engine_result.get_unique_start_times.return_value = available_times
        engine_result.best = MagicMock()
        engine_result.best.starts_at = datetime(2025, 1, 6, 9, 0, tzinfo=UTC)
        engine_result.best.span_minutes = 60
        return engine_result

    def test_raises_slot_already_booked_when_time_unavailable(self, mock_adapter):
        engine_result = self._setup_mocks(["10:00", "10:30"])
        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            # Patch transaction.atomic as context manager
            with patch("codex_django.booking.selectors.transaction") as mock_txn:
                mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
                mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
                from codex_services.booking.slot_master import SlotAlreadyBookedError  # noqa: PLC0415

                from codex_django.booking.selectors import create_booking  # noqa: PLC0415

                with pytest.raises(SlotAlreadyBookedError):
                    create_booking(
                        adapter=mock_adapter,
                        cache_adapter=MagicMock(),
                        appointment_model=MagicMock(),
                        service_ids=[1],
                        target_date=date(2025, 1, 6),
                        selected_time="09:00",  # not in ["10:00", "10:30"]
                        master_id=1,
                        client=MagicMock(),
                    )

    def test_raises_when_best_is_none(self, mock_adapter):
        engine_result = MagicMock()
        engine_result.get_unique_start_times.return_value = ["09:00"]
        engine_result.best = None
        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            with patch("codex_django.booking.selectors.transaction") as mock_txn:
                mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
                mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
                from codex_services.booking.slot_master import SlotAlreadyBookedError  # noqa: PLC0415

                from codex_django.booking.selectors import create_booking  # noqa: PLC0415

                with pytest.raises(SlotAlreadyBookedError):
                    create_booking(
                        adapter=mock_adapter,
                        cache_adapter=MagicMock(),
                        appointment_model=MagicMock(),
                        service_ids=[1],
                        target_date=date(2025, 1, 6),
                        selected_time="09:00",
                        master_id=1,
                        client=MagicMock(),
                    )

    def test_extra_fields_merged_into_create(self, mock_adapter):
        engine_result = self._setup_mocks(["09:00"])
        appointment_model = MagicMock()
        appointment_model.objects.create.return_value = MagicMock()
        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            with patch("codex_django.booking.selectors.transaction") as mock_txn:
                mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
                mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
                mock_txn.on_commit = MagicMock()
                from codex_django.booking.selectors import create_booking

                create_booking(
                    adapter=mock_adapter,
                    cache_adapter=MagicMock(),
                    appointment_model=appointment_model,
                    service_ids=[1],
                    target_date=date(2025, 1, 6),
                    selected_time="09:00",
                    master_id=1,
                    client=MagicMock(),
                    extra_fields={"notes": "VIP client"},
                )
        call_kwargs = appointment_model.objects.create.call_args[1]
        assert call_kwargs["notes"] == "VIP client"

    def test_on_commit_registers_cache_invalidation(self, mock_adapter):
        """Verify that transaction.on_commit is called with a callback."""
        engine_result = self._setup_mocks(["09:00"])
        appointment_model = MagicMock()
        appointment_model.objects.create.return_value = MagicMock()
        captured_callbacks = []
        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            with patch("codex_django.booking.selectors.transaction") as mock_txn:
                mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
                mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
                mock_txn.on_commit.side_effect = lambda fn: captured_callbacks.append(fn)
                from codex_django.booking.selectors import create_booking

                cache_adapter = MagicMock()
                create_booking(
                    adapter=mock_adapter,
                    cache_adapter=cache_adapter,
                    appointment_model=appointment_model,
                    service_ids=[1],
                    target_date=date(2025, 1, 6),
                    selected_time="09:00",
                    master_id=1,
                    client=MagicMock(),
                )
        assert len(captured_callbacks) == 1
        # Execute the callback and verify cache invalidation
        captured_callbacks[0]()
        cache_adapter.invalidate_master_date.assert_called_once_with("1", "2025-01-06")

    def test_multi_without_persistence_hook_raises(self, mock_adapter):
        with patch("codex_django.booking.selectors.transaction") as mock_txn:
            mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
            mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
            from codex_django.booking.selectors import create_booking

            with pytest.raises(NotImplementedError, match="Multi-service persistence requires a persistence hook"):
                create_booking(
                    adapter=mock_adapter,
                    cache_adapter=MagicMock(),
                    appointment_model=MagicMock(),
                    service_ids=[1, 2],
                    target_date=date(2025, 1, 6),
                    selected_time="09:00",
                    master_id=1,
                    client=MagicMock(),
                )
        mock_adapter.lock_masters.assert_not_called()

    def test_multi_with_hook_calls_persist_chain(self, mock_adapter):
        engine_result = self._setup_mocks(["09:00"])
        step1 = MagicMock()
        step1.resource_id = "10"
        step2 = MagicMock()
        step2.resource_id = "12"
        engine_result.best.items = [step1, step2]

        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            with patch("codex_django.booking.selectors.transaction") as mock_txn:
                mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
                mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
                mock_txn.on_commit = MagicMock()
                from codex_django.booking.selectors import create_booking

                hook = MagicMock()
                created = [MagicMock(), MagicMock()]
                hook.persist_chain.return_value = created
                result = create_booking(
                    adapter=mock_adapter,
                    cache_adapter=MagicMock(),
                    appointment_model=MagicMock(),
                    service_ids=[1, 2],
                    target_date=date(2025, 1, 6),
                    selected_time="09:00",
                    master_id=1,
                    client=MagicMock(),
                    persistence_hook=hook,
                )

        hook.persist_chain.assert_called_once()
        mock_adapter.lock_masters.assert_called_once_with([1, 2])
        assert result == created

    def test_multi_hook_error_prevents_on_commit_registration(self, mock_adapter):
        engine_result = self._setup_mocks(["09:00"])
        engine_result.best.items = [MagicMock(resource_id="10")]

        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            with patch("codex_django.booking.selectors.transaction") as mock_txn:
                mock_txn.atomic.return_value.__enter__ = MagicMock(return_value=None)
                mock_txn.atomic.return_value.__exit__ = MagicMock(return_value=False)
                mock_txn.on_commit = MagicMock()
                from codex_django.booking.selectors import create_booking

                hook = MagicMock()
                hook.persist_chain.side_effect = RuntimeError("boom")
                with pytest.raises(RuntimeError, match="boom"):
                    create_booking(
                        adapter=mock_adapter,
                        cache_adapter=MagicMock(),
                        appointment_model=MagicMock(),
                        service_ids=[1, 2],
                        target_date=date(2025, 1, 6),
                        selected_time="09:00",
                        master_id=1,
                        client=MagicMock(),
                        persistence_hook=hook,
                    )

        mock_txn.on_commit.assert_not_called()


# ---------------------------------------------------------------------------
# create_booking — with real Django DB (on_commit fires immediately in tests)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateBookingWithDb:
    def _engine_result(self, times):
        r = MagicMock()
        r.get_unique_start_times.return_value = times
        r.best = MagicMock()
        r.best.starts_at = datetime(2025, 1, 6, 9, 0, tzinfo=UTC)
        r.best.span_minutes = 60
        return r

    def test_creates_appointment_and_returns_it(self):
        engine_result = self._engine_result(["09:00"])
        appointment_model = MagicMock()
        mock_appointment = MagicMock()
        appointment_model.objects.create.return_value = mock_appointment
        adapter = MagicMock()
        adapter.step_minutes = 30
        sr = MagicMock()
        sr.possible_resource_ids = ["1"]
        req = MagicMock()
        req.service_requests = [sr]
        adapter.build_engine_request.return_value = req
        adapter.build_masters_availability.return_value = {}
        adapter.lock_masters.return_value = None
        with patch("codex_django.booking.selectors.ChainFinder") as finder_cls:
            finder = MagicMock()
            finder.find.return_value = engine_result
            finder_cls.return_value = finder
            from codex_django.booking.selectors import create_booking

            result = create_booking(
                adapter=adapter,
                cache_adapter=MagicMock(),
                appointment_model=appointment_model,
                service_ids=[1],
                target_date=date(2025, 1, 6),
                selected_time="09:00",
                master_id=1,
                client=MagicMock(),
            )
        appointment_model.objects.create.assert_called_once()
        assert result is mock_appointment
