# T-07. Renderers: SMS text, voice note, social card, poster, QR

- Owner:
- Depends on: T-04, T-13
- Estimate: L

## Goal

One approved message becomes every format a channel needs.

## Context

TECHNICAL_ARCHITECTURE 5.4; `services/rendering/sms.py`.

## Acceptance criteria

- [ ] SMS renderer shortens to a target segment count and appends the short link; never strips tone marks
- [ ] Voice note via `SpeechSynthesizer`, stored as OGG Opus
- [ ] Social card PNG and poster PDF include verdict, source name and QR code to the public page
- [ ] Each renderer has a unit test using fakes
- [ ] `make verify` passes

## Files likely touched

services/rendering/, adapters/storage/

## Questions
