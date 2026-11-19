# 0009. Public voice notes, made on first use

- Status: proposed
- Date: 2026-11-19
- Deciders: Emmanuel Lafenwa

## Context

The mission is the time and language distance between a rumour and its correction. Many voters cannot read comfortably in English, Yoruba, Hausa, Igbo or Pidgin, or have little data. Voice notes already exist, but only a reviewer can render them (`POST /messages/{id}/renditions`, which calls the speech service every time), so the public correction page cannot play them. A new public endpoint changes the public API and spends money on a paid speech service, so it needs a decision.

## Options considered

1. **List the voice note URLs in the public correction.** The page would need to know which files exist. That needs a table to remember them (a new migration, repository and wiring), and files would only exist once a reviewer had prepared them.
2. **Reuse the reviewer endpoint for the public.** It is signed-in only and regenerates audio on every call, so opening it up would let anyone run up the speech bill.
3. **A public endpoint that makes each voice note once and keeps it.** `GET /public/corrections/{id}/voice/{language}` checks the object store for a fixed key, makes the audio only if it is missing, and redirects to the file.

## Decision

Option 3. The endpoint only serves a correction that is approved and sealed, and only in a language that has approved text (English is the summary). A sealed message never changes, so one stored file per language is always right. The speech service is therefore called at most once for each message and language, which bounds the cost by the number of sealed corrections times five, whatever the traffic. Reviewer renditions use the same fixed key, so audio a reviewer already prepared is reused, not paid for twice. The object store gains `exists` and `public_url`. Failures from the speech service return a 503 with a plain message, and the page shows that audio is not available right now.

## Consequences

- Voters can press Listen on the public page in every approved language, with no sign in and no change to the public record or its fingerprint.
- No new table. The files themselves are the cache. An S3 store answers `exists` with one signed HEAD request each time someone presses Listen, not on every page view.
- The first listener in a language waits for the speech call. A reviewer who presses Prepare voice notes before sending removes that wait.
- If audio is ever wrong, delete the file under `renditions/<message id>/` and the next request makes it again.
- Speech still has no budget guard (see ADR 0007). The once-per-language bound is the only limit, so watch the Spitch dashboard during pilots.
