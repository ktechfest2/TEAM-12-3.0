# 0001. Record architecture decisions

- Status: accepted
- Date: 2026-11-19

## Context

Four people and several coding agents will change this codebase in parallel under a 48 hour deadline. Decisions made in chat get lost and agents repeat old debates.

## Decision

Any change that crosses a boundary in `TECHNICAL_ARCHITECTURE.md`, adds a dependency, or changes a public API or table gets a short ADR in `docs/adr/`, copied from `0000-template.md`.

## Consequences

A few minutes per decision. Agents can read why things are the way they are before changing them.
