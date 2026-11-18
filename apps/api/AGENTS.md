# AGENTS.md (apps/api)

## Layers and what may import what

| Package | May import | Must not import |
| --- | --- | --- |
| `domain` | stdlib, pydantic | anything else in the app, any I/O |
| `services` | `domain`, adapter and repository **protocols** | vendor SDKs, `db`, FastAPI |
| `adapters/*` | `domain`, its vendor SDK (only in its own module) | `services`, `api` |
| `repositories` | `domain`, `db` (sql implementation only) | `services`, `api` |
| `api` | everything above | business rules (put them in services or domain) |
| `worker` | `services`, `api.container` | FastAPI request objects |

## Rules

- Read settings only via `config.get_settings()` or the container. Never `os.environ` outside `config.py` and test setup.
- Every route has an explicit `operation_id`, typed request and response models in `api/schemas.py`, and a test in `tests/api/`.
- Changing `api/schemas.py` means running `make openapi` (or `make contract` from root) and committing `contracts/openapi.json`.
- New table or column: change `db/tables.py`, then `make db-revision m="..."`, review the generated migration by hand.
- Logging: `get_logger(__name__)`, event names as `noun.verb` (`delivery.send.requested`), no secrets, no phone numbers, no message bodies.

## Verify

`make verify` here for speed, `make verify` at root before finishing.
