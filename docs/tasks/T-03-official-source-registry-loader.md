# T-03. Official source registry loader

- Owner: claude
- Depends on: T-02
- Estimate: S

## Goal

Reviewers can load official passages so claims match real INEC statements.

## Context

ADR 0003; `data/seed_sources.json`.

## Acceptance criteria

- [x] `make -C apps/api seed-sources` loads a JSON file of passages with embeddings into the active repository
- [x] Duplicate URLs plus text are skipped
- [ ] Seed passages replaced with direct INEC wording where available and each URL checked by a person
- [x] `make verify` passes

## Files likely touched

apps/api/scripts/, data/, Makefile

## Questions

- Duplicates are detected by URL plus text together (same URL with different text is a different passage). Criterion 3 (replace seed passages with direct INEC wording, each URL checked by a person) needs a human and is left unticked.
