---
title: Booking Multi-Service Handoff Plan
updated: 2026-03-26
status: draft (reviewed, amendments added)
---

# Booking multi-service: handoff plan

## Goal

Extend `codex-django` booking so the library can support both:

- solo booking flow
- multi-service booking flow (service chain / service set)

without breaking the current single-service API and generated blueprints.

This work is driven by an already working real-world pattern from `lily_website`, where booking chains can be created from the admin/cabinet side. The implementation in this repository should align with the booking engine behavior already present in `codex-services`, not invent a parallel model.

## What is already known

- `codex-services` support is expected to exist already; the missing part is correct integration in `codex-django`.
- Current adapter code in `src/codex_django/booking/adapters/availability.py` already builds multiple `ServiceRequest` items, but the overall flow is still effectively biased toward a single booking/master path.
- Current booking creation in `src/codex_django/booking/selectors.py` assumes one final `master_id`, which is likely not enough for true multi-service persistence.
- Current generated booking blueprint is single-service oriented.

## Main files involved

- `src/codex_django/booking/adapters/availability.py`
- `src/codex_django/booking/selectors.py`
- `src/codex_django/cli/blueprints/features/booking/booking/selectors.py.j2`
- `src/codex_django/cli/blueprints/features/booking/booking/views.py.j2`
- `tests/unit/booking/test_availability_adapter.py`
- `tests/unit/booking/test_selectors.py`

## Constraints

- Preserve backward compatibility for solo mode.
- Do not hardcode `lily_website` models into the library.
- Keep adapter logic generic and library-grade.
- Prefer an incremental migration with passing tests after each phase.
- Treat `codex-services` as the source of truth for booking-chain semantics.

## Open questions that must be answered before implementation

1. What exact `codex-services` request/response fields are needed for chain booking in the currently used version?
2. Does the engine expect one resource per service step, or can one resource span several sequential services implicitly?
3. What is the canonical representation of a chosen solution when different services map to different masters?
4. How should persistence work in `codex-django` if the host project has one appointment row but the engine returns a chain?
5. Which parts belong in the generic library versus generated project code?
6. How should UI master selection behave in multi mode:
   - one master for all services
   - per-service selection
   - mixed mode with `"any"` fallback
7. Which edge cases are guaranteed by engine constraints already, and which must be guarded in adapter/view code?

## Recommended implementation phases

## Phase 1: engine audit and contract freeze

Goal: remove ambiguity before code changes.

Tasks:

- Audit `codex-services` around:
  - `ChainFinder`
  - `BookingEngineRequest`
  - `ServiceRequest`
  - solution/result DTOs
  - booking modes
  - parallel groups
  - resource filtering semantics
- Compare those contracts with the current `codex-django` adapter assumptions.
- Produce a short compatibility note describing:
  - what already matches
  - what is missing
  - what `codex-django` must expose as configuration

Deliverable:

- A short design note or section appended to this file with confirmed engine facts.

Exit criteria:

- No critical API ambiguity remains for adapter redesign.

## Phase 2: define library-facing booking request model

Goal: stop relying on an implicit "list of service ids means everything".

Tasks:

- Define the target input contract for booking selection.
- Decide whether the adapter should keep accepting `service_ids: list[int]` as a compatibility wrapper while internally normalizing into richer request items.
- Introduce an internal normalized structure conceptually similar to:
  - service id
  - optional forced master id
  - optional selection mode
  - optional metadata needed for future UI flows

Recommended direction:

- Keep current public `service_ids` entry points working.
- Add an internal normalization layer first.
- Only expand public API once compatibility is understood.

Exit criteria:

- One normalized internal model exists for both solo and multi paths.

## Phase 3: adapter redesign for solo + multi

Goal: make `build_engine_request()` explicit, predictable, and mode-aware.

Tasks:

- Refactor `build_engine_request()` to build requests from normalized selection data.
- Review `_resolve_master_ids()` because it currently assumes a simple category + weekday filter and index-based selection mapping.
- Add explicit configuration for booking mode, likely via adapter settings or function parameter.
- Ensure support for:
  - solo flow
  - multi flow with same master for all services
  - multi flow with different masters per service
  - `"any"` semantics per service

Likely risks:

- Current `master_selections: dict[str, str]` may be too weak and too positional.
- Current service-to-master resolution may need richer filtering hooks.

Exit criteria:

- Adapter can produce a correct engine request for confirmed multi-service scenarios while solo tests still pass.

## Phase 4: selector split between search and persistence

