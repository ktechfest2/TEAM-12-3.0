# T-12. Telegram intake and JOIN subscriptions

- Owner: claude
- Depends on: T-04
- Estimate: M

## Goal

People send a claim or JOIN YORUBA to the bot and get answers and future corrections.

## Context

`adapters/channels/telegram.py`; subscribers table.

## Acceptance criteria

- [x] Webhook route receives updates; claims go through the same intake as the web
- [x] JOIN <language> stores a hashed subscriber with consent time; STOP removes it
- [x] Replies use approved text only
- [x] `make verify` passes

## Files likely touched

api/routes/telegram.py, adapters/channels/telegram.py

## Questions

- Delivering future corrections to subscribers is not part of this task. The table stores only a hash of the chat id (by design), so the bot cannot message a subscriber later. Doing that needs an ADR for an encrypted or reversible address column. Chosen reading: JOIN and STOP store and remove consent; nothing is sent to subscribers yet.
- A claim sent to the bot gets a fixed acknowledgement only, never the draft verdict, because drafts are not reviewed. A draft message is queued for reviewers.
- New setting `CHANNEL_TELEGRAM_WEBHOOK_SECRET` (the secret token given to Telegram setWebhook); add it to `.env.example` by hand. The webhook refuses all calls while it is unset.
