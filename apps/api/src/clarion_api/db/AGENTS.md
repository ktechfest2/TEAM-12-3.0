# AGENTS.md (db)

- Follow the naming convention in `tables.py`. Constraint names come from `NAMING_CONVENTION`; do not hand name them.
- Every schema change ships with an Alembic migration that has a working `downgrade`.
- Keep `EMBEDDING_DIMENSIONS` in step with `LLM_EMBEDDING_DIMENSIONS` and the migration.
