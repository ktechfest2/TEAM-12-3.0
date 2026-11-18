# AGENTS.md (tests)

- Test behaviour, named as a sentence: `test_unreviewed_message_is_blocked`.
- Use `factories.py`; do not hand build large objects in each test.
- No network, no real keys, no real phone numbers. Fakes only outside `integration/`.
- `unit/test_rules.py` guards real people from unreviewed messages. Never delete or weaken these tests.
