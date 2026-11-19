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

- Not started, on purpose. Criterion 1 says to pick the provider after native speakers rate sample clips, and to record the choice in an ADR. That needs people listening to Yoruba, Hausa, Igbo and Pidgin samples, which I cannot do or guess. Candidates named in `docs/CREDITS.md`: 9jaLingo and Spitch.
- When a provider is chosen: add `adapters/speech/<name>.py` that returns OGG Opus (the renderer in `services/rendering/voice.py` already refuses anything else), a factory branch, the `SPEECH_PROVIDER` value, a `banned-api` entry if it has an SDK, and credits.
