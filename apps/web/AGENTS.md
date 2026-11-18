# AGENTS.md (apps/web)

- File names are kebab case; components are named exports; no default exports; no `console.log`. Biome enforces all three.
- Call the API only through `src/lib/api/client.ts`. Never hand write API types; run `make contract` from the repo root after API changes.
- Read environment values only in `src/lib/env.ts`.
- Feature code lives in `src/features/<feature>/` with its tests beside it (`*.test.tsx`). Pages stay thin.
- Verdict wording comes from `features/claims/verdict.ts`. Do not add new labels or opinion words.
- Accessibility: every form control has a label, colour is never the only signal, pages work at 360 px wide.