Goal: avoid forcing multi-service booking into the current single-master write path.

Tasks:

- Reassess `get_available_slots()` and `get_nearest_slots()` contracts based on engine result shape.
- Redesign `create_booking()` path.
- Decide whether generic library code should:
  - persist a simple appointment only for solo mode
  - expose a hook/callback for multi persistence
  - or provide a generic chain persistence abstraction

Recommended direction:

- Keep solo persistence in the library.
- For multi persistence, strongly consider an extension hook instead of hardcoding assumptions into the library until the domain model is proven stable.

Reason:

- Different host projects may store multi-service bookings differently.

Exit criteria:

- There is a clear persistence strategy that does not fake multi-service support by collapsing it to one master row.

## Phase 5: blueprint and UI flow update

Goal: generated projects can actually use the new behavior.

Tasks:

- Update generated selectors/views templates.
- Add support for:
  - selecting multiple services
  - carrying a service cart or service chain through the flow
  - master selection strategy
  - mode switching (`solo` / `multi`)
- Keep existing single-service blueprint output valid.

Important note:

- UI work should follow the confirmed data contract from phases 2-4, not lead it.

Exit criteria:

- Blueprint can generate a working solo flow and a coherent multi-service flow entry point.

## Phase 6: tests and regression net

Goal: lock behavior before broader rollout.

Required test matrix:

- solo mode remains unchanged
- multi mode request builds correct `ServiceRequest[]`
- same-master multi chain
- different-master multi chain
- per-service forced master selection
- `"any"` master selection path
- parallel-group behavior
- buffer conflict handling
- nearest-slot search in multi mode
- locking/concurrency expectations for supported persistence path

Priority files:

- `tests/unit/booking/test_availability_adapter.py`
- `tests/unit/booking/test_selectors.py`

Possible additions:

- integration tests for generated booking blueprint once contracts stabilize

Exit criteria:

- Tests cover both backward compatibility and the new multi-service paths.

## Suggested execution order for the next model

1. Read this plan.
2. Audit `codex-services` and write down confirmed engine facts.
3. Convert those facts into a normalized internal request model.
4. Refactor the adapter with compatibility wrappers.
5. Decide the persistence strategy before editing views heavily.
6. Add tests before or alongside each refactor step.

## Suggested deliverable slicing

To reduce risk, implementation should be split into separate commits or PRs:

1. Audit + design note + failing tests for multi-service scenarios
2. Adapter/request normalization refactor
3. Selector/persistence changes
4. Blueprint/UI support
5. Docs and cleanup

## Version / model recommendation

- Planning and engine audit: `GPT-5.4` or `GPT-5.3-Codex` with `high` reasoning is enough.
- Full implementation: prefer `GPT-5.1-Codex-Max` or the strongest Codex-oriented model available with `very high` reasoning.

Reason:

- This is architecture-sensitive integration work with compatibility risk, not a simple local bugfix.

## Handoff note

If a stronger model takes over, it should not start by changing templates or persistence code blindly.

The first implementation action should be:

- confirm the exact `codex-services` chain-booking contract in use by the real project

Only after that should it redesign adapter inputs and booking persistence.

---

## Review amendments (2026-03-26)

> This plan is intended for execution by an AI agent, not a human developer.
> The following amendments address gaps specific to AI execution context.

### Amendment 1: Current state is more advanced than the plan assumes

The plan frames Phase 3 as "adapter redesign", but the adapter **already works for multi-service**:

```python
# availability.py, line ~108
for idx, svc_id in enumerate(service_ids):
    service = service_map.get(svc_id)
    possible_ids = self._resolve_master_ids(service, weekday, locked_master_id, master_selections, idx)
    service_requests.append(ServiceRequest(
        service_id=str(svc_id),
        duration_minutes=service.duration,
        min_gap_after_minutes=gap,
        possible_resource_ids=possible_ids,
        parallel_group=parallel_group,
    ))
```

**For the AI agent:** Do NOT rewrite `build_engine_request()` from scratch. It already iterates `service_ids` and builds `ServiceRequest[]`. Focus Phase 3 on:
- Adding `mode` and `overlap_allowed` as configurable parameters
- Replacing positional `master_selections` keying (see Amendment 3)
- Keeping everything else as-is

The **real gap** is `create_booking()` in `selectors.py` — it accepts one `master_id` and creates one row.

### Amendment 2: Exact engine contracts (answers to open questions 1-3)

The AI agent should NOT spend time auditing `codex-services` by reading random files. Here are the confirmed contracts from the installed package:

