# T-02. SQL repositories with pgvector search

- Owner: claude
- Depends on: T-01
- Estimate: M

## Goal

Claims and sources persist in Postgres and similarity search uses pgvector.

## Context

TECHNICAL_ARCHITECTURE sections 4 and 6; `repositories/base.py`, `repositories/memory.py`, `db/tables.py`.

## Acceptance criteria

- [x] `repositories/sql.py` implements `SourceRepository` and `ClaimRepository` with SQLAlchemy async sessions
- [x] `search` orders by cosine distance using the HNSW index
- [ ] New setting `REPOSITORY_BACKEND=memory|sql` (add to `.env.example` and `config.py`); container picks the implementation
- [x] Integration tests in `tests/integration/` cover add, get and search (run in CI with `RUN_INTEGRATION=1`)
- [x] `make verify` passes

## Files likely touched

apps/api/src/clarion_api/repositories/sql.py, api/container.py, config.py, tests/integration/

## Questions

- `.env.example` could not be edited (access denied for the agent). Setting is in `config.py`; add `REPOSITORY_BACKEND=memory` to `.env.example` by hand. Criterion left unticked.
