# AGENTS.md (worker)

- Jobs take ids, not objects, load fresh state, and are safe to run twice.
- Task names are `noun.verb` strings set explicitly (`deliveries.send`); never rely on function names.
- A job that sends to people must check the delivery is still `queued` before sending.
