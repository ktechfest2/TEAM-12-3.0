# T-10. LLM budget guard

- Owner: claude
- Depends on: T-01
- Estimate: S

## Goal

Model calls stop before spend passes `LLM_MONTHLY_BUDGET_USD`.

## Context

`adapters/llm/`.

## Acceptance criteria

- [x] A wrapper counts tokens or calls per month in Redis and raises a clear error past the cap
- [x] Unit test with the fake model
- [x] `make verify` passes

## Files likely touched

adapters/llm/

## Questions

- Cost is estimated from text length (4 characters per token) because the model protocol returns no usage. Rate is the new setting `LLM_USD_PER_MILLION_TOKENS` (default 1.0); add it to `.env.example` (the agent cannot edit that file).
