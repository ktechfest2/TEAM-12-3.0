#!/usr/bin/env bash
# Provision, update, back up and remove a self hosted Clarion on a VPS that has Docker and Caddy.
#
#   infra/deploy/clarion.sh <command>                 run on the VPS
#   infra/deploy/clarion.sh --host <ssh host> <cmd>   run from your laptop; sends the working tree
#
# Commands: init | up | update | status | logs [service] | backup | telegram-webhook | sms-webhook | down | destroy
# Everything it creates carries the compose project label "clarion"; it never touches other stacks.
# Docs: docs/deploy/
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="clarion"
COMPOSE_FILE="$HERE/compose.yaml"
STATE_DIR="${CLARION_STATE_DIR:-$HOME/.clarion-deploy}"
LOOPBACK_PORT=18080
CADDYFILE="/etc/caddy/Caddyfile"
CADDY_DIR="/etc/caddy/conf.d"
CADDY_SNIPPET="$CADDY_DIR/clarion.caddy"
IMPORT_LINE="import /etc/caddy/conf.d/*.caddy"
IMPORT_MARK="# added by clarion-deploy"
KEEP_BACKUPS=14

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mwarning:\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

# ------------------------------------------------------------------ run from a laptop
if [[ "${1:-}" == "--host" ]]; then
  host="${2:-}"; [[ -n "$host" ]] || usage 1
  shift 2
  repo_root="$(cd "$HERE/../.." && pwd)"
  dest="clarion-deploy-src"   # a dedicated folder in the remote home; emptied on every run
  say "sending the working tree to $host:~/$dest"
  tar -C "$repo_root" --exclude=.git --exclude=node_modules --exclude=.venv --exclude='.env*' \
    --exclude=__pycache__ --exclude=.mypy_cache --exclude=.ruff_cache --exclude=.pytest_cache \
    --exclude=dist --exclude=var -cf - . |
    ssh "$host" "mkdir -p $dest && cd $dest && find . -mindepth 1 -delete && tar xf - && sed -i 's/\r\$//' infra/deploy/*.sh"
  args=""
  for a in "$@"; do args+=" $(printf '%q' "$a")"; done
  exec ssh -t "$host" "cd $dest && bash infra/deploy/clarion.sh$args"
fi

# ------------------------------------------------------------------ helpers
dc() { docker compose -p "$PROJECT" -f "$COMPOSE_FILE" --env-file "$STATE_DIR/compose.env" "$@"; }

var() {  # var KEY FILE -> last value of KEY=value in FILE, quotes stripped
  local v
  v="$(grep -E "^$1=" "$2" 2>/dev/null | tail -1 | cut -d= -f2- || true)"
  v="${v%\"}"; v="${v#\"}"; v="${v%\'}"; v="${v#\'}"
  printf '%s' "$v"
}

random_hex() { openssl rand -hex "$1"; }

project_ids() {  # project_ids <containers|volumes|networks>
  case "$1" in
    containers) docker ps -aq --filter "label=com.docker.compose.project=$PROJECT" ;;
    volumes) docker volume ls -q --filter "label=com.docker.compose.project=$PROJECT" ;;
    networks) docker network ls -q --filter "label=com.docker.compose.project=$PROJECT" ;;
  esac
}

preflight() {
  command -v docker >/dev/null || die "docker is not installed"
  docker compose version >/dev/null 2>&1 || die "docker compose v2 is not available"
  command -v openssl >/dev/null || die "openssl is required to generate secrets"
  command -v curl >/dev/null || die "curl is required"
}

placeholder_env() {  # compose needs the required variables even to tear down
  mkdir -p "$STATE_DIR"; chmod 700 "$STATE_DIR"
  if [[ ! -f "$STATE_DIR/compose.env" ]]; then
    printf 'DOMAIN=unset.invalid\nPOSTGRES_PASSWORD=unused\nAUTH_JWT_SECRET=unused\n' >"$STATE_DIR/compose.env"
    chmod 600 "$STATE_DIR/compose.env"
  fi
}

