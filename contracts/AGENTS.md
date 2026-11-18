# AGENTS.md (contracts)

- Never edit `openapi.json` by hand. Change the API schemas in `apps/api/src/clarion_api/api/schemas.py`, then run `make contract` from the repo root.
- A removed or renamed field is a breaking change: note it in the PR and update every web caller in the same PR.
