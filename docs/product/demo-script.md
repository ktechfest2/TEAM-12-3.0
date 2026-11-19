# Demo script (3 minutes)

One idea to land: **a correction can reach the voter's phone, in their language, minutes after a person approves it, with the official source one scan away.**

## Before you go on

Run these once, about ten minutes before. Use a copy of the database you can wipe.

| Step | Command or action |
| --- | --- |
| Services | `make services-up` then `make db-migrate` |
| Settings | In `.env`: `REPOSITORY_BACKEND=sql`, `AUTH_REVIEWER_INVITE_CODE=<pick one>`, `AUTH_JWT_SECRET=<private value>`. For a live Telegram channel also set `CHANNEL_TELEGRAM_BOT_TOKEN` and `CHANNEL_TELEGRAM_CHAT_ID` to a test chat you own |
| Known data | `make demo-reset CONFIRM=1` (wipes claims, messages, reviews, deliveries and subscribers; keeps the official sources; queues two drafts) |
| Start | `make dev`, open the web app, and open the public page in a second tab later |
| Check | Open **Review queue**, sign in, confirm two claims are waiting. Open **Broadcast board** and confirm it says no approved corrections yet |

`make demo-reset` refuses to run when `APP_ENV=production`, when `REPOSITORY_BACKEND` is not `sql`, or without `CONFIRM=1`.

## The three claims (use these exact words)

| When | Claim | Verdict you will show |
| --- | --- | --- |
| Queued by the reset | INEC has released a new 2027 campaign timetable graphic | Contradicted by an official source |
| Queued by the reset | The presidential election is scheduled for 16 January 2027 | Confirmed by an official source |
| Typed live | Nigerians abroad can cast ballots through a mobile phone app | No official statement found yet |

The offline model gives these exact verdicts (a test pins them). A real language model may word the summary differently but should reach the same verdicts; run the three once with your real keys before you present.

## Run of show

| Time | Screen | Say | Do |
| --- | --- | --- | --- |
| 0:00 to 0:20 | Slide or **Check a claim** | "The rumour speaks Yoruba. The correction speaks English. Clarion closes that gap." | Paste the timetable claim into **Check a claim** and press **Check it** |
| 0:20 to 0:40 | Verdict card | "It finds what INEC actually said and shows the source. It never calls anything true or false; it says what the official source says." | Point at the verdict words and the source link |
| 0:40 to 1:25 | **Review queue** | "Nothing goes out without a person. The reviewer sees the draft beside the official passage." | Sign in. Open the timetable claim. Draft each of the four translations, approve each one ("a native speaker approves these"). Approve. Press **Seal this message** |
| 1:25 to 2:00 | **Broadcast board** | "One tap sends it to every channel." | Press **Send to every channel** on the review screen, switch to **Broadcast board**. Point at tiles turning green and the timer |
| 2:00 to 2:25 | Public correction page | "Anyone can check it was not changed after approval." | Open the page for this message (`/c/<message id>`, also the QR on the card). Show approver, time, fingerprint and **How to check it yourself** |
| 2:25 to 2:50 | **Check a claim** | "And when there is no official statement, we say so instead of guessing." | Type the live claim. Show **No official statement found yet** |
| 2:50 to 3:00 | Slide | "Minutes from approval to every channel, in the voter's language, with the source attached." | Stop |

## What is real in this build, and what is not

Say only what you can show.

- **Real:** matching to official passages, the review and translation approval steps, sealing, sending to Telegram (if configured), the live board, the public page and its fingerprint check, SMS text sizing, the social card, poster and QR code.
- **Placeholder:** with `LLM_PROVIDER=fake` the "translations" are the English text with a language tag, so show the approval step but do not read them out. With real keys (`LLM_PROVIDER=gemini`) they are model drafts that must be approved by native speakers.
- **Voice notes:** with `SPEECH_PROVIDER=spitch` they are real Yoruba, Hausa and Igbo voices; Pidgin is read by an English voice until a Pidgin voice is confirmed, so say so if you play it. With `SPEECH_PROVIDER=fake` the stored file does not play; do not open it on screen.
- **Not built yet:** SMS, WhatsApp, X and Instagram sending (T-14), sending future corrections to JOIN subscribers. Do not say the board reaches those channels. With no Telegram keys the board shows a single test channel called "Console (test)".
- **Seed sources** paraphrase INEC statements as reported by news and fact checking outlets. A person must check each against the original before a public demo.

## If something goes wrong

| Problem | Do this |
| --- | --- |
| Model call fails or is slow | Set `LLM_PROVIDER=fake` and restart; the script's verdicts are the same. Say it is the offline mode |
| Telegram does not deliver | The board shows the tile as failed. Say so, and show the Console (test) channel or the recorded video |
| Board stays empty | Press **Send to every channel** again only if the review screen shows "Sealed". Check the API log for `delivery.send.finished` |
| You need a clean start | `make demo-reset CONFIRM=1`, then reload the page |

## Recording the backup video

Record the run of show above once, under three minutes, after a clean `make demo-reset CONFIRM=1`. Show the board with the timer visible. Save it outside the repository (it is large) and put the link in `docs/product/README.md`.
