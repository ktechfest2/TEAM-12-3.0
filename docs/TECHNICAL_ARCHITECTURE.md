# Technical architecture

Status: foundation (19 November 2026). Owner: Team Triumph. Change this file in the same PR as any change to a boundary it describes.

## 1. What the system does

Clarion closes the **correction gap**: the time and language distance between a false election claim spreading and the official correction reaching the voter.

```
claim in ─▶ match to official source ─▶ human review ─▶ localise ─▶ render ─▶ broadcast ─▶ receipts
(web, Telegram)  (three verdicts only)   (approve/escalate)  (4 languages)  (SMS, voice, card...)  (every channel)
```

Measured outcome: minutes from approval to every channel live, shown on the broadcast board.

## 2. Principles

1. **People approve, machines draft.** No message reaches a channel without an approved review and approved translations (`domain/rules.py`).
2. **Point to sources, never to opinions.** Three verdicts: `confirmed`, `contradicted`, `no_official_statement`. The first two must cite a stored official passage.
3. **Vendor neutral core.** Domain and services depend on protocols. Vendors sit in `adapters/`. Configuration names describe roles (`LLM_*`, `SPEECH_*`, `STORAGE_*`), not companies.
4. **Standard protocols for infrastructure.** Postgres, Redis and S3 are reached through their protocols, so any compliant provider works.
5. **Works offline by default.** `APP_ENV=test` or `*_PROVIDER=fake` swaps every external service for a deterministic fake. The full flow and every test run without keys or network.
6. **One gate.** `make verify` is the definition of done for people, agents and CI.

## 3. System context

```
                 ┌──────────────┐        ┌───────────────────────────┐
 citizens ──────▶│  web (Vercel) │──HTTPS▶│  API (FastAPI on Render)  │──▶ Gemini (LLM adapter)
 reviewers ─────▶│  React, Vite  │        │  routes ▸ services ▸ domain│──▶ speech API (adapter)
 Telegram users ─────────────────────────▶│  adapters ▸ repositories  │──▶ Telegram, SMS, WhatsApp...
                 └──────────────┘        └──────┬──────────┬─────────┘
                                                 │          │ enqueue
                                    Postgres+pgvector   Redis (Render Key Value)
                                    (Supabase)                │
                                                 ▲    ┌──────┴────────┐
                                                 └────│ worker (taskiq)│──▶ channels, renderers
                                                      └───────────────┘
                                    S3 storage (Supabase Storage) ◀── audio, cards, posters, video
```

## 4. Repository layout

```
apps/api/src/clarion_api/
  config.py            only reader of environment variables
  observability.py     structured logging
  domain/              entities, enums, publish rules. Pure Python. No I/O.
  services/            use cases: matching, localisation, rendering, integrity, broadcasting
  adapters/            vendor boundary: llm/, speech/, channels/, storage/ (Protocol + fake + real)
  repositories/        persistence boundary: Protocol + memory + sql (REPOSITORY_BACKEND)
  db/                  SQLAlchemy tables and session; used only by repositories/sql.py
  api/                 FastAPI routes, request/response schemas, dependency container
  worker/              taskiq broker and queued jobs
  data/                seed official passages for demo and tests
apps/web/src/
  lib/                 env, typed API client (generated from contracts/openapi.json)
  features/<feature>/  components, hooks and tests for one feature
  pages/               route level screens, thin, compose features
  components/          shared layout and UI pieces
contracts/openapi.json  the API contract; web types are generated from it
```

### Dependency direction (enforced by review and lint)

```
api  ──▶ services ──▶ domain
  │          │
  └────▶ adapters (protocols) ◀── implemented by vendor modules
  └────▶ repositories (protocols) ◀── memory.py, sql.py
worker ──▶ services
```

- `domain` imports nothing from the app.
- `services` import `domain`, adapter **protocols** and repository **protocols** only.
- Vendor SDKs are imported only in their adapter module. Ruff rule `TID251` bans `google.genai` elsewhere; add new SDKs to that ban list when you add an adapter.

## 5. Core flows

### 5.1 Check a claim (built)

1. `POST /claims` with text and language.
2. `services.matching.match_claim` embeds the claim, retrieves the top passages from `SourceRepository.search`, and asks the LLM to choose a verdict and cite a passage by index.
3. Guard: if the model cites nothing valid or confidence is below 0.6, the verdict becomes `no_official_statement`. The model can never invent a source.
4. Response returns the verdict, rationale and the cited source.

