# 0006. Self hosted VPS deploy behind Cloudflare

- Status: accepted
- Date: 2026-11-19
- Deciders: Team Triumph

## Context

Contributors cannot create Render or Vercel projects for the team. The team has a small ARM VPS (2 CPUs, about 12 GB RAM) that already runs other containers and a host Caddy that owns ports 80 and 443. The domain is on Cloudflare, with the record proxied to the VPS address.

## Options considered

1. Keep Render and Vercel only: blocked by access.
2. Cloudflare Tunnel (`cloudflared`): no open ports, but the DNS record then points at the tunnel, not the VPS, and adds a service to run.
3. One compose project on the VPS, with the existing host Caddy as the front door and a proxied A record: no new public ports, reuses TLS.

## Decision

Option 3. One compose project named `clarion` runs Postgres with pgvector, Redis, the API, the worker and an nginx web container. Only the web container publishes a port, bound to `127.0.0.1:18080`. The host Caddy proxies the hostname to it through a snippet in `/etc/caddy/conf.d/`, added by one `import` line in the shared Caddyfile. nginx serves the web build, sends `/api/*` to the API (prefix stripped) and serves media from a local volume. Cloudflare SSL mode is Full (strict).

Storage is a local volume through the existing `LocalObjectStore`; the S3 adapter stays available. Secrets that deployers should not invent (database password, signing secret, webhook secret) are generated into a mode 700 state directory. `infra/deploy/clarion.sh` provisions, updates, backs up and destroys, touching only resources labelled with the `clarion` project.

## Consequences

Single node and no automatic backups beyond `clarion.sh backup`. Rolling back means redeploying an earlier commit. The Render and Vercel files remain as the managed option. The shared Caddyfile gets one extra line; `destroy` removes the snippet and that line when no other snippets exist. Cloudflare Bot Fight Mode can block Telegram's webhook calls, so `/api/webhooks/telegram` needs a skip rule.
