# AGENTS.md (scripts)

- `verify.sh` is the contract between agents, people and CI. Do not make it skip checks, swallow failures or depend on network services. If a check needs to be removed, write an ADR first.
- New scripts: bash with `set -euo pipefail`, `cd "$(dirname "$0")/.."` at the top, and a comment on line 2 saying what the script is for.
- Never put secrets or real phone numbers in scripts.
