# `BaseMessagingEngine` and Dispatch

## Origin

`BaseMessagingEngine` is a rename of the existing `BaseNotificationEngine`
(see `src/codex_django/notifications/service.py`). No behavior change
in the rename; the migration adds a small surface for the new
`@email_template` and `@email_rendered` decorators.

## Construction

```python
from codex_django.messaging import (
    BaseMessagingEngine,
    DjangoQueueAdapter,
    DjangoCacheAdapter,
    DjangoI18nAdapter,
    BaseEmailContentSelector,
)

engine = BaseMessagingEngine(
    queue_adapter=DjangoQueueAdapter(arq_client=DjangoArqClient()),
    cache_adapter=DjangoCacheAdapter(),
    i18n_adapter=DjangoI18nAdapter(),
    selector=BaseEmailContentSelector(
        model=EmailContent,
        cache_adapter=DjangoCacheAdapter(),
        i18n_adapter=DjangoI18nAdapter(),
    ),
)
```

The four adapters bridge to Django; the selector resolves localized
subject lines from a project-supplied content table. Each is injected;
none is constructed inside the engine.

## Class attributes (configurable)

```python
class MyEngine(BaseMessagingEngine):
    task_name = "send_universal_notification_task"   # ARQ task to enqueue
    mode = "template"                                  # default mode
    default_language = "de"                            # fallback language
```

* `task_name` is the worker task that will receive the payload. The
  default matches the lily worker (`tasks/notification_tasks.py:201`).
  Projects with a different worker task override.
* `mode` is the default for `dispatch()` calls that don't pass a
  `mode` argument. The migration adds the value `"rendered_inline"`
  for the rendered-inline shortcut (host renders + the engine produces
  a `RenderedNotificationDTO` payload). Today only `"template"` and
  `"rendered"` exist.
* `default_language` falls back into payloads that don't pass a
  `language`. Projects override.

## `dispatch()` — the canonical entry point

```python
engine.dispatch(
    recipient_email="anna@example.com",
    recipient_phone=None,
    client_name="Anna Müller",
    template_name="contacts/ct_reply.html",
    event_type="conversations.thread_reply",
    channels=["email"],
    language="de",
    subject_key="conversations.thread_reply.subject",
    subject="Re: …",                # optional explicit override
    mode="template",                  # or "rendered"

    # Mode 2 only — mutually exclusive with template_name:
    html_content="<html>…",
    text_content="…",

    # Anything else — flows into context_data:
    booking=booking,
    appointment=appointment,
)
```

All args are keyword-only. The engine:

1. Resolves the subject (explicit `subject` wins, otherwise
   `selector.get(subject_key, language)`).
2. Generates a `notification_id` (`uuid.uuid4()`).
3. Calls `MessagingPayloadBuilder.build_template` or
   `build_rendered`.
4. Calls `queue_adapter.enqueue(task_name, payload)`.

Returns the queue job ID (string) or `None`.

## Dispatching a pre-built spec

When a domain handler builds a `NotificationDispatchSpec` (see
`03_decorators.md`), the engine consumes it via `dispatch_spec`:

```python
spec = NotificationDispatchSpec(
    recipient_email="anna@example.com",
    subject_key="…",
    event_type="conversations.thread_reply",
    channels=["email"],
    mode="template",
    template_name="contacts/ct_reply.html",
    context={"reply_text": "…"},
)
engine.dispatch_spec(spec)
```

Or in bulk via `dispatch_event(event_type, *args, **kwargs)` — the
engine looks up handlers in the registry, invokes each, and dispatches
every spec they yield. This is the lily `notify_thread_reply` flow
today (`features/conversations/services/alerts.py:37-42`).

## Async equivalents

`adispatch`, `adispatch_spec`, `adispatch_event` mirror the sync API
and call `queue_adapter.aenqueue` instead. ARQ workers are async —
async dispatch avoids the `async_to_sync` round-trip that the sync
path goes through. Use async wherever the call site allows.

## Error handling

The engine does **not** catch exceptions from the queue adapter.
Infrastructure failures (Redis down, serialization error) propagate.
Callers (lily today wraps in `try/except` — see
`features/conversations/services/alerts.py:31-34`) decide whether to
rethrow, log, or silently swallow.

Recommendation: log + swallow at the cabinet/view layer, log + rethrow
in service layers. The engine itself does not impose a policy.

## What the engine does NOT do

* It does not write to `EmailLog`. The worker callback writes the row
  on terminal status. The engine is upstream of that.
* It does not enrich context (greeting, calendar URLs, etc.). That is
  project logic — for lily it lives in
  `src/workers/notification_worker/services/notification_service.py:217-245`.
* It does not validate `template_name` exists. The renderer raises at
  the worker.
* It does not deduplicate by `notification_id` — it always generates a
  fresh one. If you need stable IDs (idempotent enqueue), construct
  the payload yourself and call `queue_adapter.enqueue` directly.

## Open question — `mode="rendered_inline"`

In lily today, the compose-new flow is supposed to render text on the
host side and pass it as `RenderedNotificationDTO`, but the broken
code path skips dispatch entirely. After the migration, the natural
shape is:

```python
engine.dispatch(
    recipient_email=to_email,
    event_type="conversations.compose_new",
    channels=["email"],
    subject_key="conversations.compose_new.subject",
    subject=message.subject,
    mode="rendered",
    html_content=render_compose_new_html(message),
    text_content=message.body,
)
```

If many call sites repeat the `render_compose_new_html(...)` step,
adding a `mode="rendered_inline"` shortcut that takes a callable
becomes worthwhile. For Phase 0 we document the manual pattern only;
the shortcut can be added later without breaking anything.
