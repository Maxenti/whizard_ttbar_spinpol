#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_one.sh [--dry-run] [--force] <sample.sin> [run-directory]

Options:
  --dry-run  Validate paths and print the resolved execution plan only.
  --force    Remove an existing non-empty run directory before starting.
  -h, --help Show this help.
EOF
}

DRY_RUN=0
FORCE=0
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; POSITIONAL+=("$@"); break ;;
    -*) echo "ERROR: unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [[ ${#POSITIONAL[@]} -lt 1 || ${#POSITIONAL[@]} -gt 2 ]]; then
  usage >&2
  exit 2
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
SIN_INPUT=${POSITIONAL[0]}

if [[ ! -f "$SIN_INPUT" ]]; then
  echo "ERROR: SINDARIN file does not exist: $SIN_INPUT" >&2
  exit 3
fi

SIN_ABS=$(readlink -f "$SIN_INPUT")
SAMPLE_ID=$(basename "$SIN_ABS" .sin)

case "$SIN_ABS" in
  */sindarin/ee/*) INITIAL_STATE=ee ;;
  */sindarin/mumu/*) INITIAL_STATE=mumu ;;
  *)
    echo "ERROR: cannot infer initial state from path: $SIN_ABS" >&2
    echo "Expected the file below sindarin/ee or sindarin/mumu." >&2
    exit 4
    ;;
esac

if [[ ${#POSITIONAL[@]} -eq 2 ]]; then
  RUN_DIR=${POSITIONAL[1]}
else
  RUN_DIR="$REPO_ROOT/runs/$INITIAL_STATE/$SAMPLE_ID"
fi
RUN_DIR=$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$RUN_DIR")
CENTRAL_LOG="$REPO_ROOT/logs/${SAMPLE_ID}.log"
LHE_DIR="$REPO_ROOT/lhe/$INITIAL_STATE"

if [[ $DRY_RUN -eq 0 ]] && ! command -v whizard >/dev/null 2>&1; then
  echo "ERROR: whizard is not available in PATH." >&2
  echo "Enter the intended WHIZARD environment before running." >&2
  exit 5
fi

if [[ -d "$RUN_DIR" ]] && [[ -n "$(find "$RUN_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
  if [[ $FORCE -eq 1 ]]; then
    echo "Removing existing run directory: $RUN_DIR"
    rm -rf "$RUN_DIR"
  else
    echo "ERROR: run directory already exists and is non-empty: $RUN_DIR" >&2
    echo "Use --force or provide a different run directory." >&2
    exit 6
  fi
fi

cat <<EOF
Sample ID:      $SAMPLE_ID
Initial state:  $INITIAL_STATE
SINDARIN:       $SIN_ABS
Run directory:  $RUN_DIR
Central log:    $CENTRAL_LOG
LHE directory:  $LHE_DIR
Dry run:        $DRY_RUN
EOF

if [[ $DRY_RUN -eq 1 ]]; then
  echo "DRY-RUN OK"
  exit 0
fi

mkdir -p "$RUN_DIR" "$REPO_ROOT/logs" "$LHE_DIR"
cp "$SIN_ABS" "$RUN_DIR/input.sin"

START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  echo "sample_id=$SAMPLE_ID"
  echo "initial_state=$INITIAL_STATE"
  echo "sindarin_file=$SIN_ABS"
  echo "run_directory=$RUN_DIR"
  echo "hostname=$(hostname -f 2>/dev/null || hostname)"
  echo "start_time_utc=$START_UTC"
  echo "whizard_path=$(command -v whizard)"
  echo "return_code=RUNNING"
  echo
  whizard --version 2>&1 || true
} > "$RUN_DIR/run_metadata.txt"

env | sort > "$RUN_DIR/environment.txt"

set +e
(
  cd "$RUN_DIR"
  set -o pipefail
  whizard input.sin 2>&1 | tee console.log
)
RC=$?
set -e

END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 - "$RUN_DIR/run_metadata.txt" "$RC" "$END_UTC" <<'PY_METADATA'
from pathlib import Path
import sys
p = Path(sys.argv[1])
rc = sys.argv[2]
end = sys.argv[3]
lines = p.read_text().splitlines()
out = []
for line in lines:
    out.append(f'return_code={rc}' if line.startswith('return_code=') else line)
out.append(f'end_time_utc={end}')
p.write_text('\n'.join(out) + '\n')
PY_METADATA

if [[ -f "$RUN_DIR/whizard.log" ]]; then
  cp "$RUN_DIR/whizard.log" "$CENTRAL_LOG"
fi

mapfile -t LHE_FILES < <(
  find "$RUN_DIR" -maxdepth 2 -type f \
    \( -iname '*.lhe' -o -iname '*.lhe.gz' -o -iname '*.lhef' -o -iname '*.lhef.gz' \) \
    -print | sort
)

if [[ ${#LHE_FILES[@]} -gt 0 ]]; then
  for src in "${LHE_FILES[@]}"; do
    cp "$src" "$LHE_DIR/$(basename "$src")"
  done
  echo "Collected ${#LHE_FILES[@]} LHE/LHEF file(s)."
else
  echo "WARNING: no LHE/LHEF output discovered below $RUN_DIR" >&2
fi

python3 "$REPO_ROOT/scripts/make_sample_manifest.py" --repo-root "$REPO_ROOT" >/dev/null || true

if [[ $RC -ne 0 ]]; then
  echo "ERROR: WHIZARD exited with code $RC for $SAMPLE_ID" >&2
  exit "$RC"
fi

echo "Completed successfully: $SAMPLE_ID"
