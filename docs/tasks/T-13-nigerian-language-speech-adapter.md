# T-13. Nigerian language speech adapter

- Owner:
- Depends on: T-01
- Estimate: S

## Goal

Approved text becomes a voice note in Yoruba, Hausa, Igbo and Pidgin.

## Context

ADR 0002; `adapters/speech/`.

## Acceptance criteria

- [ ] Pick the provider after native speakers rate sample clips; record the choice in an ADR
- [ ] Adapter module plus factory entry; `SPEECH_PROVIDER` value added
- [ ] Credits updated
- [ ] `make verify` passes

## Files likely touched

adapters/speech/, docs/adr/, docs/CREDITS.md

## Questions

