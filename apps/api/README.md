# apps/api

FastAPI service and taskiq worker for Clarion.

```bash
make setup     # uv sync --frozen
make dev       # http://localhost:8000, docs at /docs
make worker    # background jobs (needs Redis)
make verify    # ruff, mypy strict, pytest
make openapi   # write ../../contracts/openapi.json
```

With `APP_ENV=test` or `LLM_PROVIDER=fake`, everything runs offline with deterministic fakes and seed sources loaded in memory. Try:

```bash
curl -s localhost:8000/claims -H 'content-type: application/json' \
  -d '{"text":"INEC has released a new 2027 campaign timetable graphic"}'
```

Layout and rules: see `AGENTS.md` here and `docs/TECHNICAL_ARCHITECTURE.md`.
