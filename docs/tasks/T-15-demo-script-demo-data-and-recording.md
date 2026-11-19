# T-15. Demo script, demo data and recording

- Owner: claude
- Depends on: T-06, T-08, T-09
- Estimate: M

## Goal

A three minute demo that runs live and has a recorded backup.

## Context

docs/product/.

## Acceptance criteria

- [x] `docs/product/demo-script.md` with timings and the exact claims to use
- [x] Demo reset command that seeds known data
- [ ] Recorded video under three minutes
- [x] `make verify` passes

## Files likely touched

docs/product/, apps/api/scripts/

## Questions

- The recorded video (criterion 3) needs a person at a screen and is not done. The script has a section on recording it.
- The reset deletes workspace data, so it needs `REPOSITORY_BACKEND=sql`, `CONFIRM=1` and refuses `APP_ENV=production`. It keeps official sources.
- The jollof rice claim I first picked got `confirmed` from the offline model (it shares words with the PVC passage), caught by `tests/unit/test_demo.py`. The live claim is now about ballots through a phone app. Run all three claims once with the real model before presenting.
- The script lists what is placeholder (fake translations and voice, one test channel) so the presenter does not over claim.
