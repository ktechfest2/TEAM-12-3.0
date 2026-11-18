#!/usr/bin/env bash
# The single quality gate. CI runs exactly this. Agents run this before
# declaring work done. Exit code 0 means every check passed.
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf "\n\033[1;36m==> %s\033[0m\n" "$1"; }

step "api: lint, format, types, tests"
make -C apps/api verify

step "contract: openapi.json is current"
make -C apps/api openapi >/dev/null
if ! git diff --quiet -- contracts/openapi.json 2>/dev/null; then
  echo "contracts/openapi.json changed. Run 'make contract' and commit the result." >&2
  [[ "${CI:-}" == "true" ]] && exit 1
fi

step "web: lint, format, types, tests, build"
make -C apps/web verify

printf "\n\033[1;32mverify: all checks passed\033[0m\n"
