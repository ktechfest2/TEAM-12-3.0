# T-06. Review queue screen

- Owner: claude
- Depends on: T-04
- Estimate: M

## Goal

A reviewer sees pending claims, edits the summary, approves translations and approves or escalates.

## Context

Web `features/` structure; ADR 0003.

## Acceptance criteria

- [x] `features/review/` with list and detail components and tests
- [x] Shows the cited official passage beside the draft answer
- [x] Approve button disabled until every target language has an approved translation
- [x] Uses the generated API client only
- [x] `make verify` passes

## Files likely touched

apps/web/src/features/review/, pages/review-queue-page.tsx

## Questions

- Reviewers sign in with the invite code (T-11); the token is kept in sessionStorage for the tab only and attached by the API client middleware.
- "Every target language" means Yoruba, Hausa, Igbo and Pidgin (English is the master text). Saving a changed answer clears translations on the server, so the answer is saved before translating.
- The detail screen also seals and starts the broadcast, because a reviewer needs those steps after approval; the live status lives on the board (T-08).
