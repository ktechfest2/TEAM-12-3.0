# T-11. Reviewer access

- Owner:
- Depends on: T-04
- Estimate: S

## Goal

Only invited reviewers can approve or broadcast.

## Context

`config.py` auth settings.

## Acceptance criteria

- [ ] Invite code exchange returns a signed token; review and broadcast routes require it
- [ ] Tests for missing and invalid tokens
- [ ] `make verify` passes

## Files likely touched

api/routes/, api/deps.py

## Questions

