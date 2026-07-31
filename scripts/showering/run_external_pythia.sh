#!/usr/bin/env bash
# Runtime wrapper; fails explicitly if PYTHIA runtime is absent.
set -euo pipefail
LHE=""; OUT=""; CONFIG=""; PYTHIA_EXEC=${PYTHIA_EXEC:-pythia8}
while [[ $# -gt 0 ]]; do case "$1" in --lhe) LHE="$2"; shift 2 ;; --out) OUT="$2"; shift 2 ;; --config) CONFIG="$2"; shift 2 ;; *) echo "ERROR: unknown argument $1" >&2; exit 2 ;; esac; done
[[ -n "$LHE" && -f "$LHE" ]] || { echo "ERROR: --lhe file is required" >&2; exit 2; }
[[ -n "$OUT" ]] || { echo "ERROR: --out is required" >&2; exit 2; }
[[ -n "$CONFIG" && -f "$CONFIG" ]] || { echo "ERROR: --config file is required" >&2; exit 2; }
command -v "$PYTHIA_EXEC" >/dev/null 2>&1 || { echo "ERROR: PYTHIA executable not found: $PYTHIA_EXEC" >&2; exit 127; }
exec "$PYTHIA_EXEC" "$CONFIG" "$LHE" "$OUT"
