# T-04. Message, review and broadcast API

- Owner: claude
- Depends on: T-02
- Estimate: L

## Goal

A claim becomes a master message that a reviewer approves and broadcasts to every channel.

## Context

TECHNICAL_ARCHITECTURE 5.2 to 5.5; `domain/rules.py`; `services/broadcasting.py`; `worker/tasks.py`.

## Acceptance criteria

- [x] Endpoints: create message from claim, add review, add or approve localisation, seal, broadcast, retract
- [x] Broadcast calls `plan_deliveries` and enqueues one `deliveries.send` job per delivery
- [x] Worker job sends via `send_one`, stores the receipt and is idempotent on retry
- [x] API test proves an unapproved message returns 409 and sends nothing
- [x] `make contract` run and committed
- [x] `make verify` passes

## Files likely touched

api/routes/messages.py, services/, worker/tasks.py, repositories/

## Questions

- Retraction sends one English notice per channel (not per language) and is a reviewer action with a required reason. Chosen as the safest reading; a localised notice would need approved translations first.
