#!/usr/bin/env bash
set -Eeuo pipefail

MODE="${1:?MODE required}"
OUT_ROOT="${2:?OUT_ROOT required}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WORKER="$HERE/run_${MODE}.sh"

if [[ ! -x "$WORKER" ]]; then
  echo "ERROR: missing worker for MODE=$MODE" >&2
  echo "WORKER=$WORKER" >&2
  exit 2
fi

exec "$WORKER" "$MODE" "$OUT_ROOT"
