# T-12. Telegram intake and JOIN subscriptions

- Owner: claude
- Depends on: T-04
- Estimate: M

## Goal

People send a claim or JOIN YORUBA to the bot and get answers and future corrections.

## Context

`adapters/channels/telegram.py`; subscribers table.

## Acceptance criteria

- [ ] Webhook route receives updates; claims go through the same intake as the web
- [ ] JOIN <language> stores a hashed subscriber with consent time; STOP removes it
- [ ] Replies use approved text only
- [ ] `make verify` passes

## Files likely touched

api/routes/telegram.py, adapters/channels/telegram.py

## Questions
