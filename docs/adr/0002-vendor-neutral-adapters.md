# 0002. Vendor neutral core with adapters

- Status: accepted
- Date: 2026-11-19

## Context

The hackathon stack is Gemini, Supabase, Render, Vercel and Telegram. Pilots after the hackathon may need different providers (cost, data residency, a partner's existing contracts).

## Options considered

1. Call vendor SDKs directly from services: fastest to write, expensive to change.
2. Protocols in `adapters/<area>/base.py`, one module per vendor, role based env names: small upfront cost, swaps are local.

## Decision

Option 2. Infrastructure with a standard protocol (Postgres, Redis, S3) is reached through that protocol, never a vendor SDK. Model, speech and channel vendors live behind Protocols with offline fakes. Ruff `banned-api` stops SDK imports outside adapters.

## Consequences

Every new vendor needs a fake and a factory entry. Tests never need keys. Moving from Supabase to any Postgres plus S3 store, or from Gemini to another model, touches one module and the env file.
