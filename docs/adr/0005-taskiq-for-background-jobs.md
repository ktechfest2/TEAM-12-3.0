# 0005. taskiq on Redis for background jobs

- Status: accepted
- Date: 2026-11-19

## Context

Each channel send must run independently with retries so one failing provider never blocks the rest. The queue must run on Render Key Value and locally on any Redis.

## Options considered

1. FastAPI background tasks: no retries, lost on restart.
2. Celery: heavy for a two day build.
3. taskiq with taskiq-redis: async native, typed, small, Redis protocol only.

## Decision

taskiq with `ListQueueBroker` in development and production, `InMemoryBroker` in tests.

## Consequences

Worker is a separate process (`make -C apps/api worker`, Render worker service). Jobs must be idempotent.
