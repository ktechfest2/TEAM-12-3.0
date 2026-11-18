# apps/web

React dashboard, reviewer queue, broadcast board and public correction pages.

```bash
make setup     # pnpm install --frozen-lockfile
make dev       # http://localhost:5173 (expects the API on :8000)
make verify    # biome, tsc, vitest, vite build
make types     # regenerate the API client types from contracts/openapi.json
```

Structure: `src/lib` (env, API client), `src/features/<feature>` (components, hooks, tests), `src/pages` (route screens), `src/components` (shared UI). Routes are defined in `src/router.tsx`.
