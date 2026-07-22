#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/qis/run_365GeV_smoke.sh [options]

Options:
  --repo-root PATH       Repository root (default: inferred from script)
  --pilot-config PATH    Pilot YAML relative to repo
  --template PATH        Override the frozen 500 GeV input.sin template
  --prepare-only         Prepare and validate input.sin, but do not run WHIZARD
  --validate-only        Validate an already generated LHE file
  --lhe PATH             LHE file for --validate-only
  --force                Replace the 365 GeV smoke run directory
  -h, --help             Show this help

Default behavior prepares the new run directory, executes WHIZARD locally, finds
its generated LHE product, and runs the strict 365 GeV threshold audit.
EOF
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEFAULT_REPO=$(cd "$SCRIPT_DIR/../.." && pwd)
REPO=$DEFAULT_REPO
PILOT_CONFIG=configs/qis/paper_spin_365GeV_pilot.yaml
TEMPLATE=
PREPARE_ONLY=0
VALIDATE_ONLY=0
LHE=
FORCE=0

while (($#)); do
  case "$1" in
    --repo-root)
      REPO=$2
      shift 2
      ;;
    --pilot-config)
      PILOT_CONFIG=$2
      shift 2
      ;;
    --template)
      TEMPLATE=$2
      shift 2
      ;;
    --prepare-only)
      PREPARE_ONLY=1
      shift
      ;;
    --validate-only)
      VALIDATE_ONLY=1
      shift
      ;;
    --lhe)
      LHE=$2
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

REPO=$(cd "$REPO" && pwd)
cd "$REPO"

if [[ -f setup_lxplus.sh ]]; then
  # shellcheck disable=SC1091
  source ./setup_lxplus.sh
fi

python3 scripts/qis/validate_365GeV_threshold_inputs.py \
  --repo-root "$REPO" \
  --pilot-config "$PILOT_CONFIG" \
  --strict \
  --output /tmp/paper_spin_365GeV_config_preflight.json

if ((VALIDATE_ONLY)); then
  if [[ -z $LHE ]]; then
    echo "ERROR: --validate-only requires --lhe PATH" >&2
    exit 2
  fi
  python3 scripts/qis/validate_365GeV_threshold_inputs.py \
    --repo-root "$REPO" \
    --pilot-config "$PILOT_CONFIG" \
    --lhe "$LHE" \
    --strict
  exit $?
fi

mapfile -t PILOT_VALUES < <(
  python3 - "$REPO" "$PILOT_CONFIG" <<'PY'
from pathlib import Path
import sys
import yaml

repo = Path(sys.argv[1])
path = Path(sys.argv[2])
if not path.is_absolute():
    path = repo / path
payload = yaml.safe_load(path.read_text())
print(payload["production"]["output_run_dir"])
print(payload["production"].get("input_filename", "input.sin"))
print(payload["production"].get("whizard_command", "whizard"))
print(payload["sample"]["events"])
print(payload["sample"]["sample_id"])
PY
)

RUN_DIR=${PILOT_VALUES[0]}
INPUT_NAME=${PILOT_VALUES[1]}
WHIZARD_COMMAND=${PILOT_VALUES[2]}
REQUESTED_EVENTS=${PILOT_VALUES[3]}
SAMPLE_ID=${PILOT_VALUES[4]}

if [[ $RUN_DIR != /* ]]; then
  RUN_DIR="$REPO/$RUN_DIR"
fi

PREPARE_ARGS=(
  --repo-root "$REPO"
  --pilot-config "$PILOT_CONFIG"
)
if [[ -n $TEMPLATE ]]; then
  PREPARE_ARGS+=(--template "$TEMPLATE")
fi
if ((FORCE)); then
  PREPARE_ARGS+=(--force)
fi

python3 scripts/qis/prepare_365GeV_smoke.py "${PREPARE_ARGS[@]}"

python3 scripts/qis/validate_365GeV_prepared_input.py \
  --repo-root "$REPO" \
  --pilot-config "$PILOT_CONFIG" \
  --input "$RUN_DIR/$INPUT_NAME" \
  --strict \
  --output "$RUN_DIR/prepared_input_validation.json"

python3 scripts/qis/validate_365GeV_threshold_inputs.py \
  --repo-root "$REPO" \
  --pilot-config "$PILOT_CONFIG" \
  --strict \
  --output "$RUN_DIR/config_validation.json"

if ((PREPARE_ONLY)); then
  echo
  echo "365 GeV smoke input prepared without executing WHIZARD:"
  echo "  $RUN_DIR/$INPUT_NAME"
  echo
  echo "Prepared-input contract passed. Review the transformation before running:"
  echo "  sed -n '1,240p' '$RUN_DIR/input_500_to_365.patch'"
  exit 0
fi

if ! command -v "$WHIZARD_COMMAND" >/dev/null 2>&1; then
  echo "ERROR: WHIZARD command not found: $WHIZARD_COMMAND" >&2
  exit 1
fi

printf '%s\n' \
  "============================================================" \
  "365 GeV WHIZARD smoke" \
  "============================================================" \
  "Sample:            $SAMPLE_ID" \
  "Requested events:  $REQUESTED_EVENTS" \
  "Run directory:     $RUN_DIR" \
  "Input:             $INPUT_NAME" \
  "WHIZARD:           $(command -v "$WHIZARD_COMMAND")" \
  "============================================================"

cd "$RUN_DIR"
"$WHIZARD_COMMAND" "$INPUT_NAME" 2>&1 | tee console.log

mapfile -t LHE_CANDIDATES < <(
  find "$RUN_DIR" -maxdepth 1 -type f \
    \( -iname '*.lhe' -o -iname '*.lhe.gz' -o -iname '*.lhef' -o -iname '*.lhef.gz' \) \
    -printf '%s\t%T@\t%p\n' \
  | sort -k1,1nr -k2,2nr \
  | cut -f3-
)

if ((${#LHE_CANDIDATES[@]} == 0)); then
  echo "ERROR: WHIZARD finished but no LHE/LHEF file was found in $RUN_DIR" >&2
  echo "Inspect: $RUN_DIR/console.log" >&2
  exit 1
fi

LHE=${LHE_CANDIDATES[0]}
cd "$REPO"

python3 scripts/qis/validate_365GeV_threshold_inputs.py \
  --repo-root "$REPO" \
  --pilot-config "$PILOT_CONFIG" \
  --lhe "$LHE" \
  --strict \
  --output "$RUN_DIR/threshold_validation.json" \
  | tee "$RUN_DIR/threshold_validation.log"

(
  cd "$RUN_DIR"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > SHA256SUMS.txt
)

cat > "$RUN_DIR/SMOKE_COMPLETE.md" <<EOF
# 365 GeV WHIZARD smoke complete

- Sample: \`$SAMPLE_ID\`
- Requested events: \`$REQUESTED_EVENTS\`
- LHE product: \`$LHE\`
- Threshold validation: \`threshold_validation.json\`
- Input transformation: \`input_500_to_365.patch\`
- Checksums: \`SHA256SUMS.txt\`

This is a tree-level continuum ttbar smoke sample near threshold. It does not
claim threshold resummation or nonresonant W+b W-bbar accuracy.
EOF

printf '\n365 GeV WHIZARD smoke passed:\n  %s\n' "$RUN_DIR"
