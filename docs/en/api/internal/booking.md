<!-- DOC_TYPE: API -->

# Booking Internal Modules

The booking package is built from adapters, selectors, and abstract model mixins. This section indexes those implementation modules directly.

## Selectors

::: codex_django.booking.selectors

## Availability adapter

::: codex_django.booking.adapters.availability

## Cache adapter

::: codex_django.booking.adapters.cache

## Service mixins

::: codex_django.booking.mixins.service

## Master mixins

::: codex_django.booking.mixins.master

> Note: The module keeps historical `master` naming for model-level compatibility.
> Runtime selector/gateway contracts use `resource_*` naming.

## Appointment mixins

::: codex_django.booking.mixins.appointment

## Schedule mixins

::: codex_django.booking.mixins.schedule

## Settings mixins

::: codex_django.booking.mixins.settings
