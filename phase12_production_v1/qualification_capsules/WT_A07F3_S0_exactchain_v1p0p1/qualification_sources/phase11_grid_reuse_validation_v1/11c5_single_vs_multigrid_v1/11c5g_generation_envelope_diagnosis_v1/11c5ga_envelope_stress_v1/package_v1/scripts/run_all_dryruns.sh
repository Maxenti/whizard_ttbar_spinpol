#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_all_dryruns.sh \
    --itemdata FILE \
    --dryrun-dir DIR \
    --repo DIR \
    --worker FILE \
    --source-card FILE \
    --output-root DIR
EOF
}

ITEMDATA=""; DRYRUN_DIR=""; REPO=""; WORKER=""; SOURCE_CARD=""; OUTPUT_ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --itemdata) ITEMDATA=$2; shift 2 ;;
    --dryrun-dir) DRYRUN_DIR=$2; shift 2 ;;
    --repo) REPO=$2; shift 2 ;;
    --worker) WORKER=$2; shift 2 ;;
    --source-card) SOURCE_CARD=$2; shift 2 ;;
    --output-root) OUTPUT_ROOT=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg $1" >&2; usage >&2; exit 2 ;;
  esac
done
for V in ITEMDATA DRYRUN_DIR REPO WORKER SOURCE_CARD OUTPUT_ROOT; do
  [[ -n "${!V}" ]] || { echo "ERROR: missing $V" >&2; exit 2; }
done
mkdir -p "$DRYRUN_DIR"

N=0
while IFS=$'\t' read -r MODE GRID KIND TAR VG2SHA PHSSHA GRIDSEED SHARDSEED METADATASEED EVENTS; do
  [[ -n "${MODE:-}" ]] || continue
  N=$((N+1))
  echo "[$N/60] dry-run $MODE grid=$GRID seed=$SHARDSEED events=$EVENTS"
  "$WORKER" \
    --repo "$REPO" \
    --mode "$MODE" \
    --checkpoint-kind "$KIND" \
    --workspace-tar "$TAR" \
    --expected-vg2-sha "$VG2SHA" \
    --expected-phs-sha "$PHSSHA" \
    --source-card "$SOURCE_CARD" \
    --output-root "$OUTPUT_ROOT" \
    --grid-seed "$GRIDSEED" \
    --pre-integration-seed "$SHARDSEED" \
    --generation-seed "$METADATASEED" \
    --events "$EVENTS" \
    --dry-run 1 \
    > "$DRYRUN_DIR/${MODE}.dryrun.txt"
done < "$ITEMDATA"

[[ "$N" -eq 60 ]] || { echo "ERROR: expected 60 dry-runs, got $N" >&2; exit 2; }
echo "C5GA_DRYRUN_COUNT=$N"
echo "C5GA_ALL_DRYRUNS_COMPLETE=PASS"
