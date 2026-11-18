# AGENTS.md (domain)

- `rules.ensure_publishable` protects real people. Do not relax it. Changes need an ADR and new tests in `tests/unit/test_rules.py`.
- `Verdict` has exactly three members. Do not add more.
- Models are frozen. Use `model_copy(update=...)`.
- No imports from `services`, `adapters`, `repositories`, `db`, `api` or `worker`.
