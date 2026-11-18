# AGENTS.md (api)

- Routes are thin: validate, call a service, map to a response schema. No business rules here.
- Never return domain models directly; map to `schemas.py` types so the public contract is explicit.
- Every route: `operation_id` in camelCase, explicit status code for creates, a test in `tests/api/`.
- After changing schemas or routes, run `make contract` from the repo root.
