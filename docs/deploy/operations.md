# Operating a self hosted Clarion

All commands run from the repository root. Add `--host <ssh-host>` to run them against a server from your laptop. On the server itself, leave it out.

| Command | What it does |
| --- | --- |
| `clarion.sh init` | Creates the settings file `~/.clarion-deploy/deploy.env` from the example |
| `clarion.sh up` | Checks settings, generates secrets, builds, starts, configures Caddy, checks health. Safe to repeat |
| `clarion.sh update` | Same as `up`. Run it after pulling new code; the API applies database migrations on start |
| `clarion.sh status` | Container state, local and public health, whether the Caddy site is present |
| `clarion.sh logs [service]` | Follows logs. Services: `api`, `worker`, `web`, `postgres`, `redis` |
| `clarion.sh backup` | Writes a Postgres dump and a media archive to `~/.clarion-deploy/backups` (keeps the newest 14 of each) |
| `clarion.sh telegram-webhook` | Registers the Telegram webhook with the generated secret |
| `clarion.sh down` | Stops containers, keeps all data |
| `clarion.sh destroy` | Removes everything (see below) |

## Updating

```bash
git pull
infra/deploy/clarion.sh --host <ssh-host> update
```

Migrations must stay backward compatible for one release, because the old container keeps running until the new one is healthy. If an update fails, `git checkout` the previous commit and run `update` again.

## Backup and restore

```bash
infra/deploy/clarion.sh --host <ssh-host> backup
```

Copy `~/.clarion-deploy/backups` off the server for safety. Restoring the database replaces its current contents:

```bash
cd infra/deploy   # on the server, inside a checkout
P="docker compose -p clarion -f compose.yaml --env-file ~/.clarion-deploy/compose.env"
$P exec -T postgres psql -U clarion -d clarion -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
gunzip -c ~/.clarion-deploy/backups/clarion-db-<stamp>.sql.gz | $P exec -T postgres psql -U clarion -d clarion
$P exec -T api tar xzf - -C /data/media < ~/.clarion-deploy/backups/clarion-media-<stamp>.tar.gz   # media
$P restart api worker
```


## Removing everything

```bash
infra/deploy/clarion.sh --host <ssh-host> destroy
```

It asks you to type `destroy clarion`, then removes:

- the containers and the compose network
- the Postgres, Redis and **media volumes** (all stored data and files)
- the built images `clarion-api:local` and `clarion-web:local`
- the generated secrets and settings in `~/.clarion-deploy`
- the Caddy site, and the one `import` line it added to the shared Caddyfile when nothing else uses it (the Caddyfile returns to its original bytes; safety copies the script made are deleted)

Then it checks that nothing labelled `clarion` is left and tells you if anything is. It does not touch other stacks.

Options:

- `--yes` skips the typed confirmation (for scripts).
- `--purge-images` also removes the pulled base images (`pgvector`, `redis`, `nginx`, `node`) if nothing else uses them, and the Docker build cache.
- `--purge-backups` also deletes `~/.clarion-deploy/backups`. Without it, backups are kept.

After `destroy`, delete the proxied DNS record in Cloudflare (the script cannot, and does not hold a Cloudflare token).

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `up` stops with "DOMAIN ... must be a hostname" or "INVITE_CODE is empty" | Edit `~/.clarion-deploy/deploy.env` |
| `up` says a database volume exists but `secrets.env` is missing | The generated password was lost. Restore `~/.clarion-deploy/secrets.env`, or run `destroy` to start clean |
| `up` says port 18080 is in use | Another process holds it; the port is fixed in `compose.yaml` and the Caddy snippet |
| Site shows a Cloudflare 52x or 525/526 error | SSL mode must be Full (strict); check `status` shows the Caddy site present; check DNS points at the server |
| Redirect loop | Cloudflare SSL mode is Flexible; change it to Full (strict) |
| `/api/health` works locally but not publicly | `clarion.sh status`; `sudo journalctl -u caddy -n 50` for certificate errors (DNS must point at the server first) |
| Telegram bot never replies | Run `telegram-webhook`; check the WAF skip rule; `clarion.sh logs api` for 401s (secret mismatch) |
| Live board stays empty | The board lists sealed messages only. Seal one on the review screen, then press send |
| Language model errors or "budget used up" | `LLM_*` values in `deploy.env`; the monthly cap `LLM_MONTHLY_BUDGET_USD`; run `up` after editing |

Where things live on the server: settings and secrets in `~/.clarion-deploy`, the Caddy site in `/etc/caddy/conf.d/clarion.caddy`, data in Docker volumes `clarion_pgdata`, `clarion_redisdata` and `clarion_media`.
