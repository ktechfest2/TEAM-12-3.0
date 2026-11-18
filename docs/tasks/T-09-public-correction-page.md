# T-09. Public correction page

- Owner:
- Depends on: T-04
- Estimate: S

## Goal

Anyone who scans the QR code sees the claim, verdict, official source, approver, time and integrity hash.

## Context

`services/integrity.py`.

## Acceptance criteria

- [ ] Public read endpoint, no auth, no personal data
- [ ] Page recomputes nothing client side but shows the hash and how to verify it
- [ ] Works on a small Android screen
- [ ] `make verify` passes

## Files likely touched

api/routes/, apps/web/src/pages/public-correction-page.tsx

## Questions
