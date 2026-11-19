# T-16. Self hosted VPS deploy behind Cloudflare

- Owner: claude
- Depends on: T-04
- Estimate: L

## Goal

A contributor with ssh access to a small VPS can run one command to bring Clarion up at a Cloudflare proxied hostname, and one command to remove every trace of it, storage included.

## Context

ADR 0006; `infra/deploy/`; `docs/deploy/`. The VPS already runs a host Caddy on ports 80 and 443 for other projects.

## Acceptance criteria

- [x] One compose project runs Postgres with pgvector, Redis, API, worker and a web container, with no host port except `127.0.0.1:18080`
- [x] The only values a deployer supplies are the hostname, LLM, auth invite code and channel settings; database, queue and storage settings are generated or derived
- [x] `clarion.sh up` is idempotent and ends with a passing health check; `destroy` removes containers, volumes, images, network, state and the Caddy snippet, and reports anything left
- [x] The script only touches resources labelled with the `clarion` compose project
- [x] `backup` writes a Postgres dump and a media archive
- [x] Docs: root README deploy section, `docs/deploy/`, updated runbook and infra README
- [x] `make verify` passes

## Files likely touched

infra/deploy/, docs/deploy/, docs/adr/0006-*.md, README.md, Makefile, apps/api/Dockerfile, apps/api/src/clarion_api/config.py

## Questions

- Tested on the team VPS (aarch64, Ubuntu 24.04, shared with another stack): `up` from nothing, the full review to broadcast flow through Caddy and nginx (sign in, claim, translate, seal, send, live stream, renders, public page, media), `backup`, restore of that backup into a wiped database and media volume, a second `up` (idempotent), and `destroy` (nothing labelled `clarion` left; the shared Caddyfile checksum identical to before; the other stack untouched). Tested with `DOMAIN=clarion.localhost` so no real DNS or Let's Encrypt request was made.
- Not tested: a real proxied Cloudflare hostname. `clarion.triumphsystems.tech` currently resolves to two addresses that are not the VPS and not Cloudflare, so change that DNS record (proxied A record to the VPS address) before `up` with the real `DOMAIN`.
- The Caddy `import` line is added to the shared Caddyfile with sudo (approved) and removed again by `destroy` when no other snippet exists.
- Added `env_ignore_empty=True` to settings so blank optional values in compose count as unset. Added `.gitattributes` so shell scripts keep LF on Windows checkouts.
- `destroy` cannot delete the Cloudflare DNS record (no token by design); it reminds you.
