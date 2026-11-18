# contracts

`openapi.json` is generated from the API (`make contract`) and committed. The web app generates `src/lib/api/schema.gen.ts` from it. CI fails if the committed file is out of date, so API and web can never drift silently.
