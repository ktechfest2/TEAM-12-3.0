# 0010. Claims and commands by text message, on a SIM that also carries personal texts

- Status: accepted
- Date: 2026-11-20
- Deciders: Team Triumph

## Context

Voters without data or a smartphone cannot reach the Telegram bot or the web form. Basic phones can still send a text, so letting people text a claim to a phone number reaches the people the correction gap hurts most. It also lets people send `STOP` by text, which ADR 0008 could not offer ("inbound replies are not wired up").

The SMS gateway (TextBee) is an Android phone holding the owner's **personal SIM**. When "Receive SMS" is on, the gateway forwards *every* text that phone receives: messages from family, banks, the network operator and one-time passwords included. Clarion must tell election texts apart from personal ones without a person in the loop, and must never store, log, answer or show a reviewer anything personal.

Other forces:

- Every reply is a text the owner pays for and counts against the gateway's daily limit. Anyone who learns the number can flood it.
- Gateways resend a webhook when they do not get a 2xx, so the same text can arrive more than once.
- The sender's number is personal data (architecture section 9, ADR 0008).
- Replies in Yoruba, Igbo or Hausa letters switch to UCS-2, which fits 70 characters per text instead of 160.
- One Android phone is a single point of failure, and a network operator may flag it as spam if it sends too much.

## Options considered

1. **Treat every incoming text as a claim.** Simplest, but personal texts would be stored as claims, shown to reviewers and answered. Rejected.
2. **Use a language model to decide whether a text is about elections.** Personal content would still be sent to an outside model and stored for review, and the decision is not predictable. Rejected.
3. **Accept only texts from an allow list of numbers.** Safe, but it closes the door on the voters this feature is for. Rejected.
4. **A keyword gate.** A text is Clarion's only if its first word is `CLARION`. A bare `STOP` counts only from a number that already has a Clarion subscription. Senders that are not phone numbers (bank or operator names, short codes) are never Clarion's. Everything else is dropped on arrival: not stored, not logged, not answered. Predictable, cheap, and the keyword is printed on every poster and reply. The cost is that people must remember the word.
5. **A second SIM or a paid short code for Clarion only.** Best in the long run, but it costs money and paperwork we do not have for the demo. It stays the production path; the adapter boundary (ADR 0002) means only the adapter changes.

Common words such as `CHECK` or `JOIN` alone were also considered as the gate and rejected, because friends send texts like "check this out" or "join us".

## Decision

Take option 4, behind a vendor neutral boundary.

- **Webhook.** `POST /webhooks/sms` reads the raw body through an `InboundSmsReader` adapter. The TextBee reader checks the `X-Textbee-Signature` HMAC-SHA256 over `"<t>.<raw body>"` with our signing secret (`CHANNEL_SMS_WEBHOOK_SECRET`) and refuses timestamps older than 5 minutes. It accepts only `MESSAGE_RECEIVED` events, and only from our gateway device when `CHANNEL_SMS_DEVICE_ID` is set. With no secret set, the route answers 401 and nothing is read.
- **The gate, in this order.** (1) The sender must normalise to an international phone number. (2) The first word must be `CLARION`, in any letter case and with trailing punctuation allowed. The exception is a bare `STOP` from a number that already has a subscription. (3) Anything else returns 200 and is forgotten. Its text, sender and id are not kept, and the log records only that a message was ignored.
- **Commands after `CLARION`.** `CLARION <claim>` stores a claim and queues a draft for reviewers. `CLARION JOIN <language>` subscribes. `CLARION STOP` (or bare `STOP` from a subscriber) unsubscribes. `CLARION` alone gets a help text. Replies are fixed, human-written text only. No draft and no model output is ever sent back (ADR 0003 is unchanged).
- **Consent by text.** Texting `CLARION JOIN YORUBA` from a number proves control of it, just as entering a code does. The subscription becomes active with `consented_at` set, stored encrypted as in ADR 0008, with the default limits (instant, 3 a day). `STOP` deletes the subscription and the encrypted number.
- **Privacy.** A claim never stores the sender. The number is used in memory to reply, and is kept (encrypted) only if the person joins. Logs never hold a number or message text.
- **Cost and abuse.** Each texted message id is handled once (an in-memory set; the API runs as one process, the same reasoning as the code limiter in ADR 0008). Each number may send 5 messages an hour that Clarion acts on, and gets at most 3 replies an hour. All numbers together get at most 100 replies a day. Over a limit, Clarion stays silent instead of replying, so a flood cannot use up the owner's credit.
- **Short replies.** Every SMS reply is plain ASCII and fits one 160-character text; a test enforces it.
- **Language.** A claim is tagged with the sender's first subscribed language when they have a subscription, otherwise English. Reviewers can still read any language.

## Consequences

- Easier: basic phone users can send claims, join and leave by text; `STOP` works in the way people expect.
- Harder: people must start with `CLARION`. Posters, replies and the public page must say so. A personal text that happens to start with "Clarion" would be taken as a claim; that is unlikely, and a reviewer still sees it before anything is published.
- Personal texts still pass through TextBee's cloud, because the phone forwards them before Clarion can filter. The owner accepts that by switching on Receive SMS; a dedicated SIM removes it.
- Rate limits and the duplicate set live in one process and reset on restart. That is fine for one API process, but they must move to Redis if the API ever runs more than one.
- Requires: `CHANNEL_SMS_WEBHOOK_SECRET` in the deploy env, a TextBee webhook subscription for `MESSAGE_RECEIVED` pointing at `https://<api host>/webhooks/sms`, and Receive SMS switched on in the app.
- Follow-up, not in this change: text the approved answer back to the person who asked. That needs a stored, encrypted link from the claim to the number and must go through the approved broadcast path.
