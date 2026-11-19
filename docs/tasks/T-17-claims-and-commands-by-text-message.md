# T-17. Claims and commands by text message

- Owner: claude
- Depends on: T-12, phone subscriptions (ADR 0008)
- Estimate: M (2 to 5h)

## Goal

A person with any phone can text `CLARION <claim>`, `CLARION JOIN <language>` or `STOP` to the Clarion number. The gateway SIM's personal texts are never stored, logged or answered.

## Context

ADR 0010, ADR 0008, `services/chat_bot.py` (the Telegram version of the same commands), `adapters/channels/textbee.py`.

## Acceptance criteria

- [x] `POST /webhooks/sms` refuses requests with a missing, wrong or older than 5 minute signature, and refuses everything when `CHANNEL_SMS_WEBHOOK_SECRET` is unset (`tests/api/test_sms_webhook.py`).
- [x] Texts without the `CLARION` keyword, a bare `STOP` from a non-subscriber, and texts from names such as banks or network operators are not stored, not remembered and not answered (`test_personal_texts_are_not_stored_or_answered`).
- [x] `CLARION <claim>` stores a claim with `submitted_via=sms` and no sender, queues a draft for reviewers and replies with fixed text only.
- [x] `CLARION JOIN <language>` makes an active, encrypted subscription with a consent time; `STOP` deletes it.
- [x] A retried delivery is handled once; one number gets at most 5 handled texts and 3 replies an hour; all numbers together at most 100 replies a day.
- [x] Every reply fits in one plain (GSM-7) text (`tests/unit/test_sms_inbox.py`).
- [ ] TextBee webhook created for `MESSAGE_RECEIVED` and Receive SMS switched on in the app (needs the SIM owner).
- [x] `make verify` passes.

## Files likely touched

`api/routes/webhooks.py`, `services/sms_inbox.py`, `adapters/channels/textbee_inbound.py`, `adapters/channels/base.py`, `api/container.py`, `config.py`, `infra/deploy/deploy.env.example`, `docs/TECHNICAL_ARCHITECTURE.md`.

## Setup for the SIM owner

1. In the TextBee app: Settings, SMS, switch on **Receive SMS**.
2. Make a secret: `openssl rand -hex 32`. Put it in the server's deploy env as `CHANNEL_SMS_WEBHOOK_SECRET`. Also set `CHANNEL_SMS_DEVICE_ID`, so only your gateway phone is accepted.
3. In the TextBee dashboard: Webhooks, Add Webhook. Use the URL `https://<api host>/webhooks/sms`, the event `MESSAGE_RECEIVED`, and the same secret.
4. Text `CLARION` from another phone; you should get the help text back.

## Questions

- Should the approved answer be texted back to the person who sent the claim? Picked: not in this task. It needs a stored, encrypted link from the claim to the number, and must go through the approved broadcast path (ADR 0010, follow-up).
