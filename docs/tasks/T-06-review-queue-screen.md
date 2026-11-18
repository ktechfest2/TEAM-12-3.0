# T-06. Review queue screen

- Owner:
- Depends on: T-04
- Estimate: M

## Goal

A reviewer sees pending claims, edits the summary, approves translations and approves or escalates.

## Context

Web `features/` structure; ADR 0003.

## Acceptance criteria

- [ ] `features/review/` with list and detail components and tests
- [ ] Shows the cited official passage beside the draft answer
- [ ] Approve button disabled until every target language has an approved translation
- [ ] Uses the generated API client only
- [ ] `make verify` passes

## Files likely touched

apps/web/src/features/review/, pages/review-queue-page.tsx

## Questions

