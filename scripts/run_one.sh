#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run_one.sh [--dry-run] [--force] <sample.sin> [final-run-directory]

The WHIZARD compilation/integration/simulation runs in local scratch.
All persistent products are staged to the EOS-backed project output tree.

Options:
  --dry-run  Validate paths and print the resolved execution plan only.
  --force    Remove an existing non-empty final run directory before staging.
  -h, --help Show this help.
USAGE
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
OUTPUT_ROOT=${WHIZARD_TTBAR_OUTPUT_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
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

case "$OUTPUT_ROOT" in
  /eos/*) ;;
  *)
    if [[ ${WHIZARD_ALLOW_NON_EOS_OUTPUT:-0} != 1 ]]; then
      echo "ERROR: persistent output root is not on EOS: $OUTPUT_ROOT" >&2
      echo "Set WHIZARD_ALLOW_NON_EOS_OUTPUT=1 only for an intentional test." >&2
      exit 5
    fi
    ;;
esac

if [[ ${#POSITIONAL[@]} -eq 2 ]]; then
  FINAL_RUN_DIR=${POSITIONAL[1]}
else
  FINAL_RUN_DIR="$OUTPUT_ROOT/runs/$INITIAL_STATE/$SAMPLE_ID"
fi
FINAL_RUN_DIR=$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$FINAL_RUN_DIR")
CENTRAL_LOG="$OUTPUT_ROOT/logs/${SAMPLE_ID}.log"
LHE_DIR="$OUTPUT_ROOT/lhe/$INITIAL_STATE"

case "$FINAL_RUN_DIR" in
  /eos/*) ;;
  *)
    if [[ ${WHIZARD_ALLOW_NON_EOS_OUTPUT:-0} != 1 ]]; then
      echo "ERROR: final run directory is not on EOS: $FINAL_RUN_DIR" >&2
      exit 6
    fi
    ;;
esac

if [[ $DRY_RUN -eq 0 ]] && ! command -v whizard >/dev/null 2>&1; then
  echo "ERROR: whizard is not available in PATH." >&2
  exit 7
fi

FINAL_RUN_DIR_NONEMPTY=0
if [[ -d "$FINAL_RUN_DIR" ]] && \
   [[ -n "$(find "$FINAL_RUN_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
  FINAL_RUN_DIR_NONEMPTY=1
fi

# A dry run must never remove or reject an existing destination. It should
# report the destination state and exit without modifying either AFS or EOS.
if [[ $DRY_RUN -eq 0 && $FINAL_RUN_DIR_NONEMPTY -eq 1 ]]; then
  if [[ $FORCE -eq 1 ]]; then
    echo "Removing existing final run directory: $FINAL_RUN_DIR"
    rm -rf "$FINAL_RUN_DIR"
  else
    echo "ERROR: final run directory already exists and is non-empty: $FINAL_RUN_DIR" >&2
    echo "Use --force for an intentional real rerun, or provide a different final run directory." >&2
    exit 8
  fi
fi

if [[ -n ${_CONDOR_SCRATCH_DIR:-} ]]; then
  SCRATCH_BASE=$_CONDOR_SCRATCH_DIR
elif [[ -n ${TMPDIR:-} ]]; then
  SCRATCH_BASE=$TMPDIR
else
  SCRATCH_BASE=/tmp/$USER
fi
mkdir -p "$SCRATCH_BASE"
WORK_DIR=$(mktemp -d "$SCRATCH_BASE/whizard_${SAMPLE_ID}_XXXXXX")

cat <<PLAN
Sample ID:          $SAMPLE_ID
Initial state:      $INITIAL_STATE
SINDARIN:           $SIN_ABS
Scratch workspace:  $WORK_DIR
Final run directory:$FINAL_RUN_DIR
Central log:        $CENTRAL_LOG
LHE directory:      $LHE_DIR
Output root:        $OUTPUT_ROOT
Destination exists: $FINAL_RUN_DIR_NONEMPTY
Force replacement:  $FORCE
Dry run:            $DRY_RUN
PLAN

if [[ $DRY_RUN -eq 1 ]]; then
  rm -rf "$WORK_DIR"
  echo "DRY-RUN OK"
  exit 0
fi

mkdir -p "$(dirname "$FINAL_RUN_DIR")" "$(dirname "$CENTRAL_LOG")" "$LHE_DIR"
cp "$SIN_ABS" "$WORK_DIR/input.sin"

START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  echo "sample_id=$SAMPLE_ID"
  echo "initial_state=$INITIAL_STATE"
  echo "sindarin_file=$SIN_ABS"
  echo "scratch_workspace=$WORK_DIR"
  echo "final_run_directory=$FINAL_RUN_DIR"
  echo "output_root=$OUTPUT_ROOT"
  echo "hostname=$(hostname -f 2>/dev/null || hostname)"
  echo "start_time_utc=$START_UTC"
  echo "whizard_path=$(command -v whizard)"
  echo "return_code=RUNNING"
  echo
  whizard --version 2>&1 || true
} > "$WORK_DIR/run_metadata.txt"

env | sort > "$WORK_DIR/environment.txt"

set +e
(
  cd "$WORK_DIR"
  set -o pipefail
  whizard input.sin 2>&1 | tee console.log
)
RC=$?
set -e

END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 - "$WORK_DIR/run_metadata.txt" "$RC" "$END_UTC" <<'PY_METADATA'
from pathlib import Path
import sys
p = Path(sys.argv[1])
rc = sys.argv[2]
end = sys.argv[3]
lines = p.read_text().splitlines()
out = []
for line in lines:
    out.append(f"return_code={rc}" if line.startswith("return_code=") else line)
out.append(f"end_time_utc={end}")
p.write_text("\n".join(out) + "\n")
PY_METADATA

# Stage the complete workspace, including generated O'Mega/Fortran libraries,
# integration grids, EVX, LHE, and native logs, to EOS.
mkdir -p "$FINAL_RUN_DIR"
if ! rsync -rlt --delete --safe-links --omit-dir-times "$WORK_DIR/" "$FINAL_RUN_DIR/"; then
  echo "ERROR: failed to stage scratch workspace to EOS." >&2
  echo "Scratch has been preserved at: $WORK_DIR" >&2
  exit 90
fi

if [[ -f "$WORK_DIR/whizard.log" ]]; then
  cp "$WORK_DIR/whizard.log" "$CENTRAL_LOG"
elif [[ -f "$WORK_DIR/console.log" ]]; then
  cp "$WORK_DIR/console.log" "$CENTRAL_LOG"
fi

mapfile -t LHE_FILES < <(
  find "$WORK_DIR" -maxdepth 2 -type f \
    \( -iname '*.lhe' -o -iname '*.lhe.gz' -o -iname '*.lhef' -o -iname '*.lhef.gz' \) \
    -print | sort
)

if [[ ${#LHE_FILES[@]} -gt 0 ]]; then
  for src in "${LHE_FILES[@]}"; do
    cp "$src" "$LHE_DIR/$(basename "$src")"
  done
  echo "Collected ${#LHE_FILES[@]} LHE/LHEF file(s) to EOS."
else
  echo "WARNING: no LHE/LHEF output discovered below $WORK_DIR" >&2
fi

# metadata/ is expected to be an EOS-backed symlink in the AFS repository.
python3 "$REPO_ROOT/scripts/make_sample_manifest.py" --repo-root "$REPO_ROOT" >/dev/null || true

rm -rf "$WORK_DIR"

if [[ $RC -ne 0 ]]; then
  echo "ERROR: WHIZARD exited with code $RC for $SAMPLE_ID" >&2
  echo "Failure products were staged to: $FINAL_RUN_DIR" >&2
  exit "$RC"
fi

echo "Completed successfully: $SAMPLE_ID"