# ------------------------------------------------------------------ init and env
cmd_init() {
  mkdir -p "$STATE_DIR/backups"; chmod 700 "$STATE_DIR" "$STATE_DIR/backups"
  if [[ -f "$STATE_DIR/deploy.env" ]]; then
    say "settings already exist: $STATE_DIR/deploy.env"
  else
    install -m 600 "$HERE/deploy.env.example" "$STATE_DIR/deploy.env"
    say "created $STATE_DIR/deploy.env"
  fi
  echo "Edit it (hostname, invite code, LLM and channel values), then run: clarion.sh up"
}

prepare_env() {
  local file="$STATE_DIR/deploy.env" secrets="$STATE_DIR/secrets.env"
  [[ -f "$file" ]] || die "no settings yet; run: clarion.sh init"
  local domain; domain="$(var DOMAIN "$file")"
  [[ "$domain" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$ ]] ||
    die "DOMAIN in $file must be a hostname such as clarion.example.org"
  [[ -n "$(var AUTH_REVIEWER_INVITE_CODE "$file")" ]] ||
    die "AUTH_REVIEWER_INVITE_CODE in $file is empty; nobody could sign in to review"
  if [[ "$(var LLM_PROVIDER "$file")" == "gemini" ]]; then
    for k in LLM_API_KEY LLM_MODEL LLM_EMBEDDING_MODEL; do
      [[ -n "$(var "$k" "$file")" ]] || die "$k is required when LLM_PROVIDER=gemini"
    done
  fi
  if [[ "$(var SPEECH_PROVIDER "$file")" == "spitch" ]]; then
    [[ -n "$(var SPEECH_API_KEY "$file")" ]] || die "SPEECH_API_KEY is required when SPEECH_PROVIDER=spitch"
  fi

  if [[ ! -f "$secrets" ]]; then
    if docker volume inspect "${PROJECT}_pgdata" >/dev/null 2>&1; then
      die "a database volume exists but $secrets is missing, so its password is lost. Restore the file, or run: clarion.sh destroy"
    fi
    umask 077
    printf 'POSTGRES_PASSWORD=%s\nAUTH_JWT_SECRET=%s\nCHANNEL_TELEGRAM_WEBHOOK_SECRET=%s\n' \
      "$(random_hex 24)" "$(random_hex 32)" "$(random_hex 24)" >"$secrets"
    say "generated secrets in $secrets"
  fi

  # Key for subscriber phone numbers (ADR 0008). Generated once and kept: losing it makes
  # every stored number unreadable, so it lives in secrets.env next to the database password.
  if ! grep -q '^SUBSCRIBER_ENCRYPTION_KEY=' "$secrets"; then
    umask 077
    printf 'SUBSCRIBER_ENCRYPTION_KEY=%s\n' "$(openssl rand -base64 32 | tr '+/' '-_' | tr -d '\n')" >>"$secrets"
    say "generated the subscriber encryption key in $secrets"
  fi

  # Signing secret for incoming texts (ADR 0010). Paste it into the SMS gateway webhook.
  if ! grep -q '^CHANNEL_SMS_WEBHOOK_SECRET=' "$secrets"; then
    umask 077
    printf 'CHANNEL_SMS_WEBHOOK_SECRET=%s\n' "$(random_hex 32)" >>"$secrets"
    say "generated the incoming text webhook secret in $secrets"
  fi

  umask 077
  {
    grep -vE '^(POSTGRES_PASSWORD|AUTH_JWT_SECRET|CHANNEL_TELEGRAM_WEBHOOK_SECRET|SUBSCRIBER_ENCRYPTION_KEY|CHANNEL_SMS_WEBHOOK_SECRET)=' "$file" || true
    echo "POSTGRES_PASSWORD=$(var POSTGRES_PASSWORD "$secrets")"
    for k in AUTH_JWT_SECRET CHANNEL_TELEGRAM_WEBHOOK_SECRET SUBSCRIBER_ENCRYPTION_KEY CHANNEL_SMS_WEBHOOK_SECRET; do
      mine="$(var "$k" "$file")"
      echo "$k=${mine:-$(var "$k" "$secrets")}"
    done
  } >"$STATE_DIR/compose.env"
}

