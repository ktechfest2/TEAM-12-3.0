# T-10. LLM budget guard

- Owner:
- Depends on: T-01
- Estimate: S

## Goal

Model calls stop before spend passes `LLM_MONTHLY_BUDGET_USD`.

## Context

`adapters/llm/`.

## Acceptance criteria

- [ ] A wrapper counts tokens or calls per month in Redis and raises a clear error past the cap
- [ ] Unit test with the fake model
- [ ] `make verify` passes

## Files likely touched

adapters/llm/

## Questions

