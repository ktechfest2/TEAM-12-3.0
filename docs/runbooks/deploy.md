# Deploy runbook

1. **Supabase:** create project; Database > Extensions > enable `vector`; copy the pooled connection string and change its scheme to `postgresql+asyncpg://`. Storage > create bucket `clarion-media` (public read); create S3 access keys.
2. **Render:** New > Blueprint > point at `infra/render.yaml`. Set every `sync: false` secret. Confirm the Key Value instance is attached as `REDIS_URL`.
3. **Migrate:** from a laptop with the production `DATABASE_URL` exported: `make db-migrate`.
4. **Vercel:** import repo, root directory `apps/web`, env `VITE_API_BASE_URL=<render api url>`. Add the Vercel URL to `CORS_ALLOWED_ORIGINS` on Render.
5. **Telegram:** create bot with BotFather, create a public channel, add the bot as admin, set `CHANNEL_TELEGRAM_BOT_TOKEN` and `CHANNEL_TELEGRAM_CHAT_ID`.
6. **Smoke test:** `curl <api>/health`; submit the timetable claim on the web app; confirm a Telegram message after T-04 lands.

Rollback: Render and Vercel both keep previous deploys; redeploy the last green one. Migrations must be backward compatible for one release.
