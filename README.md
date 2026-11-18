# Clarion

**One verified answer. Every channel. Every language. Within minutes.**

Clarion is a correction broadcast engine for Nigerian elections. A citizen sends a rumour, Clarion matches it to an official source, a human reviewer approves the answer, and one tap sends it as SMS, voice notes, social posts, a radio spot and a printable poster in Yoruba, Hausa, Igbo, Pidgin and English. Every output links back to the official source.

Built by Team Triumph for the KTech Fest 3.0 hackathon, "Every Vote, Every Voice".

## Repository map

| Path | What lives there |
| --- | --- |
| `apps/api` | Python FastAPI service and background worker |
| `apps/web` | React dashboard, reviewer queue and public correction pages |
| `contracts` | `openapi.json`, the single contract between API and web |
| `docs` | Architecture, decisions, conventions, product docs, task board |
| `infra` | Local services (Postgres with pgvector, Redis) and deployment notes |
| `scripts` | Repository wide scripts, including `verify.sh` |

## Quick start

Requirements: Python 3.13, [uv](https://docs.astral.sh/uv/), Node 22, pnpm 10, Docker (for local Postgres and Redis).

```bash
cp .env.example .env          # fill in keys; test mode needs none
make setup                    # install everything and the git hooks
make services-up              # Postgres with pgvector and Redis in Docker
make db-migrate               # apply database migrations
make dev                      # API on :8000, web on :5173
```

Without any API keys, `APP_ENV=test` runs every provider as an offline fake, so the whole flow works on a laptop.

## The one command that matters

```bash
make verify
```

Lint, format check, type check, tests and contract drift for both apps. CI runs the same script. Nothing is done until it passes.

## Documentation

- [Technical architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Conventions](docs/CONVENTIONS.md)
- [How agents and people work here](AGENTS.md)
- [Verification](docs/VERIFICATION.md)
- [Architecture decisions](docs/adr/)
- [Task board](docs/tasks/BOARD.md)

## Credits and declarations

All code in this repository was written during the hackathon. Libraries, models and AI coding assistants used are listed in [docs/CREDITS.md](docs/CREDITS.md), as the rules require.
