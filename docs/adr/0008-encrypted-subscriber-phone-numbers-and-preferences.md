# 0008. Encrypted subscriber phone numbers, SMS code verification and delivery preferences

- Status: accepted
- Date: 2026-11-19
- Deciders: Team Triumph

## Context

A public subscribe page lets people give a phone number and choose what they receive, how often, and a daily maximum. Two existing rules get in the way:

- `docs/TECHNICAL_ARCHITECTURE.md` (section 9) says subscriber addresses are stored only as a keyed hash. A hash cannot be reversed, so Clarion could never text a subscriber later. T-14 already flags this.
- T-14 and the root rules say we never message a number that has not opted in. A form that accepts any number would let one person sign up a stranger.

Corrections also arrive when a reviewer approves one, not on a schedule, so "interval" needs a defined meaning.

## Options considered

1. **Keep hash only.** Safest for privacy, but we can never send. Rejected: it defeats the feature.
2. **Store the number in plain text.** Simplest. A database leak exposes every subscriber's phone number, which is a serious harm in an election context.
3. **Store the number encrypted, with the key outside the database.** A leaked database alone reveals no numbers. Costs one new dependency (`cryptography`, for Fernet) and a key to manage.
4. **No verification of the number.** Fastest to build, but anyone could subscribe someone else's phone.
5. **Verify with a 6 digit code sent by SMS.** Proves control of the number and doubles as the consent record. Costs one text per signup, which matters on TextBee's free daily limit.
6. **Intervals as a minimum gap between texts.** Simple, but corrections inside the gap would be dropped or held unpredictably.
7. **Intervals as instant or a digest (hourly, daily, weekly), plus a daily maximum.** Matches how people think about notification settings, and every correction is still delivered.

## Decision

Take options 3, 5 and 7.

- The phone number is stored encrypted (Fernet) in a new column. The key comes from config (`SUBSCRIBER_ENCRYPTION_KEY`) and is never stored in the database. The keyed hash stays, used for lookup, de-duplication and `STOP`. The number is decrypted only inside the SMS channel adapter at send time and is never logged.
- A subscription is created as `pending`. We text a 6 digit code that expires in 10 minutes and allows 5 attempts. It becomes `active` and `consented_at` is set only after the code is entered. Codes are stored hashed. Requests are rate limited per number and per IP.
- Each subscriber stores preferences: languages, channels (SMS first), delivery mode (`instant` or `digest` with hourly, daily or weekly frequency) and a maximum number of texts per day (default 3, hard cap 10, enforced server side). A correction that would exceed the cap is held and sent in a later text (the next day, or the next digest) instead of being dropped. Each person gets one text per correction, in the first of their chosen languages that is ready.
- Every text ends with a link to the subscribe page, where the owner can stop texts (confirmed with a code, like signing up). We do not say "Reply STOP" because inbound replies are not wired up (ADR 0010 later adds texted `STOP`). Unsubscribing deletes the encrypted number.
- This supersedes the "hash only" rule in architecture section 9 for SMS subscribers; the document is updated in the same change as the code. Nothing here changes the rule that only an approved, sealed message is ever sent.

## Consequences

- Easier: texting real, consenting subscribers, and showing a clear consent record.
- Harder: we now hold personal data. We must protect the key (set it only in the server's deploy env, never in code or fixtures), plan for key rotation, and delete numbers on unsubscribe.
- Requires: a database migration, new public endpoints (start signup, confirm code, update preferences, unsubscribe) with contract regeneration, a digest job in the worker, a web subscribe page, and an entry for `cryptography` in `docs/CREDITS.md`.
- Watch: SMS cost and TextBee limits (a verification text plus broadcasts), abuse of the code endpoint, and the digest job sending outside the daily maximum.
