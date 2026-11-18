# Conventions

## Naming

| Thing | Rule | Example |
| --- | --- | --- |
| Python modules, functions, variables | snake_case | `match_claim`, `source_passages` |
| Python classes, enums | PascalCase | `MasterMessage`, `Verdict` |
| Python constants | UPPER_SNAKE | `TOP_K_PASSAGES` |
| Enum values | lower snake strings | `no_official_statement` |
| TS files | kebab case | `verdict-card.tsx` |
| React components | PascalCase, named export | `export function VerdictCard` |
| TS functions, variables | camelCase | `submitClaim` |
| API paths | plural nouns, kebab case | `/claims`, `/tools/sms-size` |
| API operation ids | camelCase verb first | `createClaim` |
| JSON fields | snake_case (matches Python) | `document_title` |
| Database tables | plural snake_case | `deliveries` |
| Env variables | ROLE_THING, no vendor names except under CHANNEL_<NAME>_ | `LLM_API_KEY` |
| Branches | `task/<id>-<short-name>` | `task/T-02-sql-repositories` |
| Commits | Conventional Commits | `feat(api): add sql claim repository` |

Language codes are ISO 639: `en`, `yo`, `ha`, `ig`, `pcm`.

## Writing for users

Plain English, short sentences, no jargon. The three verdict labels are fixed in `apps/web/src/features/claims/verdict.ts`. Never use "true", "false", "fake news" or "misleading" as verdicts.

## Python

- Typed everything. `Any` only at serialisation edges.
- Domain models are frozen pydantic models; change them with `model_copy(update=...)`.
- Async I/O everywhere. No blocking calls in request handlers; use `asyncio.to_thread` if unavoidable.
- New external service: Protocol in `adapters/<area>/base.py`, fake in `fake.py`, real provider in its own module, wired in the area `__init__.py` factory, SDK added to ruff `banned-api`.
- Errors: raise domain errors from `domain/errors.py`; the API maps them to responses.

## TypeScript

- Feature folders own their components, hooks and tests. Pages only compose features.
- Server data goes through TanStack Query and the generated client in `src/lib/api`. Never hand write API types.
- No default exports (except config files). No `console.log`.

## Tests

- Name tests after behaviour: `test_unreviewed_message_is_blocked`.
- Unit tests use fakes, never network. Integration tests are marked `integration` and run in CI.
- Every bug fix starts with a failing test.
