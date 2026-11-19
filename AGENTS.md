# AGENTS.md (root)

Instructions for any coding agent (Claude Code, Codex, Cursor, Gemini CLI) and for people. Nested `AGENTS.md` files add local rules; the closest one to the file you are editing wins on conflict, and this file always applies.

## Mission

Clarion closes the correction gap: the time and language distance between an election rumour spreading and the official correction reaching the voter. Every change should make that path faster, more trustworthy or easier to verify.

## Non negotiables

1. **Run `make verify` before you say a task is done.** Paste the final lines of its output in your summary or PR. If you could not run it, say so plainly.
2. **Never publish without a human approval.** No code path may send to a channel unless the message has an approved review. This is enforced in `domain/` and tested; do not weaken it.
3. **The verdict has exactly three values:** `confirmed`, `contradicted`, `no_official_statement`. Never add "true", "false", "misleading" or opinions.
4. **Every verdict cites an official source passage.** `confirmed` and `contradicted` without a citation is a bug.
5. **No secrets in code, tests, fixtures or logs.** Read config only through `apps/api/src/clarion_api/config.py` or `apps/web/src/lib/env.ts`.
6. **No vendor names in core code.** Vendors live behind adapters (`adapters/llm`, `adapters/speech`, `adapters/channels`, `adapters/storage`). Domain and services import protocols, never SDKs.
7. **All work is new and credited.** Do not paste code from earlier projects. Add every new dependency to `docs/CREDITS.md` in the same change.

## Commands

| Command | What it does |
| --- | --- |
| `make setup` | Install Python and JS dependencies and the git hooks |
| `make dev` | Run API, worker and web together |
| `make fmt` | Format everything (ruff format, biome format) |
| `make lint` | Lint everything (ruff, biome) |
| `make typecheck` | mypy strict and tsc |
| `make test` | pytest and vitest |
| `make contract` | Export OpenAPI and regenerate web types |
| `make verify` | Everything above, as CI runs it |
| `make demo-reset CONFIRM=1` | Wipe workspace data and queue the demo claims (sql backend, never production) |
| `make deploy HOST=<ssh host> CMD=up` | Self hosted VPS deploy: init, up, status, logs, backup, destroy (see docs/deploy) |

Run one app only: `make -C apps/api verify` or `make -C apps/web verify`.

## How to take a task

1. Open `docs/tasks/BOARD.md`. Pick the highest task in **Ready** whose dependencies are done.
2. Move it to **In progress** with your name or agent name. One task per branch: `task/<id>-<short-name>`.
3. Read the task file in `docs/tasks/`, the nearest `AGENTS.md`, and any ADR it links.
4. Write or update the test first when behaviour changes.
5. Make the smallest change that meets the acceptance criteria.
6. Run `make verify`. Fix until green.
7. Update docs touched by the change (README of the folder, architecture, credits).
8. Move the task to **Review** and open a PR using the template.

## When you are unsure

- A change that crosses a boundary in `docs/TECHNICAL_ARCHITECTURE.md`, adds a dependency, or changes a public API or database table needs an ADR in `docs/adr/` first. Copy `0000-template.md`.
- If acceptance criteria are ambiguous, write the question at the bottom of the task file and pick the safest reading. Never guess on anything that sends messages to real people.

## Style in one breath

Python: snake_case, typed everywhere, ruff and mypy strict. TypeScript: camelCase, PascalCase components, kebab case file names, biome. Full rules in `docs/CONVENTIONS.md`.

## Commit messages

Conventional Commits: `feat(api): add sms segment counter`, `fix(web): ...`, `docs: ...`, `chore: ...`, `test: ...`. Scope is `api`, `web`, `docs`, `infra` or `repo`.