### 5.2 Review and approve (T-06)

Reviewer opens the queue, edits the summary, approves, rejects or escalates. Approval creates a `Review` with `status=approved`. Translations are drafted by `services.localisation` and each is approved by a native speaker (`Localisation.approved_by`).

### 5.3 Seal (built: `services/integrity.py`)

After approval the master message is sealed: SHA-256 over a canonical JSON of claim, verdict, source, summary, approver and approved translations, chained to the previous message hash. The public correction page shows the hash so anyone can recompute it.

### 5.4 Render (T-07)

From one sealed message: SMS text sized with `services/rendering/sms.py` (GSM-7 or UCS-2, segment count, never strips tone marks), voice note via `SpeechSynthesizer` (OGG Opus), social card (HTML to PNG), poster (PDF), radio script and short captioned video (ffmpeg). Media goes to `ObjectStore`.

### 5.5 Broadcast (T-04, T-08)

`services.broadcasting.plan_deliveries` calls `ensure_publishable`, then creates one `Delivery` per channel and language. Each delivery is a queued job (`worker/tasks.py: deliveries.send`) with retries. A failing channel is recorded as `failed` and never blocks others. Receipts stream to the broadcast board over server sent events. Retraction sends a correction notice through the same path.

## 6. Data model

Tables (`db/tables.py`, migration `0001`): `source_passages` (with `embedding vector(768)` and an HNSW cosine index), `claims`, `messages` (verdict check constraint), `reviews`, `localisations`, `deliveries`, `subscribers` (address stored as a hash, consent time required), `audit_events`.

Naming: plural snake_case tables, `<entity>_id` foreign keys, `<verb>_at` UTC timestamps, constraint names from a fixed naming convention so migrations are stable.

## 7. Configuration

All settings live in `config.py` (`pydantic-settings`), documented in `.env.example`. Rules:

- Role based names: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `SPEECH_PROVIDER`, `STORAGE_ENDPOINT_URL`, `CHANNEL_<NAME>_*`.
- Standard names where a standard exists: `DATABASE_URL`, `REDIS_URL`.
- Secrets are `SecretStr` and never logged.
- The web app reads only `VITE_` variables, through `src/lib/env.ts`.

## 8. Quality gates

| Layer | Tool | Gate |
| --- | --- | --- |
| Python lint and format | ruff (broad rule set incl. security, async, tidy imports) | `ruff check`, `ruff format --check` |
| Python types | mypy strict with pydantic plugin | zero errors |
| Python tests | pytest, pytest-asyncio, coverage report | all pass; integration tests run in CI against Postgres+pgvector and Redis |
| TS lint and format | Biome (kebab case files, no default exports, no console) | `biome ci` |
| TS types | tsc strict, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` | zero errors |
| TS tests | Vitest with jsdom and Testing Library | all pass |
| Contract | `contracts/openapi.json` regenerated and diffed | no drift in CI |
| Commits | pre-commit: ruff, biome, gitleaks, private key check, Conventional Commits | on every commit |

## 9. Security and safety

- Publish rules are domain code with tests; weakening them needs an ADR.
- Subscriber phone numbers are hashed; raw numbers only pass through the channel adapter at send time.
- No personal data in logs at info level. No message bodies in logs.
- LLM spend capped by `LLM_MONTHLY_BUDGET_USD` (enforcement is task T-10).
- Reviewer access requires an invite code until proper auth lands (T-11).

## 10. Deployment

Web on Vercel (`apps/web/vercel.json`). API and worker on Render from one Docker image (`apps/api/Dockerfile`, `infra/render.yaml`). Queue on Render Key Value. Postgres and object storage on Supabase, reached only through Postgres and S3 protocols. See `infra/README.md` for the swap table and `docs/runbooks/deploy.md`.

## 11. Known limits

- Repositories are in memory by default and reset on restart. Set `REPOSITORY_BACKEND=sql` for Postgres.
- Only the Telegram channel adapter is real. SMS, WhatsApp, X and Instagram adapters are tasks.
- Seed passages paraphrase official statements as reported by news and fact checking outlets. Replace with primary INEC text before any public demo.
- Translation and voice quality must be judged by native speakers; nothing automated measures it.
