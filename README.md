<p align="center">
  <img src="apps/web/public/logo.svg" alt="Clarion" width="96">
</p>

<h1 align="center">Clarion</h1>

<p align="center">
  <strong>The rumour was corrected. The people who believed it never heard. Clarion carries the correction the rest of the way.</strong>
</p>

<p align="center">
  <a href="#what-clarion-does">What it does</a> ·
  <a href="#run-it-on-your-laptop">Run it locally</a> ·
  <a href="docs/product/demo-script.md">Demo script</a> ·
  <a href="docs/TECHNICAL_ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/deploy/README.md">Deploy</a>
</p>

---

## The problem

A few weeks before an election, a voice note lands in a family WhatsApp group: *the election has been moved*. By evening it has crossed hundreds of groups. By the weekend it is being repeated at the market, at the bus stop and after church.

On Tuesday, INEC says it isn't true. The statement goes up on its website and its social accounts, in English.

On paper, the rumour has been dealt with. In practice it is still spreading. It keeps moving on social media, and it moves even faster among people who will never see that statement: people who don't follow the news, who don't read English, or who don't read at all. Someone's mother hears it from a neighbour she trusts, in Yoruba, and decides there's no rush to collect her voter's card.

The correction exists. It just never reaches the people who need it. We call that distance the **correction gap**. Clarion exists to close it.

## What Clarion does

### 1. You ask from wherever you saw it

You shouldn't have to leave the conversation, find the right website and search through press releases. Send the message you received to Clarion on the channel you already use, and it checks it against what the election authority has actually said.

| Where you are | Ask Clarion | Get corrections |
| --- | --- | --- |
| Web | ✅ Paste it on the homepage | ✅ Public correction pages |
| Telegram | ✅ Message the bot | ✅ Send `JOIN YORUBA` (or Hausa, Igbo, Pidgin, English) |
| SMS | ✅ Text `CLARION` followed by the claim | ✅ Text `CLARION JOIN YORUBA`, or sign up on the web with a code we text you |
| X | Planned (reply or mention) | ✅ Posted from the Clarion account |
| WhatsApp, Instagram | Planned | Planned |

**Is your platform missing?** [Open an issue](https://github.com/ktechfest2/TEAM-12-3.0/issues) and tell us where the rumours in your community spread. Each channel is a small, self-contained adapter, so adding one doesn't touch the rest of the system. See [how adapters work](apps/api/src/clarion_api/adapters/README.md).

### 2. You get an answer you can check

Clarion compares the claim with a library of official statements and gives one of three answers:

- **Confirmed**: an official statement says the same thing.
- **Contradicted**: an official statement says otherwise.
- **No official statement yet**: there is nothing official to compare it with.

Clarion never calls anything "true", "false" or "misleading", and it never gives an opinion. Every answer quotes the official passage it is based on, so you can read the source yourself.

### 3. A person approves every message before it goes out

A language model drafts the correction and the translations. It never sends anything itself. A reviewer reads the draft next to the source, checks each language, listens to the voice notes and approves the message. The system won't send anything until that has happened, and our tests check that.

Each approved message is sealed with a fingerprint. Anyone can open its public page and confirm that it wasn't changed after it was approved.

### 4. The correction travels the way the rumour did

A rumour spreads through voice notes, forwarded texts and conversation, in the languages people speak at home. A correction that only exists as an English web page can't follow it there. From one approved message, Clarion makes:

- **Voice notes** in Yoruba, Hausa, Igbo, Pidgin and English, for people who listen instead of read.
- **Short texts** that fit in an SMS and work on basic phones with no data.
- **A radio spot** that a local station can play.
- **A printable poster** with a QR code, for noticeboards, churches, mosques and market stalls.
- **A social card** that is easy to share in groups.

They all link back to the same public page, so the correction someone hears at the market can be traced to the official source.

## Where things stand

We built this in a hackathon, so here's an honest picture.

- **Working today:** checking claims on the web, on Telegram and by SMS, the three answers with their quoted sources, review and translation approval, sealing, the live broadcast board, public pages with listen buttons, voice notes, SMS text, social cards, posters and QR codes. Corrections can go out on Telegram, on X, and by SMS to subscribers who have confirmed their number. Voice notes in Yoruba, Hausa and Igbo use real Nigerian voices.
- **Not yet:** asking Clarion on X, and WhatsApp and Instagram in both directions. When you send a claim by Telegram or SMS, Clarion confirms that it received it, and the answer reaches you after review if you have joined. A direct reply is planned. Pidgin voice notes currently use an English voice.
- **Needs a person before real use:** the seed sources paraphrase INEC statements as reported in the news. Each one should be checked against the original before anyone relies on it.

---

## For developers

### Run it on your laptop

You'll need Python 3.13 with [uv](https://docs.astral.sh/uv/), Node 22 with pnpm 10, and Docker.

```bash
cp .env.example .env    # no keys needed to try it out
make setup              # installs dependencies and git hooks
make services-up        # starts Postgres (with pgvector) and Redis
make db-migrate
make dev                # API on :8000, web app on :5173
```

You don't need any API keys to start. With `APP_ENV=test`, every outside service (the language model, speech and channels) is replaced with an offline stand-in, so the whole flow runs on your machine. Add your keys to `.env` when you want real translations, voices and delivery.

To see the whole flow, follow the [three-minute demo script](docs/product/demo-script.md). `make demo-reset CONFIRM=1` gives you a clean database with two claims waiting for review.

### How it's put together

```text
 claim ──▶ match against official sources ──▶ draft + translations ──▶ human review ──▶ seal ──▶ channels
 (web, Telegram, SMS)  (three answers)          (language model)        (required)     (fingerprint)
```

- **`apps/api`**: a FastAPI service plus a background worker that does the matching, drafting, rendering and sending.
- **`apps/web`**: a React app with the claim checker, the reviewer queue, the broadcast board and the public correction pages.
- **`contracts`**: the OpenAPI spec both apps share. The web app's types are generated from it.
- **`infra`**: local Docker services and the deployment scripts.

The core logic never imports a vendor SDK. Language models, speech engines, storage and delivery channels each sit behind a small adapter in `apps/api/src/clarion_api/adapters/`. To add a channel, you write one adapter that can send text (and, optionally, receive messages), register it, and the review and sealing rules apply to it automatically. The [architecture doc](docs/TECHNICAL_ARCHITECTURE.md) and the [decision records](docs/adr/) explain why things are built this way.

### Deploying

The simplest option is a single VPS behind Cloudflare. One script sets up the whole stack, and one command removes all of it again, stored media included:

```bash
infra/deploy/clarion.sh --host <ssh-host> init
infra/deploy/clarion.sh --host <ssh-host> up
```

You provide the hostname, a reviewer invite code, a language model and your channel settings. Database passwords and signing secrets are generated for you. The [deploy guide](docs/deploy/README.md) walks through it, and [infra/README.md](infra/README.md) covers the managed route on Render, Vercel and Supabase instead.

### Contributing

Before you open a PR, run:

```bash
make verify
```

It runs the same formatting, lint, type checks, tests and contract check as CI, for both apps. Open work lives on the [task board](docs/tasks/BOARD.md). [AGENTS.md](AGENTS.md) explains how we pick up tasks and the rules we don't bend, such as human approval before anything is sent. [CONVENTIONS.md](docs/CONVENTIONS.md) covers code style.

## Credits

Built by **Team Triumph** for KTech Fest 3.0, *"Every Vote, Every Voice"*. Everything in this repository was written during the hackathon. The libraries, models, services and AI coding assistants we used are listed in [docs/CREDITS.md](docs/CREDITS.md).
