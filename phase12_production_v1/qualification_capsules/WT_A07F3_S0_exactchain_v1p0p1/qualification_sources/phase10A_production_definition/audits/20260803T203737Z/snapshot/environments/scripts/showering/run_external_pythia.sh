#!/usr/bin/env bash
# Runtime wrapper for external PYTHIA8/HepMC3 handoff.
#
# Preferred project driver interface:
#   qis_lhe_to_hepmc3 --input FILE.lhe --output FILE.hepmc3 --settings FILE.cmnd
#                    --sample-id ID --campaign-id ID [options]
#
# Legacy fallback:
#   executable CONFIG LHE OUT

set -euo pipefail

LHE=""
OUT=""
CONFIG=""
PYTHIA_EXEC="${PYTHIA_EXEC:-pythia8}"

CAMPAIGN_ID="${CAMPAIGN_ID:-full6f_365gev_ee_ttbar_spinpol_v1}"
SAMPLE_ID="${SAMPLE_ID:-unknown_sample}"
SHARD_ID="${SHARD_ID:-bridge}"
MAX_EVENTS="${MAX_EVENTS:--1}"
SEED="${SEED:-12345}"
METADATA=""
ALLOW_FAILED_EVENTS="${ALLOW_FAILED_EVENTS:-0}"
MAX_CONSECUTIVE_FAILURES="${MAX_CONSECUTIVE_FAILURES:-10}"
EXTRA_SET_ARGS=()

usage() {
  cat <<'USAGE'
Usage:
  run_external_pythia.sh --lhe FILE.lhe --out FILE.hepmc3 --config FILE.cmnd [options]

Required:
  --lhe FILE
  --out FILE
  --config FILE

Options:
  --pythia-exec FILE
  --campaign-id ID
  --sample-id ID
  --shard-id ID
  --max-events N
  --seed N
  --metadata FILE.json
  --allow-failed-events
  --max-consecutive-failures N
  --set 'Pythia:setting = value'

Environment fallbacks:
  PYTHIA_EXEC, CAMPAIGN_ID, SAMPLE_ID, SHARD_ID, MAX_EVENTS, SEED
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lhe) LHE="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --config) CONFIG="$2"; shift 2 ;;
    --pythia-exec) PYTHIA_EXEC="$2"; shift 2 ;;
    --campaign-id) CAMPAIGN_ID="$2"; shift 2 ;;
    --sample-id) SAMPLE_ID="$2"; shift 2 ;;
    --shard-id) SHARD_ID="$2"; shift 2 ;;
    --max-events) MAX_EVENTS="$2"; shift 2 ;;
    --seed) SEED="$2"; shift 2 ;;
    --metadata) METADATA="$2"; shift 2 ;;
    --allow-failed-events) ALLOW_FAILED_EVENTS=1; shift ;;
    --max-consecutive-failures) MAX_CONSECUTIVE_FAILURES="$2"; shift 2 ;;
    --set) EXTRA_SET_ARGS+=(--set "$2"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$LHE" && -f "$LHE" ]] || { echo "ERROR: --lhe file is required" >&2; exit 2; }
[[ -n "$OUT" ]] || { echo "ERROR: --out is required" >&2; exit 2; }
[[ -n "$CONFIG" && -f "$CONFIG" ]] || { echo "ERROR: --config file is required" >&2; exit 2; }
command -v "$PYTHIA_EXEC" >/dev/null 2>&1 || { echo "ERROR: PYTHIA executable not found: $PYTHIA_EXEC" >&2; exit 127; }

mkdir -p "$(dirname "$OUT")"

HELP_TEXT="$("$PYTHIA_EXEC" --help 2>&1 || true)"

if grep -q -- '--input FILE.lhe' <<<"$HELP_TEXT"; then
  if [[ -z "$METADATA" ]]; then
    METADATA="${OUT}.metadata.json"
  fi

  cmd=(
    "$PYTHIA_EXEC"
    --input "$LHE"
    --output "$OUT"
    --settings "$CONFIG"
    --sample-id "$SAMPLE_ID"
    --campaign-id "$CAMPAIGN_ID"
    --shard-id "$SHARD_ID"
    --max-events "$MAX_EVENTS"
    --seed "$SEED"
    --metadata "$METADATA"
    --max-consecutive-failures "$MAX_CONSECUTIVE_FAILURES"
  )

  if [[ "$ALLOW_FAILED_EVENTS" == "1" ]]; then
    cmd+=(--allow-failed-events)
  fi

  if [[ "${#EXTRA_SET_ARGS[@]}" -gt 0 ]]; then
    cmd+=("${EXTRA_SET_ARGS[@]}")
  fi

  echo "RUN_EXTERNAL_PYTHIA_MODE=named_project_driver"
  printf 'RUN_EXTERNAL_PYTHIA_CMD='
  printf '%q ' "${cmd[@]}"
  printf '\n'

  exec "${cmd[@]}"
fi

echo "RUN_EXTERNAL_PYTHIA_MODE=legacy_positional"
exec "$PYTHIA_EXEC" "$CONFIG" "$LHE" "$OUT"