# ------------------------------------------------------------------ caddy
render_snippet() {
  cat <<EOF
# Managed by clarion-deploy. Removed by: clarion.sh destroy
$1 {
	reverse_proxy 127.0.0.1:$LOOPBACK_PORT {
		flush_interval -1
	}
}
EOF
}

caddy_manual() {
  cat <<EOF
Caddy was not changed (no passwordless sudo, or --no-caddy). To do it by hand:
  sudo mkdir -p $CADDY_DIR
  sudo tee $CADDY_SNIPPET <<'SNIP'
$(render_snippet "$1")
SNIP
  grep -qF '$IMPORT_LINE' $CADDYFILE || echo '$IMPORT_LINE' | sudo tee -a $CADDYFILE
  sudo caddy validate --config $CADDYFILE --adapter caddyfile && sudo systemctl reload caddy
EOF
}

caddy_install() {
  local domain="$1"
  command -v caddy >/dev/null || { warn "caddy is not installed on this machine"; caddy_manual "$domain"; return 0; }
  sudo -n true 2>/dev/null || { caddy_manual "$domain"; return 0; }

  local tmp backup="" added=0
  tmp="$(mktemp)"; render_snippet "$domain" >"$tmp"
  sudo mkdir -p "$CADDY_DIR"
  sudo install -m 644 "$tmp" "$CADDY_SNIPPET"; rm -f "$tmp"
  if ! sudo grep -qF "$IMPORT_LINE" "$CADDYFILE"; then
    backup="$CADDYFILE.clarion-backup-$(date +%s)"
    sudo cp -p "$CADDYFILE" "$backup"
    printf '\n%s\n%s\n' "$IMPORT_MARK" "$IMPORT_LINE" | sudo tee -a "$CADDYFILE" >/dev/null
    added=1
  fi
  if sudo caddy validate --config "$CADDYFILE" --adapter caddyfile >/dev/null 2>&1; then
    sudo systemctl reload caddy
    say "caddy now proxies $domain to 127.0.0.1:$LOOPBACK_PORT"
  else
    warn "caddy rejected the new configuration; undoing"
    sudo rm -f "$CADDY_SNIPPET"
    [[ "$added" == 1 ]] && sudo cp -p "$backup" "$CADDYFILE"
    die "caddy configuration was restored; check: sudo caddy validate --config $CADDYFILE"
  fi
}

caddy_remove() {
  command -v caddy >/dev/null || return 0
  sudo -n true 2>/dev/null || { warn "no passwordless sudo: remove $CADDY_SNIPPET and the import line in $CADDYFILE by hand, then reload caddy"; return 0; }
  sudo rm -f "$CADDY_SNIPPET"
  if ! compgen -G "$CADDY_DIR/*.caddy" >/dev/null && grep -qxF "$IMPORT_LINE" "$CADDYFILE"; then
    local backup="$CADDYFILE.clarion-backup-$(date +%s)"
    sudo cp -p "$CADDYFILE" "$backup"
    # drop our two lines and the blank line we added before them, so the file returns to its original bytes
    awk -v mark="$IMPORT_MARK" -v imp="$IMPORT_LINE" '
      { line[NR] = $0 }
      END { for (i = 1; i <= NR; i++) {
              if (line[i] == mark || line[i] == imp) continue
              if (line[i] == "" && line[i + 1] == mark) continue
              print line[i] } }' "$CADDYFILE" | sudo tee "$CADDYFILE.clarion-new" >/dev/null
    sudo mv "$CADDYFILE.clarion-new" "$CADDYFILE"
    sudo rmdir "$CADDY_DIR" 2>/dev/null || true
    if ! sudo caddy validate --config "$CADDYFILE" --adapter caddyfile >/dev/null 2>&1; then
      sudo cp -p "$backup" "$CADDYFILE"
      die "removing the import line broke the caddy config; it was restored from $backup"
    fi
  fi
  sudo systemctl reload caddy
  sudo rm -f "$CADDYFILE".clarion-backup-*   # safety copies this script made
  say "removed the clarion caddy configuration"
}

