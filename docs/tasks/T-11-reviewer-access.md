# T-11. Reviewer access

- Owner: claude
- Depends on: T-04
- Estimate: S

## Goal

Only invited reviewers can approve or broadcast.

## Context

`config.py` auth settings.

## Acceptance criteria

- [x] Invite code exchange returns a signed token; review and broadcast routes require it
- [x] Tests for missing and invalid tokens
- [x] `make verify` passes

## Files likely touched

api/routes/, api/deps.py

## Questions

- Reviewer identity now comes from the token (`reviewer_name` at exchange), so `reviewer_id` and `approved_by` were removed from request bodies. All `/messages` routes need a token; `/claims` stays public. New setting `AUTH_TOKEN_TTL_MINUTES` (default 720) and production refuses the placeholder `AUTH_JWT_SECRET`; add both to `.env.example` by hand (the agent cannot edit it).
