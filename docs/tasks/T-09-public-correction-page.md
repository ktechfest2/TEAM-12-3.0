# T-09. Public correction page

- Owner: claude
- Depends on: T-04
- Estimate: S

## Goal

Anyone who scans the QR code sees the claim, verdict, official source, approver, time and integrity hash.

## Context

`services/integrity.py`.

## Acceptance criteria

- [x] Public read endpoint, no auth, no personal data
- [x] Page recomputes nothing client side but shows the hash and how to verify it
- [x] Works on a small Android screen
- [x] `make verify` passes

## Files likely touched

api/routes/, apps/web/src/pages/public-correction-page.tsx

## Questions

- Verifying a seal needs the previous message hash, which the schema did not store. Seals are now recorded in `audit_events` (`message.sealed`, detail = previous hash), and the public record publishes the exact canonical JSON so anyone can run SHA-256 on it. The server also reports `integrity_verified`.
- The page lays out in one column with long values set to wrap, which is meant for 360 px screens. It has not been looked at on a real Android phone; please check it before the demo.
- The approver is shown by the name given at sign in (a reviewer name, not a citizen). Only approved and sealed corrections are public; drafts return 404.
