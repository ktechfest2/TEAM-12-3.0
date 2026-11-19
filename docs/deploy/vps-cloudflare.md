# Set up the server and Cloudflare

## What the server needs

- Linux with Docker and Docker Compose v2 (arm64 or amd64), `curl` and `openssl`.
- Caddy running as a system service on ports 80 and 443 (the script adds one site to it). Without Caddy or passwordless `sudo`, the script prints the exact commands to run by hand.
- Your user in the `docker` group.
- About 1 GB of free disk for images, plus room for data.

The script never opens ports and never touches other containers. It only creates things labelled with the compose project `clarion`.

## 1. First deploy

```bash
# from the repository root on your laptop
infra/deploy/clarion.sh --host <ssh-host> init
```

This creates `~/.clarion-deploy/deploy.env` on the server. Edit it there (the comments explain each line):

```bash
ssh <ssh-host> nano ~/.clarion-deploy/deploy.env
```

Set at least `DOMAIN` (for example `clarion.example.org`) and `AUTH_REVIEWER_INVITE_CODE` (a long random value). Leave `LLM_PROVIDER=fake` to run offline with placeholder answers, or set it to `gemini` with the key and model names for real ones.

```bash
infra/deploy/clarion.sh --host <ssh-host> up
```

`up` checks the settings, generates secrets, builds the images on the server (the first build takes a few minutes), starts everything, adds the Caddy site, and ends by checking `/api/health`. Run it again any time; it is safe to repeat.

Use `up --no-caddy` if you would rather add the Caddy site yourself; the script then prints what to add.

## 2. Cloudflare

In the Cloudflare dashboard for your domain:

1. **DNS:** add an `A` record for the hostname pointing at the server's public IP, with the proxy turned on (orange cloud). If a record for that name already exists (for example, one pointing at another host), change it rather than adding a second.
2. **SSL/TLS:** set the mode to **Full (strict)**. Caddy gets a normal Let's Encrypt certificate for the hostname, which Cloudflare accepts in this mode. Do not use Flexible: it causes redirect loops.
3. **Bot protection:** if you use Telegram, add a WAF custom rule that **skips** Bot Fight Mode and security checks for requests whose path is `/api/webhooks/telegram`. Telegram's servers are otherwise sometimes challenged and the bot goes silent.
4. Leave caching at its defaults. The API sends no cache headers, and the live board relies on a stream that Cloudflare passes through (the API pings every 15 seconds, well inside Cloudflare's idle limit).

The first request after DNS changes can take a minute while Caddy obtains its certificate. Check from anywhere:

```bash
curl https://<your hostname>/api/health
```

## 3. Telegram (optional)

Set `CHANNEL_TELEGRAM_BOT_TOKEN` and `CHANNEL_TELEGRAM_CHAT_ID` in `deploy.env` (create the bot with BotFather, make a channel, add the bot as admin), run `up` again, then register the webhook:

```bash
infra/deploy/clarion.sh --host <ssh-host> telegram-webhook
```

This points Telegram at `https://<hostname>/api/webhooks/telegram` with the generated secret token.

## 4. Sign in and try it

Open `https://<hostname>/review` and sign in with your name and the invite code. Submit a claim on the home page, then review it. The reviewer screen, broadcast board and public correction pages all work under the same hostname.

## Safe test without DNS

To try the whole stack before touching DNS, set `DOMAIN=clarion.localhost`. Caddy serves that name with its own local certificate, so no Let's Encrypt request is made. On the server: `curl -k --resolve clarion.localhost:443:127.0.0.1 https://clarion.localhost/api/health`. Change `DOMAIN` and run `up` again when you are ready.
