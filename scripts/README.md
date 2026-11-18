# scripts

Repository wide shell scripts. App specific tasks live in each app's Makefile.

| Script | Purpose |
| --- | --- |
| `verify.sh` | The quality gate: API checks, contract drift, web checks. CI and agents run this. |
| `dev.sh` | Runs API, worker and web together for local development. |

Scripts must be idempotent, use `set -euo pipefail`, and work from any directory.
