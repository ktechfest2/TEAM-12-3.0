# T-03. Official source registry loader

- Owner:
- Depends on: T-02
- Estimate: S

## Goal

Reviewers can load official passages so claims match real INEC statements.

## Context

ADR 0003; `data/seed_sources.json`.

## Acceptance criteria

- [ ] `make -C apps/api seed-sources` loads a JSON file of passages with embeddings into the active repository
- [ ] Duplicate URLs plus text are skipped
- [ ] Seed passages replaced with direct INEC wording where available and each URL checked by a person
- [ ] `make verify` passes

## Files likely touched

apps/api/scripts/, data/, Makefile

## Questions