# ------------------------------------------------------------------ commands
cmd_up() {
  local no_caddy=0
  for a in "$@"; do [[ "$a" == "--no-caddy" ]] && no_caddy=1; done
  preflight
  mkdir -p "$STATE_DIR/backups"; chmod 700 "$STATE_DIR" "$STATE_DIR/backups"
  prepare_env
  if ss -tln 2>/dev/null | grep -q ":$LOOPBACK_PORT " && [[ -z "$(dc ps -q web 2>/dev/null)" ]]; then
    die "port $LOOPBACK_PORT is already in use by something else"
  fi
  say "building and starting the stack"
  dc up -d --build --wait --wait-timeout 300
  local domain; domain="$(var DOMAIN "$STATE_DIR/deploy.env")"
  if [[ "$no_caddy" == 1 ]]; then caddy_manual "$domain"; else caddy_install "$domain"; fi

  say "checking health"
  curl -fsS --retry 10 --retry-delay 2 --retry-connrefused "http://127.0.0.1:$LOOPBACK_PORT/api/health" ||
    die "the API did not answer; see: clarion.sh logs api"
  echo
  say "Clarion is running."
  echo "  local:   http://127.0.0.1:$LOOPBACK_PORT"
  echo "  public:  https://$domain  (needs a proxied DNS record in Cloudflare; see docs/deploy/)"
  echo "  next:    clarion.sh telegram-webhook   (if you set a Telegram bot token)"
}

cmd_status() {
  preflight; placeholder_env
  dc ps
  local domain; domain="$(var DOMAIN "$STATE_DIR/deploy.env")"
  echo
  if curl -fsS "http://127.0.0.1:$LOOPBACK_PORT/api/health" >/dev/null 2>&1; then
    echo "local health: ok"
  else echo "local health: DOWN"; fi
  if [[ -n "$domain" ]]; then
    if curl -fsS -m 8 "https://$domain/api/health" >/dev/null 2>&1; then echo "public health ($domain): ok"
    else echo "public health ($domain): not reachable (DNS, Cloudflare or Caddy not ready?)"; fi
  fi
  [[ -f "$CADDY_SNIPPET" ]] && echo "caddy snippet: present" || echo "caddy snippet: missing"
}

cmd_logs() { preflight; placeholder_env; dc logs -f --tail=100 "$@"; }

cmd_backup() {
  preflight; placeholder_env
  local stamp dir="$STATE_DIR/backups"
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"; mkdir -p "$dir"; chmod 700 "$dir"; umask 077
  [[ -n "$(dc ps -q postgres)" ]] || die "the stack is not running"
  dc exec -T postgres pg_dump -U clarion clarion | gzip >"$dir/clarion-db-$stamp.sql.gz"
  dc exec -T web tar czf - -C /srv/media . >"$dir/clarion-media-$stamp.tar.gz"
  say "wrote $dir/clarion-db-$stamp.sql.gz and $dir/clarion-media-$stamp.tar.gz"
  # keep the newest $KEEP_BACKUPS of each kind
  for kind in db media; do
    ls -1t "$dir"/clarion-$kind-* 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -f
  done
}

cmd_telegram_webhook() {
  preflight; placeholder_env
  local file="$STATE_DIR/deploy.env" token domain secret
  token="$(var CHANNEL_TELEGRAM_BOT_TOKEN "$file")"; domain="$(var DOMAIN "$file")"
  secret="$(var CHANNEL_TELEGRAM_WEBHOOK_SECRET "$STATE_DIR/compose.env")"
  [[ -n "$token" ]] || die "CHANNEL_TELEGRAM_BOT_TOKEN is not set in $file"
  [[ -n "$secret" ]] || die "run 'clarion.sh up' first so the webhook secret exists"
  curl -fsS "https://api.telegram.org/bot$token/setWebhook" \
    --data-urlencode "url=https://$domain/api/webhooks/telegram" \
    --data-urlencode "secret_token=$secret" >/dev/null
  say "Telegram will now call https://$domain/api/webhooks/telegram"
}

