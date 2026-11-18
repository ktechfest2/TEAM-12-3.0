# AGENTS.md (services)

- Take dependencies as arguments typed with protocols (`llm: LanguageModel`), never construct adapters here.
- Every service function has unit tests with fakes in `tests/unit/`.
- Any path that leads to a send must go through `broadcasting.plan_deliveries`, which enforces the publish rules.
- SMS text must be sized with `rendering/sms.measure`. Never strip tone marks or special letters to save space.
