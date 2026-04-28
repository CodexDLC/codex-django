# Decorator API — Two Variants Compared

The user asked for two new decorators that match the two delivery
modes: one for template-based content builders, one for pre-rendered
HTML. The existing `@notification_handler` decorator is generic — it
returns a `NotificationDispatchSpec`. The two new decorators are
**focused sugar** on top of that.

This document compares two API styles and recommends one for the
final implementation. Both are described so a future maintainer can
revisit the choice.

## Variant A — Split decorators (recommended)

Two decorators, one per mode. The mode is implicit in the decorator
name.

```python
from codex_django.messaging import (
    email_template,    # → mode="template"
    email_rendered,    # → mode="rendered"
)


@email_template("conversations.thread_reply", channels=["email"])
def build_thread_reply(message, reply):
    return {
        "recipient_email": message.sender_email,
        "subject": _build_reply_subject(message),
        "subject_key": "conversations.thread_reply.subject",
        "template_name": "contacts/ct_reply.html",
        "context": _build_reply_context(message, reply),
    }


@email_rendered("conversations.compose_new", channels=["email"])
def build_compose_new(message, *, to_email):
    html = render_to_string("emails/compose_new.html", {"message": message})
    return {
        "recipient_email": to_email,
        "subject": message.subject,
        "subject_key": "conversations.compose_new.subject",
        "html_content": html,
        "text_content": message.body,
    }
```

The decorator's job is to:

1. Register the function under the event key in
   `MessagingEventRegistry`.
2. Wrap the function so that when invoked it returns a
   `NotificationDispatchSpec` with `mode` set automatically.
3. Forbid passing a key that is incompatible with the mode (if a
   `@email_template` builder returns `html_content`, the decorator
   raises at registration time).

### Pros

* **Self-documenting.** The decorator name tells you which mode the
  builder targets.
* **Strict at registration time.** Returning the wrong key set is
  caught immediately.
* **Easy to grep.** `grep "@email_rendered"` lists every host-rendered
  email in the codebase.
* **Two clearly bounded code paths.** No "what mode is this?" branch
  inside builders.

### Cons

* **Two decorators to learn.** Marginal — they share a contract.
* **Some duplication** if a builder needs to flip modes (rare in
  practice; we have not seen this in lily).

## Variant B — Unified decorator

One decorator, mode is a parameter:

```python
from codex_django.messaging import notification


@notification("conversations.thread_reply", mode="template", channels=["email"])
def build_thread_reply(message, reply):
    return {...}


@notification("conversations.compose_new", mode="rendered", channels=["email"])
def build_compose_new(message, *, to_email):
    return {...}
```

### Pros

* **One decorator to learn.**
* **Mode is data**, so a generic builder could take it as a parameter
  and produce different specs.

### Cons

* **Mode is hidden in a kwarg.** Reading code requires opening the
  decorator call to see which mode applies.
* **Validation is harder.** A builder must pre-declare which keys it
  produces; the unified decorator either trusts the function or runs
  the same registration-time validation as the split version (in which
  case it gains the cons of A without the clarity).
* **Encourages mode-flipping inside one builder.** The unified API
  invites code that branches on mode, which is the exact source of
  the inconsistency we are trying to escape.

## Recommendation

Ship **Variant A** (split decorators). The split makes intent visible
at the call site; the cost is a single extra symbol. Keep
`@notification_handler` (returning `NotificationDispatchSpec` directly)
as the escape hatch for builders that don't fit either mode (e.g.
multi-channel dispatch where one spec yields email and SMS specs).

## Final API surface (after migration)

```python
from codex_django.messaging import (
    email_template,
    email_rendered,
    notification_handler,
    NotificationDispatchSpec,
)


# Mode 1 — worker renders
@email_template("booking.confirmed", channels=["email"])
def build_booking_confirmed(booking):
    return {
        "recipient_email": booking.client_email,
        "subject_key": "booking.confirmed.subject",
        "template_name": "booking/bk_confirmation.html",
        "language": booking.client.locale,
        "context": {
            "booking_id": booking.pk,
            "datetime": booking.datetime_str,
        },
    }


# Mode 2 — host renders
@email_rendered("conversations.compose_new", channels=["email"])
def build_compose_new(message, *, to_email):
    html = render_to_string("emails/compose_new.html", {"message": message})
    return {
        "recipient_email": to_email,
        "subject_key": "conversations.compose_new.subject",
        "subject": message.subject,
        "html_content": html,
        "text_content": message.body,
    }


# Generic — yields one or many specs
@notification_handler("conversations.thread_reply")
def build_thread_reply_specs(message, reply):
    spec = NotificationDispatchSpec(
        recipient_email=message.sender_email,
        subject_key="conversations.thread_reply.subject",
        subject=_build_reply_subject(message),
        event_type="conversations.thread_reply",
        channels=["email"],
        mode="template",
        template_name="contacts/ct_reply.html",
        context=_build_reply_context(message, reply),
    )
    yield spec
```

## Validation rules at registration

`@email_template` requires the function to return a dict with at
minimum: `recipient_email`, `subject_key`, `template_name`. Forbidden
keys: `html_content`, `text_content`, `mode`.

`@email_rendered` requires: `recipient_email`, `subject_key`,
`html_content` (`text_content` recommended). Forbidden keys:
`template_name`, `mode`.

`@notification_handler` accepts any return shape compatible with
`NotificationDispatchSpec`.

The two new decorators raise `TypeError` at registration time if the
returned dict has the wrong key set. This catches drift before
deployment.

## Engine integration

The two decorators register into a sub-registry per mode and supply a
factory that produces a `NotificationDispatchSpec` from the dict:

```python
class MessagingEventRegistry(NotificationEventRegistry):
    def email_template(self, event_type: str, *, channels: list[str]):
        def wrap(fn):
            def builder(*args, **kwargs):
                data = fn(*args, **kwargs)
                # validate keys
                return NotificationDispatchSpec(
                    recipient_email=data["recipient_email"],
                    subject_key=data["subject_key"],
                    subject=data.get("subject", ""),
                    event_type=event_type,
                    channels=channels,
                    mode="template",
                    template_name=data["template_name"],
                    language=data.get("language", ""),
                    context=data.get("context", {}),
                )
            self.register(event_type)(builder)
            return fn
        return wrap

    def email_rendered(self, event_type, *, channels):
        # symmetric
        ...
```

`engine.dispatch_event("conversations.thread_reply", message, reply)`
then resolves all three styles uniformly.

## Anti-patterns

* **Mixing two decorators on the same builder.** A builder is one mode
  by construction; if you need two paths for the same event, define
  two builders.
* **Returning a `NotificationDispatchSpec` from `@email_template`.**
  The decorator wants a dict; it owns spec construction. Returning a
  spec defeats the validation.
* **Calling the decorated function directly.** The decorator returns
  the wrapped builder, not the original; callers should use
  `engine.dispatch_event(event_type, *args, **kwargs)` to invoke
  through the registry.
