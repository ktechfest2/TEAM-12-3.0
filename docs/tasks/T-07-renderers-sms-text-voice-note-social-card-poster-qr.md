# T-07. Renderers: SMS text, voice note, social card, poster, QR

- Owner: claude
- Depends on: T-04, T-13
- Estimate: L

## Goal

One approved message becomes every format a channel needs.

## Context

TECHNICAL_ARCHITECTURE 5.4; `services/rendering/sms.py`.

## Acceptance criteria

- [x] SMS renderer shortens to a target segment count and appends the short link; never strips tone marks
- [x] Voice note via `SpeechSynthesizer`, stored as OGG Opus
- [x] Social card PNG and poster PDF include verdict, source name and QR code to the public page
- [x] Each renderer has a unit test using fakes
- [x] `make verify` passes

## Files likely touched

services/rendering/, adapters/storage/

## Questions

- Voice notes depend on the speech adapter returning OGG Opus. The renderer refuses any audio that is not an Ogg container (checks the `OggS` header) rather than storing something Telegram cannot play as a voice note. The real adapter is T-13.
- Renditions are produced on demand by `POST /messages/{id}/renditions` and not stored in a table (there is no renditions table); media files are stored through the object store.
- The card and poster are English only (see architecture 5.4). I looked at one rendered card and it reads well; the poster PDF has not been viewed by eye.
- Radio script and short video formats exist in the enum but are outside this task's acceptance criteria and were not built.
