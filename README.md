<p align="center">
  <img src="apps/web/public/logo.svg" alt="Clarion" width="96">
</p>

<h1 align="center">Clarion</h1>

<p align="center">
  <strong>The rumour speaks Yoruba. The correction speaks English. Clarion closes that gap.</strong>
</p>

<p align="center">
  <a href="#run-it-on-your-laptop">Run it locally</a> ·
  <a href="docs/product/demo-script.md">Demo script</a> ·
  <a href="docs/TECHNICAL_ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/deploy/README.md">Deploy</a>
</p>

---

A few weeks before an election, a voice note lands in a family WhatsApp group: *the election has been moved*. By evening it has crossed hundreds of groups. Someone's mother hears it from a neighbour she trusts, in Yoruba, and decides there's no rush to collect her voter's card.

INEC usually does respond to rumours like this. The trouble is that the response is an English press statement on a website most voters never visit. We call the distance between those two things the **correction gap**, and Clarion is our attempt to close it.

## What it does

1. **Someone reports a claim.** A citizen, a journalist or an election desk pastes in what they heard.
2. **Clarion finds what INEC actually said.** It matches the claim against a library of official statements and returns one of three answers: *confirmed*, *contradicted*, or *no official statement yet*. It never says "true" or "false", and every answer quotes the official passage it relied on.
3. **A person approves it.** A reviewer sees the draft next to the source, checks each translation, and seals the message. Nothing goes out without this step. The code won't allow it.
4. **One tap sends it everywhere.** Text, voice notes in Yoruba, Hausa, Igbo and Pidgin, a social card, a radio spot and a printable poster with a QR code. Each one links to a public page where anyone can check that the message wasn't changed after it was approved.

## Where things stand

We built this in a hackathon, so here's an honest picture:

- **Working today:** claim matching, the three verdicts, the review and translation approval flow, sealing, Telegram delivery, the live broadcast board, public verification pages, SMS sizing, social cards, posters and QR codes. Voice notes in Yoruba, Hausa and Igbo use real Nigerian voices.
- **Not yet:** sending over SMS, WhatsApp, X and Instagram, and pushing corrections to people who've subscribed. Pidgin voice notes currently use an English voice.
- **Needs a human before real use:** the seed sources paraphrase INEC statements as reported in the news. Each one should be checked against the original.

## Run it on your laptop

You'll need Python 3.13 with [uv](https://docs.astral.sh/uv/), Node 22 with pnpm 10, and Docker.

```bash
cp .env.example .env    # no keys needed to try it out
make setup              # installs dependencies and git hooks
make services-up        # starts Postgres (with pgvector) and Redis
make db-migrate
make dev                # API on :8000, web app on :5173
```

You don't need any API keys to get started. With `APP_ENV=test`, every outside service (the language model, speech, channels) is swapped for an offline stand-in, so the full flow runs on your machine. When you want real translations and voices, add your keys to `.env`.

To see the whole thing end to end, follow the [three-minute demo script](docs/product/demo-script.md). `make demo-reset CONFIRM=1` gives you a clean database with two claims already waiting for review.

## How it's put together

- **`apps/api`**: a FastAPI service plus a background worker that does the matching, drafting, rendering and sending.
- **`apps/web`**: a React app with the claim checker, the reviewer queue, the broadcast board and the public correction pages.
- **`contracts`**: the OpenAPI spec both apps share. The web app's types are generated from it.
- **`infra`**: local Docker services and the deployment scripts.

Language models, speech engines and delivery channels all sit behind small adapters, so swapping one provider for another doesn't touch the core logic. The [architecture doc](docs/TECHNICAL_ARCHITECTURE.md) and the [decision records](docs/adr/) explain why things are the way they are.

## Deploying

The simplest option is a single VPS behind Cloudflare. One script sets up the whole stack, and one command tears it all down again, stored media included:

```bash
infra/deploy/clarion.sh --host <ssh-host> init
infra/deploy/clarion.sh --host <ssh-host> up
```

You only provide the hostname, a reviewer invite code, a language model and your channel settings. Database passwords and signing secrets are generated for you. The [deploy guide](docs/deploy/README.md) walks through it, and [infra/README.md](infra/README.md) covers the managed route on Render, Vercel and Supabase instead.

## Contributing

Before you open a PR, run:

```bash
make verify
```

It runs the same lint, type checks, tests and contract check as CI, for both apps. Open work lives on the [task board](docs/tasks/BOARD.md). [AGENTS.md](AGENTS.md) explains how we pick up tasks and what we won't compromise on (human approval before anything is sent, for one), and [CONVENTIONS.md](docs/CONVENTIONS.md) covers code style.

## Credits

Built by **Team Triumph** for KTech Fest 3.0, *"Every Vote, Every Voice"*. Everything in this repository was written during the hackathon. The libraries, models and AI coding assistants we used are listed in [docs/CREDITS.md](docs/CREDITS.md).
