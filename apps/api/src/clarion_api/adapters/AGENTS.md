# AGENTS.md (adapters)

To add a provider:

1. Implement the area Protocol in a new module named after the provider (`adapters/speech/acme.py`).
2. Import the vendor SDK only in that module; add it to ruff `banned-api` in `pyproject.toml` so nothing else can import it.
3. Add a branch to the area factory keyed on the `*_PROVIDER` value, and the value to the `Literal` in `config.py` and to `.env.example`.
4. Unit test with a fake transport. No real network in tests.
5. Credit it in `docs/CREDITS.md`.

Never let a vendor type leak through a Protocol signature. Return domain types or plain Python types.
