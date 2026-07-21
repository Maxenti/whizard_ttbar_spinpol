#!/usr/bin/env bash
set -euo pipefail

: "${REPO:?REPO is required}"
: "${INPUT:?INPUT is required}"
: "${CONFIG:?CONFIG is required}"
: "${REPLICAS:?REPLICAS is required}"
: "${REPLICA_START:?REPLICA_START is required}"
: "${REPLICA_STOP:?REPLICA_STOP is required}"
: "${SEED:?SEED is required}"
: "${OUTPUT:?OUTPUT is required}"

cd "$REPO"
source "$REPO/setup_lxplus.sh"

mkdir -p "$(dirname "$OUTPUT")"

python3 "$REPO/scripts/qis/run_paper_spin_closure.py" data \
  --input "$INPUT" \
  --config "$CONFIG" \
  --replicas "$REPLICAS" \
  --replica-start "$REPLICA_START" \
  --replica-stop "$REPLICA_STOP" \
  --seed "$SEED" \
  --output "$OUTPUT"
