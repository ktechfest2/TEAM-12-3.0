# AGENTS.md (.github)

- CI must call `./scripts/verify.sh` and nothing that diverges from it. If you need a new check, add it to the app Makefile `verify` target so local and CI stay identical.
- Pin action major versions. Never print secrets; never add `pull_request_target`.
- The PR template checklist mirrors the root `AGENTS.md` non negotiables. Keep them in step.
