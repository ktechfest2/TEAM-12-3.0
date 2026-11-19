# T-05. S3 compatible object store adapter

- Owner: claude
- Depends on: T-01
- Estimate: S

## Goal

Media files go to Supabase Storage, or any S3 store, through one adapter.

## Context

ADR 0002; `adapters/storage/`.

## Acceptance criteria

- [x] `adapters/storage/s3.py` uses the S3 protocol (add a small S3 client dependency and credit it)
- [x] Factory selects it when `STORAGE_PROVIDER=s3`
- [x] Unit test with a fake transport; no network in tests
- [x] `make verify` passes

## Files likely touched

adapters/storage/, pyproject.toml, docs/CREDITS.md

## Questions

- The task suggests adding a small S3 client dependency. Chosen reading: no new dependency. The adapter signs requests itself (AWS Signature V4) on top of HTTPX, which is already a dependency, and is tested against the published AWS vectors. Only `put` is needed today; add `get` and `delete` when a task needs them.
