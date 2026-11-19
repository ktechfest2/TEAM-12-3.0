# infra

Local services and deployment configuration.

## Local

`make services-up` starts Postgres 17 with pgvector and Redis 8 from `docker-compose.yml`. Data persists in the `pgdata` volume.

## Self hosted alternative

`infra/deploy/` runs the whole stack (Postgres with pgvector, Redis, API, worker, web) on one VPS behind Cloudflare, with one script to provision and remove it. See [docs/deploy/](../docs/deploy/README.md) and ADR 0006. The table below describes the managed option.

## Production mapping

| Need | Generic interface | Hackathon choice | Swap without code changes to |
| --- | --- | --- | --- |
| Web hosting | static build of `apps/web` | Vercel | Netlify, Cloudflare Pages, any CDN |
| API and worker | Docker image from `apps/api/Dockerfile` | Render web service and worker | Fly, Azure Container Apps, Cloud Run |
| Queue and cache | `REDIS_URL` | Render Key Value | Upstash, ElastiCache, self hosted Redis or Valkey |
| Database | `DATABASE_URL`, Postgres with pgvector | Supabase Postgres | Neon, RDS, self hosted |
| Media storage | `STORAGE_*`, S3 protocol | Supabase Storage (S3 endpoint) | R2, S3, MinIO |
| Language model | `LLM_PROVIDER` adapter | Gemini | any provider with an adapter |
| Speech | `SPEECH_PROVIDER` adapter | Nigerian language speech API | any provider with an adapter |

The app talks to Supabase only as Postgres and as an S3 endpoint. Do not add the Supabase client SDK to the API; that would tie the core to one vendor.

## Deploy

1. Create the Supabase project, enable the `vector` extension, copy the pooled connection string into Render as `DATABASE_URL` (use the `postgresql+asyncpg://` scheme).
2. Connect the repo in Render using `render.yaml`. Set the `sync: false` secrets in the dashboard.
3. Import `apps/web` into Vercel with root directory `apps/web` and set `VITE_API_BASE_URL` to the Render API URL.
4. Run migrations once: `render ssh` into the API or run `make db-migrate` locally against the production `DATABASE_URL`.

See `docs/runbooks/deploy.md` for the step by step checklist.
