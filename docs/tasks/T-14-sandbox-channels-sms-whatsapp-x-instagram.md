# T-14. Sandbox channels: SMS, WhatsApp, X, Instagram

- Owner:
- Depends on: T-04
- Estimate: L

## Goal

The same broadcast reaches test numbers and test accounts on more channels.

## Context

`adapters/channels/`; root AGENTS rule on consent.

## Acceptance criteria

- [ ] One adapter per channel behind the `Channel` protocol, enabled only when its env values are set
- [ ] Never sends to numbers that have not opted in
- [ ] Each adapter unit tested with a fake HTTP transport
- [ ] `make verify` passes

## Files likely touched

adapters/channels/

## Questions
