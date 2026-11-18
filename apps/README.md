# apps

| App | Stack | Runs on |
| --- | --- | --- |
| [api](api/) | Python 3.13, FastAPI, taskiq worker | Render (Docker) |
| [web](web/) | React 19, Vite, Tailwind, TanStack Query | Vercel |

Each app has its own `Makefile` with the same target names (`setup`, `dev`, `fmt`, `lint`, `typecheck`, `test`, `verify`).
