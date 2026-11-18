# 0004. Pin TypeScript 5.9 while TypeScript 7 lacks a JS compiler API

- Status: accepted
- Date: 2026-11-19

## Context

TypeScript 7.0.2 (the native compiler) is the npm `latest` tag. `openapi-typescript` 7.13.0 builds types through the JavaScript compiler API, which TypeScript 7 does not expose; generation crashes. Its peer dependency is `typescript ^5.x`.

## Decision

Pin `typescript@5.9.3` in `apps/web`. Revisit when `openapi-typescript` supports TypeScript 7.

## Consequences

Type checking uses the 5.9 compiler. Do not upgrade TypeScript without running `make contract` and `make verify`.