**BookingEngineRequest:**
```python
service_requests: list[ServiceRequest]   # ordered chain
booking_date: date
mode: BookingMode = SINGLE_DAY           # SINGLE_DAY | MULTI_DAY | RESOURCE_LOCKED
overlap_allowed: bool = False            # parallel masters allowed?
max_chain_duration_minutes: int | None   # total span limit
```

**ServiceRequest:**
```python
service_id: str                          # string, not int
duration_minutes: int                    # > 0
min_gap_after_minutes: int = 0           # buffer between chain steps
possible_resource_ids: list[str]         # candidate masters
parallel_group: str | None               # same tag = parallel execution
```

**BookingChainSolution:**
```python
items: list[SingleServiceSolution]       # one per service in chain
score: float
starts_at: datetime                      # property: min start
ends_at: datetime                        # property: max end
span_minutes: int                        # total duration
```

**SingleServiceSolution:**
```python
service_id: str
resource_id: str                         # assigned master
start_time: datetime
end_time: datetime
gap_end_time: datetime                   # end + gap
```

**Answer to Q1:** Fields above are the full contract.
**Answer to Q2:** Each service step gets its own `resource_id`. One resource CAN appear in multiple steps.
**Answer to Q3:** `BookingChainSolution.items` is the canonical representation — iterate it for per-service master mapping.

### Amendment 3: Concrete proposal for `master_selections` replacement

Current (positional, fragile):
```python
master_selections: dict[str, str]  # {"0": "5", "1": "12"} — index → master_id
```

Proposed (service-keyed, explicit):
```python
master_selections: dict[int, int | None]  # {service_id: master_id_or_None}
# None or missing key = "any" semantics
```

Backward compatibility wrapper:
```python
def _normalize_master_selections(
    service_ids: list[int],
    master_selections: dict[str, str] | dict[int, int | None] | None,
) -> dict[int, int | None]:
    if master_selections is None:
        return {}
    # Detect legacy positional format
    if all(k.isdigit() and int(k) < len(service_ids) for k in master_selections):
        return {service_ids[int(k)]: int(v) for k, v in master_selections.items() if v != "any"}
    # New format
    return {int(k): (int(v) if v is not None else None) for k, v in master_selections.items()}
```

**For the AI agent:** Implement this normalization in `build_engine_request()` before touching `_resolve_master_ids()`. Add tests for both legacy and new format.

### Amendment 4: Persistence hook interface

The plan says "extension hook" but does not specify the interface. Here is the minimum contract:

```python
from typing import Protocol, Any

class BookingPersistenceHook(Protocol):
    """Called by create_booking() when mode is multi-service."""

    def persist_chain(
        self,
        solution: "BookingChainSolution",
        service_ids: list[int],
        client: Any,
        extra_fields: dict[str, Any] | None = None,
    ) -> list[Any]:
        """
        Persist all appointments from a chain solution.

        Returns a list of created appointment objects (one per service step).
        Must be called inside an atomic transaction block.
        Raise to abort the entire chain.
        """
        ...
```

**For the AI agent:** The updated `create_booking()` should:
1. For solo mode (`len(service_ids) == 1`): keep current behavior, create one row
2. For multi mode: call `persistence_hook.persist_chain()` if provided, else raise `NotImplementedError("Multi-service persistence requires a persistence hook")`
3. Both paths must be inside `transaction.atomic()` with `select_for_update` on all involved masters

### Amendment 5: Missing engine features the plan ignores

1. **`overlap_allowed`** — when `True`, engine allows different masters to work in parallel on different services. Critical for salon scenarios (маникюр + педикюр). The adapter must expose this as a parameter.

2. **`BookingMode.MULTI_DAY`** — allows chain services to span multiple days. Not needed for lily v1 but the adapter should not hardcode `SINGLE_DAY`.

3. **`parallel_group`** — services with the same tag can run simultaneously. Currently hardcoded to `None` in the adapter. Should be configurable per-service.

**For the AI agent:** Add these as optional parameters to `build_engine_request()` with safe defaults that preserve current behavior:
```python
def build_engine_request(
    self,
    service_ids: list[int],
    target_date: date,
    locked_master_id: int | None = None,
    master_selections: dict[str, str] | dict[int, int | None] | None = None,
    mode: BookingMode = BookingMode.SINGLE_DAY,       # NEW
    overlap_allowed: bool = False,                      # NEW
    parallel_groups: dict[int, str] | None = None,      # NEW: service_id → group tag
) -> BookingEngineRequest:
```

