# T-08. Live broadcast board

- Owner: claude
- Depends on: T-04
- Estimate: M

## Goal

The demo screen shows each channel tile turning green as real receipts arrive, with elapsed time.

## Context

TECHNICAL_ARCHITECTURE 5.5.

## Acceptance criteria

- [ ] API exposes server sent events for delivery status changes
- [ ] Board shows channel by language tiles and time from approval to all sent
- [ ] Only real receipts are shown; no simulated counts
- [ ] `make verify` passes

## Files likely touched

api/routes/, apps/web/src/features/board/

## Questions
