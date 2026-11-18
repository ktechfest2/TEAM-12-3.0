# migrations

Alembic migrations. `make db-migrate` applies them; `make db-revision m="..."` autogenerates a new one from `db/tables.py` (review it by hand). Preview SQL without a database: `uv run alembic upgrade head --sql`.
