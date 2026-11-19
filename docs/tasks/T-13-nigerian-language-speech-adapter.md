# T-13. Nigerian language speech adapter

- Owner: claude
- Depends on: T-01
- Estimate: S

## Goal

Approved text becomes a voice note in Yoruba, Hausa, Igbo and Pidgin.

## Context

ADR 0002; `adapters/speech/`.

## Acceptance criteria

- [ ] Pick the provider after native speakers rate sample clips; record the choice in an ADR. The team chose Spitch and ADR 0007 is written as proposed. The native speaker rating still needs a person.
- [x] Adapter module plus factory entry; `SPEECH_PROVIDER` value added (`spitch`, plus `SPEECH_VOICES` and `SPEECH_TIMEOUT_SECONDS`)
- [x] Credits updated
- [ ] `make verify` passes (runs in the team VM, not yet run for this change)

## Files likely touched

adapters/speech/, docs/adr/, docs/CREDITS.md

## Questions

- Not started, on purpose. Criterion 1 says to pick the provider after native speakers rate sample clips, and to record the choice in an ADR. That needs people listening to Yoruba, Hausa, Igbo and Pidgin samples, which I cannot do or guess. Candidates named in `docs/CREDITS.md`: 9jaLingo and Spitch.
- Resolved 2026-11-19: the team picked Spitch on price, its explicit `ogg_opus` format, and an existing key (ADR 0007). The adapter calls the HTTP API directly; endpoint and fields were read from the published `spitch` 1.50.0 SDK, because the docs site renders only in a browser. No SDK is installed, so no `banned-api` entry is needed.
- Open: Spitch documents no Pidgin voice. Pidgin is read by the English voice (`john`, language `en`) until `SPEECH_VOICES` names one. Native speakers should rate that clip too.
- Open: the default voices (`sade`, `amina`, `ngozi`, `john`) are taken from the SDK's voice list and its Yoruba example. Only `sade` for Yoruba is confirmed there. Check the others against the Spitch dashboard voice list.
- Earlier note, kept for history: when a provider is chosen, add `adapters/speech/<name>.py` that returns OGG Opus (the renderer in `services/rendering/voice.py` already refuses anything else), a factory branch, the `SPEECH_PROVIDER` value, a `banned-api` entry if it has an SDK, and credits.