### Amendment 6: Test scenarios with concrete data

The plan lists test categories but not concrete test cases. AI agents work better with specific examples:

```python
# Test 1: solo mode backward compat
build_engine_request(service_ids=[5], target_date=date(2026, 4, 1))
# Expected: 1 ServiceRequest, mode=SINGLE_DAY

# Test 2: multi mode, same master
build_engine_request(service_ids=[5, 7], target_date=date(2026, 4, 1),
                     master_selections={5: 10, 7: 10})
# Expected: 2 ServiceRequests, both with possible_resource_ids=["10"]

# Test 3: multi mode, different masters
build_engine_request(service_ids=[5, 7], target_date=date(2026, 4, 1),
                     master_selections={5: 10, 7: 12})
# Expected: 2 ServiceRequests with different possible_resource_ids

# Test 4: multi mode, "any" master for second service
build_engine_request(service_ids=[5, 7], target_date=date(2026, 4, 1),
                     master_selections={5: 10})  # 7 not specified = "any"
# Expected: service 7 gets all available masters for its category

# Test 5: overlap_allowed
build_engine_request(service_ids=[5, 7], overlap_allowed=True)
# Expected: BookingEngineRequest.overlap_allowed == True

# Test 6: legacy positional format still works
build_engine_request(service_ids=[5, 7],
                     master_selections={"0": "10", "1": "12"})
# Expected: same as Test 3 (normalized internally)

# Test 7: create_booking solo — unchanged behavior
create_booking(service_ids=[5], master_id=10, ...)
# Expected: 1 appointment row, as before

# Test 8: create_booking multi — requires hook
create_booking(service_ids=[5, 7], master_id=10, ...)
# Expected: NotImplementedError (no persistence_hook provided)

# Test 9: create_booking multi — with hook
create_booking(service_ids=[5, 7], persistence_hook=my_hook, ...)
# Expected: hook.persist_chain() called, returns list of appointments

# Test 10: partial chain failure rolls back
# persistence_hook raises on 2nd appointment
# Expected: transaction.atomic() rolls back everything
```

### Amendment 7: Execution order for AI agent (revised)

The original "suggested execution order" is too vague for an AI agent. Here is the precise sequence:

1. **Read** `availability.py` and `selectors.py` fully — understand current code before changing anything
2. **Write failing tests** (Tests 1-6 from Amendment 6) for `build_engine_request()` changes
3. **Implement** `_normalize_master_selections()` (Amendment 3)
4. **Add** `mode`, `overlap_allowed`, `parallel_groups` params to `build_engine_request()` (Amendment 5)
5. **Run tests** — Tests 1-6 should pass, solo behavior unchanged
6. **Write failing tests** (Tests 7-10) for `create_booking()` changes
7. **Define** `BookingPersistenceHook` protocol (Amendment 4)
8. **Refactor** `create_booking()` — solo path unchanged, multi path uses hook
9. **Run all tests** — everything green
10. **Update blueprint templates** only after library code is stable
11. **Do NOT touch UI flow** until persistence is proven

### Amendment 8: What the AI agent must NOT do

- Do NOT rewrite `build_engine_request()` from scratch — it works, extend it
- Do NOT add models to the library — persistence is project-specific
- Do NOT change `ChainFinder` or engine DTOs — they are in `codex-services`, a separate package
- Do NOT implement UI multi-service flow in this task — that's a separate PR after contracts are stable
- Do NOT change the solo booking path behavior — backward compatibility is non-negotiable
- Do NOT guess at lily_website's persistence model — use the hook pattern instead

### Amendment 9: Effort estimate (AI agent context)

For an AI agent with `very high` reasoning:

| Step | Estimated tokens | Risk |
|------|-----------------|------|
| Read + understand code | ~10K input | low |
| Write tests (10 cases) | ~5K output | low |
| Normalize master_selections | ~2K output | medium — backward compat |
| Extend build_engine_request params | ~2K output | low |
| Define persistence hook | ~1K output | low |
| Refactor create_booking | ~3K output | **high** — transaction logic |
| Update blueprints | ~3K output | medium |
| **Total** | ~26K tokens | |

This fits in **one strong session** (Codex-Max / Opus with high reasoning), possibly two if the agent needs to iterate on test failures.

Human difference: the original plan said 3-4 human hours. For an AI agent, the bottleneck is not time but **context window and reasoning depth** — the agent must hold adapter code, engine contracts, test expectations, and persistence design simultaneously.

