# T-04. Message, review and broadcast API

- Owner:
- Depends on: T-02
- Estimate: L

## Goal

A claim becomes a master message that a reviewer approves and broadcasts to every channel.

## Context

TECHNICAL_ARCHITECTURE 5.2 to 5.5; `domain/rules.py`; `services/broadcasting.py`; `worker/tasks.py`.

## Acceptance criteria

- [ ] Endpoints: create message from claim, add review, add or approve localisation, seal, broadcast, retract
- [ ] Broadcast calls `plan_deliveries` and enqueues one `deliveries.send` job per delivery
- [ ] Worker job sends via `send_one`, stores the receipt and is idempotent on retry
- [ ] API test proves an unapproved message returns 409 and sends nothing
- [ ] `make contract` run and committed
- [ ] `make verify` passes

## Files likely touched

api/routes/messages.py, services/, worker/tasks.py, repositories/

## Questions

