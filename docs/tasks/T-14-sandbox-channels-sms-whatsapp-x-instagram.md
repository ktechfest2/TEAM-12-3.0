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

- Not started, on purpose, for two reasons that need your decision.
- Consent: the criterion says never send to numbers that have not opted in, but `subscribers` stores only a keyed hash of the address (by design, architecture section 9), so a later send cannot recover the number. Sending needs an ADR for how to keep a reachable address safely (for example an encrypted column with a key held outside the database), plus a migration.
- Providers: the SMS provider is not named (`CHANNEL_SMS_PROVIDER` is a free string), and X and Instagram sending rules and sandbox access differ a lot. I did not want to write adapters against API shapes I cannot check. Name the SMS provider and confirm which of WhatsApp, X and Instagram have sandbox accounts.
- The `Channel` protocol, the console recorder and the Telegram adapter show the pattern each adapter should follow; `adapters/AGENTS.md` lists the steps.
