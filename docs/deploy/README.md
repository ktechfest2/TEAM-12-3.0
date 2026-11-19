# Deploying Clarion

Two supported ways to run Clarion for real:

| Way | When to use it | Guide |
| --- | --- | --- |
| **Self hosted on a VPS** behind Cloudflare | You have ssh access to a small server and cannot create Render or Vercel projects. One command up, one command to remove everything | this section |
| Managed: Render, Vercel and Supabase | You own those accounts | [`infra/README.md`](../../infra/README.md) and [`docs/runbooks/deploy.md`](../runbooks/deploy.md) |

Decision record: [ADR 0006](../adr/0006-self-hosted-vps-deploy-behind-cloudflare.md).

## What runs

```
 browser ──▶ Cloudflare (proxied, SSL Full strict)
                │
                ▼
        host Caddy :443  ── one snippet in /etc/caddy/conf.d/clarion.caddy
                │
                ▼
     127.0.0.1:18080  ┌─────────────── docker compose project "clarion" ────────────────┐
                      │ web (nginx)  /        the built app                             │
                      │              /api/*   ──▶ api (FastAPI)  ──▶ postgres + pgvector │
                      │              /media/* ◀── media volume  ◀── api, worker          │
                      │                           worker (taskiq) ──▶ redis              │
                      └──────────────────────────────────────────────────────────────────┘
```

- Only `web` publishes a port, and only on loopback. Postgres, Redis and the API are reachable inside the compose network only, so they never clash with other stacks on the server.
- Media (voice notes, cards, posters) lives in a local Docker volume and is served at `/media/`.
- The whole stack uses roughly 200 MB of memory when idle, and each service has a memory cap.

## What you set, and what the script makes

You set only the things the app cannot guess:

- `DOMAIN`, `AUTH_REVIEWER_INVITE_CODE`
- `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_EMBEDDING_MODEL`, `LLM_MONTHLY_BUDGET_USD`
- `CHANNEL_TELEGRAM_BOT_TOKEN`, `CHANNEL_TELEGRAM_CHAT_ID`

The script generates the database password, the signing secret (`AUTH_JWT_SECRET`) and the Telegram webhook secret once, and keeps them in a mode 700 folder (`~/.clarion-deploy`) on the server. Database, queue and storage addresses are filled in by the compose file. Nothing secret is stored in the repository.

## Guides

1. [Set up the server and Cloudflare](vps-cloudflare.md): first deploy, DNS, TLS mode and the Telegram webhook.
2. [Operate it](operations.md): update, status, logs, backup and restore, remove everything, and troubleshooting.

## Quick reference

```bash
# from your laptop (sends your working tree over ssh; nothing is pushed)
infra/deploy/clarion.sh --host <ssh-host> init      # create the settings file on the server
# edit ~/.clarion-deploy/deploy.env on the server, then:
infra/deploy/clarion.sh --host <ssh-host> up
infra/deploy/clarion.sh --host <ssh-host> status
infra/deploy/clarion.sh --host <ssh-host> destroy   # removes everything, asks first
```

`make deploy HOST=<ssh-host> CMD=up` does the same.
