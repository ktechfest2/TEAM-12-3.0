# repositories

Persistence protocols (`base.py`) with two implementations:

- `memory.py`: in process, resets on restart. The default (`REPOSITORY_BACKEND=memory`).
- `sql.py`: Postgres with pgvector cosine search using the HNSW index (`REPOSITORY_BACKEND=sql`).

Both must pass the shared behaviour checks in `tests/support/repository_contract.py`. The SQL run is an integration test (`RUN_INTEGRATION=1` and a `DATABASE_URL` with pgvector).