---

## Codex execution plan (expanded, 2026-03-26)

This section is the concrete implementation track to execute now, based on the amendments above and the current repository state.

### Scope for current implementation pass

- Include: booking library internals (`availability.py`, `selectors.py`, unit tests).
- Include: backward compatibility for existing solo API behavior.
- Exclude: UI multi-service flow and broad template redesign in this pass.
- Exclude: codex-services package changes.

### Current code reality check

- `build_engine_request()` already builds `ServiceRequest[]` for multiple `service_ids`.
- `create_booking()` is still single-master/single-row oriented and is the primary gap.
- Existing unit tests already cover solo behavior and should be preserved unchanged where possible.

### Phase A: lock adapter behavior with failing tests first

Add or extend tests in `tests/unit/booking/test_availability_adapter.py` for:

1. New-format `master_selections` (`{service_id: master_id}`) in multi-service.
2. Legacy positional `master_selections` (`{"0": "10"}`) still supported.
3. Missing service key means `"any"` behavior.
4. `mode` passed through into `BookingEngineRequest`.
5. `overlap_allowed=True` passed through.
6. `parallel_groups` override applied by `service_id`.

Exit gate:

- Tests fail on current code for new behavior, proving we are driving changes with tests.

### Phase B: minimal adapter extension (no rewrite)

In `src/codex_django/booking/adapters/availability.py`:

1. Add `_normalize_master_selections(...)` per Amendment 3.
2. Expand `build_engine_request(...)` signature with:
   - `master_selections: dict[str, str] | dict[int, int | None] | None`
   - `mode: BookingMode = BookingMode.SINGLE_DAY`
   - `overlap_allowed: bool = False`
   - `parallel_groups: dict[int, str] | None = None`
3. Normalize selections once, then resolve by `service_id`, not positional index only.
4. Keep current service iteration and `ServiceRequest` creation logic.
5. Set `BookingEngineRequest.overlap_allowed` and pass `mode`.
6. Apply `parallel_groups` override first, then fallback to `service.parallel_group`.

Exit gate:

- Adapter tests (including new cases) pass.
- Existing solo tests remain green.

### Phase C: define persistence protocol and write selector tests

In `tests/unit/booking/test_selectors.py`, add failing tests for:

1. Solo path unchanged.
2. Multi path without hook raises `NotImplementedError`.
3. Multi path with hook calls `persist_chain(...)`.
4. Multi path rollback behavior when hook raises.

Also assert selector forwards new engine args where relevant (`mode`, `overlap_allowed`, `parallel_groups`, new `master_selections` shape).

Exit gate:

- New selector tests fail before selector changes.

### Phase D: refactor create_booking with safe two-path behavior

In `src/codex_django/booking/selectors.py`:

1. Add `BookingPersistenceHook` protocol under `TYPE_CHECKING`-friendly typing.
2. Extend `create_booking(...)` signature with optional:
   - `persistence_hook`
   - `mode`
   - `overlap_allowed`
   - `parallel_groups`
   - widened `master_selections` type
3. Keep solo path behavior intact (single appointment create, same return type).
4. For multi path:
   - require hook; otherwise raise `NotImplementedError("Multi-service persistence requires a persistence hook")`
   - compute candidate chain, lock all involved masters, re-check availability under lock, then call hook
5. Keep everything in `transaction.atomic()`.
6. Preserve `transaction.on_commit(...)` cache invalidation semantics.

Implementation note:

- Multi path should invalidate cache for all masters involved in the persisted chain, not only one master.

Exit gate:

- Selector tests pass, including rollback/exception scenarios.

### Phase E: verification and stabilization

Run focused tests:

- `tests/unit/booking/test_availability_adapter.py`
- `tests/unit/booking/test_selectors.py`

Then run broader booking-related unit suite if needed to ensure no regressions.

Exit gate:

- All targeted tests green.
- No solo contract regressions.

### Safety rules for this execution

- Do not rewrite adapter architecture.
- Do not introduce project-specific models into the library.
- Do not touch UI/template flow in this pass.
- Do not change codex-services internals.
- Do not silently break return shape of existing solo `create_booking()`.

### Definition of done for this pass

- Adapter accepts both legacy and new `master_selections` formats.
- Adapter exposes `mode`, `overlap_allowed`, `parallel_groups`.
- `create_booking()` supports multi-service through `BookingPersistenceHook`.
- Multi-service without hook fails loudly with explicit error.
- Unit tests cover the new behavior and protect backward compatibility.
