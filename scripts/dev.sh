#!/usr/bin/env bash
# Runs API, worker and web in one terminal. Ctrl+C stops all three.
set -euo pipefail
cd "$(dirname "$0")/.."
trap 'kill 0' EXIT
make -C apps/api dev &
make -C apps/api worker &
make -C apps/web dev &
wait
