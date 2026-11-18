# AGENTS.md (repositories)

- Repositories return domain models, never SQLAlchemy rows.
- Memory and SQL implementations must pass the same behaviour tests; write tests against the Protocol and run them for both.
- Only `sql.py` may import from `db/`.
