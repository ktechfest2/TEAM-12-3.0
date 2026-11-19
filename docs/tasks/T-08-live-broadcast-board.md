# T-08. Live broadcast board

- Owner: claude
- Depends on: T-04
- Estimate: M

## Goal

The demo screen shows each channel tile turning green as real receipts arrive, with elapsed time.

## Context

TECHNICAL_ARCHITECTURE 5.5.

## Acceptance criteria

- [x] API exposes server sent events for delivery status changes
- [x] Board shows channel by language tiles and time from approval to all sent
- [x] Only real receipts are shown; no simulated counts
- [x] `make verify` passes

## Files likely touched

api/routes/, apps/web/src/features/board/

## Questions

- The stream reads the shared delivery store every half second instead of using an in-process bus, so it also works when the worker is a separate process. Receipts shown are exactly what the worker saved.
- Browsers cannot send an Authorization header with EventSource, so the web board reads the stream with fetch and the reviewer token. The stream route requires the reviewer token like every other `/messages` route.
- The fetch reader (`delivery-stream.ts`) and hook are not unit tested; the parser, the model and the board component are. Check the live feed once by hand with `make dev`.
