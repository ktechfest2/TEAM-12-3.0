# T-05. S3 compatible object store adapter

- Owner: claude
- Depends on: T-01
- Estimate: S

## Goal

Media files go to Supabase Storage, or any S3 store, through one adapter.

## Context

ADR 0002; `adapters/storage/`.

## Acceptance criteria

- [ ] `adapters/storage/s3.py` uses the S3 protocol (add a small S3 client dependency and credit it)
- [ ] Factory selects it when `STORAGE_PROVIDER=s3`
- [ ] Unit test with a fake transport; no network in tests
- [ ] `make verify` passes

## Files likely touched

adapters/storage/, pyproject.toml, docs/CREDITS.md

## Questions
