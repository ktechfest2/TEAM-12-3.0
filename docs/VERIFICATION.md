# Verification

How anyone, especially a coding agent, proves a change works.

## The loop

1. Write or update a test that fails for the behaviour you want.
2. Implement.
3. `make -C apps/<app> verify` while iterating (faster).
4. `make verify` before you finish. It runs API checks, contract drift and web checks exactly as CI does.
5. Quote the last lines of the output in the PR or your summary.

## What each failure means

| Failure | Usual cause | Fix |
| --- | --- | --- |
| `ruff format --check` | unformatted code | `make fmt` |
| `ruff check` TID251 | vendor SDK imported outside its adapter | move the call into the adapter |
| mypy error | missing or wrong type | fix the type; do not add `# type: ignore` without a reason in the comment |
| `openapi.json changed` | API schema changed | `make contract`, commit both files |
| `biome ci` filename rule | file not kebab case | rename |
| tsc error in `schema.gen.ts` usage | API changed shape | run `make contract`, then fix callers |

## Manual checks that tests cannot do

- Native speaker reads every translation template before a demo.
- Play each generated voice note once.
- Send one real Telegram message to the demo channel after any channel change.
- Open the public correction page on a cheap Android phone.

## Never

- Never mark a task done with a failing or skipped check.
- Never delete or weaken a test in `tests/unit/test_rules.py` to make something pass.
- Never call real providers from tests.
