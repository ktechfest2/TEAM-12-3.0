# Credits and declarations

Update in the same change that adds a dependency or tool.

## AI coding assistants

- Claude (Anthropic), used for planning, scaffolding, code and documentation.

## AI models used by the product

- Google Gemini (language model: matching, translation drafts, screenshot reading).
- Spitch (speech generation for Yoruba, Hausa, Igbo and English voice notes), called over its HTTP API with HTTPX; no SDK is bundled. See ADR 0007.

## Python libraries

FastAPI, Uvicorn, Pydantic, pydantic-settings, SQLAlchemy, asyncpg, Alembic, pgvector, taskiq, taskiq-redis, redis-py, google-genai, HTTPX, structlog, qrcode, Pillow, cryptography (Fernet encryption of subscriber phone numbers, see ADR 0008). Development: Ruff, mypy, pytest, pytest-asyncio, pytest-cov, pre-commit.

## JavaScript libraries

React, React DOM, React Router, TanStack Query, openapi-fetch, openapi-typescript, Vite, @vitejs/plugin-react, Tailwind CSS, TypeScript, Biome, Vitest, jsdom, Testing Library.

## Design

Logo, icon set, colour palette and type scale were drawn for Clarion (see `docs/DESIGN.md`). Typography uses each device's system fonts; no web fonts or icon libraries are bundled.

## Data

Seed passages paraphrase INEC statements as reported by Africa Check, News Central, Premium Times and Leadership; each links its source in `apps/api/src/clarion_api/data/seed_sources.json`.

## Services

Vercel, Render, Supabase, Cloudflare (DNS and proxy), Caddy (host reverse proxy), Telegram Bot API, TextBee (SMS gateway through an Android phone), X API v2 (posting). Container images for the self hosted deploy: pgvector/pgvector (PostgreSQL with pgvector), Redis, nginx, Node.js (build stage only). Object storage is reached through the S3 protocol (AWS Signature Version 4, implemented in `adapters/storage/s3.py` with HTTPX and the standard library; checked against the published AWS test vectors).