cmd_sms_webhook() {
  preflight; placeholder_env
  local domain secret
  domain="$(var DOMAIN "$STATE_DIR/deploy.env")"
  secret="$(var CHANNEL_SMS_WEBHOOK_SECRET "$STATE_DIR/compose.env")"
  [[ -n "$secret" ]] || die "run 'clarion.sh up' first so the webhook secret exists"
  say "In the TextBee dashboard: Webhooks, Add Webhook, event MESSAGE_RECEIVED"
  echo "  URL:            https://$domain/api/webhooks/sms"
  echo "  Signing secret: $secret"
  echo "  Then switch on Receive SMS in the TextBee app. Only texts starting with CLARION are used."
}

cmd_down() { preflight; placeholder_env; dc down; say "stopped; data volumes kept"; }

cmd_destroy() {
  local yes=0 purge_images=0 purge_backups=0
  for a in "$@"; do
    case "$a" in
      --yes) yes=1 ;; --purge-images) purge_images=1 ;; --purge-backups) purge_backups=1 ;;
      *) die "unknown option: $a" ;;
    esac
  done
  preflight; placeholder_env
  cat <<EOF
This permanently deletes Clarion from this machine:
  containers, the database, the queue, all stored media (volumes), the built images,
  the generated secrets, and the Caddy snippet. Other stacks are not touched.
EOF
  if [[ "$yes" != 1 ]]; then
    read -r -p "Type 'destroy clarion' to continue: " answer
    [[ "$answer" == "destroy clarion" ]] || die "cancelled"
  fi

  say "removing containers, volumes and network"
  dc down -v --remove-orphans || true
  local ids
  ids="$(project_ids containers)"; [[ -z "$ids" ]] || docker rm -f $ids >/dev/null
  ids="$(project_ids volumes)"; [[ -z "$ids" ]] || docker volume rm -f $ids >/dev/null
  ids="$(project_ids networks)"; [[ -z "$ids" ]] || docker network rm $ids >/dev/null
  docker rmi clarion-api:local clarion-web:local >/dev/null 2>&1 || true
  if [[ "$purge_images" == 1 ]]; then
    say "removing pulled base images that nothing else uses, and the build cache"
    for img in pgvector/pgvector:pg17 redis:8-alpine nginx:alpine node:22-alpine; do
      docker rmi "$img" >/dev/null 2>&1 || true   # refused while another container uses it
    done
    docker builder prune -f >/dev/null 2>&1 || true
  fi

  caddy_remove

  if [[ "$purge_backups" == 1 ]]; then
    rm -rf "$STATE_DIR"
  else
    find "$STATE_DIR" -mindepth 1 -maxdepth 1 ! -name backups -exec rm -rf {} + 2>/dev/null || true
    rmdir "$STATE_DIR/backups" "$STATE_DIR" 2>/dev/null || true
  fi

  local left=0
  for kind in containers volumes networks; do
    [[ -z "$(project_ids "$kind")" ]] || { warn "left over $kind: $(project_ids "$kind" | tr '\n' ' ')"; left=1; }
  done
  docker image inspect clarion-api:local clarion-web:local >/dev/null 2>&1 && { warn "images still present"; left=1; }
  [[ -f "$CADDY_SNIPPET" ]] && { warn "caddy snippet still present"; left=1; }
  [[ "$left" == 0 ]] || die "some resources were not removed (see above)"
  say "clean: nothing labelled '$PROJECT' remains on this machine"
  [[ -d "$STATE_DIR/backups" ]] && echo "backups were kept in $STATE_DIR/backups (use --purge-backups to delete them)"
  echo "Remember to delete the proxied DNS record for the hostname in Cloudflare."
}

# ------------------------------------------------------------------ main
cmd="${1:-}"; shift || true
case "$cmd" in
  init) cmd_init ;;
  up | update) cmd_up "$@" ;;
  status) cmd_status ;;
  logs) cmd_logs "$@" ;;
  backup) cmd_backup ;;
  telegram-webhook) cmd_telegram_webhook ;;
  sms-webhook) cmd_sms_webhook ;;
  down) cmd_down ;;
  destroy) cmd_destroy "$@" ;;
  -h | --help | help | "") usage 0 ;;
  *) warn "unknown command: $cmd"; usage 1 ;;
esac
