# tests

| Folder | What | Needs |
| --- | --- | --- |
| `unit/` | domain rules, services, renderers, with fakes | nothing |
| `api/` | HTTP routes through an in process client | nothing |
| `integration/` | Postgres with pgvector, Redis | `RUN_INTEGRATION=1` and services (CI provides them) |

`factories.py` builds valid, publishable domain objects; override one field to make an invalid one.
