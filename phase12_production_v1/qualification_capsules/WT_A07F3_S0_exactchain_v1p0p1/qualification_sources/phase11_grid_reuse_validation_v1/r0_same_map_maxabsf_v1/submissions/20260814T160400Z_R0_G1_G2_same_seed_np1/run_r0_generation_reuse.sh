#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF_USAGE'
Usage:
  run_r0_generation_reuse.sh \
    --repo PATH \
    --mode NAME \
    --workspace-tar PATH \
    --expected-vg2-sha SHA256 \
    --expected-phs-sha SHA256 \
    --source-card PATH \
    --output-root PATH \
    --generation-seed N \
    --events N \
    [--dry-run 0|1]
EOF_USAGE
}

REPO=""
MODE=""
WORKSPACE_TAR=""
EXPECTED_VG2_SHA=""
EXPECTED_PHS_SHA=""
SOURCE_CARD=""
OUTPUT_ROOT=""
GENERATION_SEED=""
EVENTS=""
DRY_RUN=0

while (($#)); do
  case "$1" in
    --repo)
      REPO=${2:?}
      shift 2
      ;;
    --mode)
      MODE=${2:?}
      shift 2
      ;;
    --workspace-tar)
      WORKSPACE_TAR=${2:?}
      shift 2
      ;;
    --expected-vg2-sha)
      EXPECTED_VG2_SHA=${2:?}
      shift 2
      ;;
    --expected-phs-sha)
      EXPECTED_PHS_SHA=${2:?}
      shift 2
      ;;
    --source-card)
      SOURCE_CARD=${2:?}
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT=${2:?}
      shift 2
      ;;
    --generation-seed)
      GENERATION_SEED=${2:?}
      shift 2
      ;;
    --events)
      EVENTS=${2:?}
      shift 2
      ;;
    --dry-run)
      DRY_RUN=${2:?}
      shift 2
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

for V in \
  REPO \
  MODE \
  WORKSPACE_TAR \
  EXPECTED_VG2_SHA \
  EXPECTED_PHS_SHA \
  SOURCE_CARD \
  OUTPUT_ROOT \
  GENERATION_SEED \
  EVENTS
do
  if [[ -z "${!V}" ]]; then
    echo "ERROR: required value $V is empty" >&2
    exit 2
  fi
done

if [[ "$DRY_RUN" != 0 && "$DRY_RUN" != 1 ]]; then
  echo "ERROR: --dry-run must be 0 or 1" >&2
  exit 2
fi

if [[ ! "$GENERATION_SEED" =~ ^[0-9]+$ ]]; then
  echo "ERROR: generation seed must be an integer" >&2
  exit 2
fi

if [[ ! "$EVENTS" =~ ^[0-9]+$ ]] || (( EVENTS < 1 )); then
  echo "ERROR: events must be a positive integer" >&2
  exit 2
fi

for F in \
  "$WORKSPACE_TAR" \
  "$SOURCE_CARD" \
  "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"
do
  if [[ ! -f "$F" ]]; then
    echo "ERROR: missing required file: $F" >&2
    exit 2
  fi
done

SOURCE_DIR="$(dirname "$SOURCE_CARD")"
SOURCE_COMMON="$SOURCE_DIR/common"

if [[ ! -d "$SOURCE_COMMON" ]]; then
  echo "ERROR: missing source common directory: $SOURCE_COMMON" >&2
  exit 2
fi

source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

WHIZARD_VERSION_LINE="$(whizard --version | head -n 1)"

if [[ "$WHIZARD_VERSION_LINE" != *"3.1.8"* ]]; then
  echo "ERROR: wrong WHIZARD runtime: $WHIZARD_VERSION_LINE" >&2
  exit 2
fi

if [[ -n "${_CONDOR_SCRATCH_DIR:-}" ]]; then
  SCRATCH="$_CONDOR_SCRATCH_DIR/phase11c_r0_${MODE}"
  rm -rf "$SCRATCH"
  mkdir -p "$SCRATCH"
else
  SCRATCH="$(mktemp -d "/tmp/${USER:-user}_phase11c_r0_${MODE}_XXXXXX")"
fi

cleanup() {
  rm -rf "$SCRATCH" || true
}
trap cleanup EXIT

echo "============================================================"
echo "PHASE11C_R0_MODE=$MODE"
echo "HOST=$(hostname -f 2>/dev/null || hostname)"
echo "SCRATCH=$SCRATCH"
echo "WORKSPACE_TAR=$WORKSPACE_TAR"
echo "GENERATION_SEED=$GENERATION_SEED"
echo "EVENTS=$EVENTS"
echo "WHIZARD=$WHIZARD_VERSION_LINE"
echo "============================================================"

cp -a "$SOURCE_CARD" "$SCRATCH/process.sin"
cp -a "$SOURCE_COMMON" "$SCRATCH/common"

if [[ -f "$SOURCE_DIR/render_context.json" ]]; then
  cp -a \
    "$SOURCE_DIR/render_context.json" \
    "$SCRATCH/render_context.json"
fi

# Localize generated-tree absolute common includes.
python3 - \
  "$SCRATCH/process.sin" \
  "$SOURCE_COMMON" <<'PY'
from pathlib import Path
import re
import sys

card = Path(sys.argv[1])
source_common = Path(sys.argv[2])

text = card.read_text(encoding="utf-8")

pattern = re.compile(
    r'include\("'
    + re.escape(str(source_common))
    + r'/([^"]+)"\)'
)

localized, n = pattern.subn(
    lambda m: f'include("common/{m.group(1)}")',
    text,
)

if str(source_common) in localized:
    raise SystemExit(
        "ERROR: absolute source-common path remains in localized process.sin"
    )

for required in (
    'include("common/integration.inc")',
    'include("common/event_output.inc")',
):
    if localized.count(required) != 1:
        raise SystemExit(
            f"ERROR: expected exactly one {required}; "
            f"found {localized.count(required)}"
        )

card.write_text(localized, encoding="utf-8")

print(f"LOCALIZED_INCLUDE_REPLACEMENTS={n}")
PY

# ----------------------------------------------------------------------
# CRITICAL 11C CONTRACT:
# generation-only reuse.
#
# NO iterations statement.
# NO integrate(proc_epmum).
# ----------------------------------------------------------------------

cat > "$SCRATCH/common/integration.inc" <<'EOF_INTEGRATION'
! Phase 11C generation-only frozen-workspace reuse.
!
! Deliberately contains NO iterations statement and NO integrate command.
! Existing proc_epmum.i1.phs / proc_epmum.m1.vg2 must be reused.

$integration_method = "vamp2"
$rng_method = "rng_stream"
$vamp_parallel_method = "simple"

?omega_openmp = false
openmp_num_threads = 1
EOF_INTEGRATION

printf 'seed = %s\n' \
  "$GENERATION_SEED" \
  >> "$SCRATCH/common/integration.inc"

SAMPLE_NAME="phase11c_${MODE}_seed${GENERATION_SEED}"

{
  echo 'simulate (proc_epmum) {'
  echo "  n_events = $EVENTS"
  echo '  sample_format = lhef'
  printf '  $sample = "%s"\n' "$SAMPLE_NAME"
  echo '}'
} > "$SCRATCH/common/event_output.inc"

if grep -Eq \
  '^[[:space:]]*(iterations[[:space:]]*=|integrate[[:space:]]*\()' \
  "$SCRATCH/common/integration.inc"
then
  echo "ERROR: generation-only integration include contains integration commands" >&2
  exit 2
fi

# Stage the frozen workspace into private scratch.
tar -xzf "$WORKSPACE_TAR" -C "$SCRATCH"

PHS="$SCRATCH/proc_epmum.i1.phs"
VG2="$SCRATCH/proc_epmum.m1.vg2"

for F in "$PHS" "$VG2"; do
  if [[ ! -f "$F" ]]; then
    echo "ERROR: workspace artifact missing after extraction: $F" >&2
    exit 2
  fi
done

PHS_SHA_BEFORE="$(sha256sum "$PHS" | awk '{print $1}')"
VG2_SHA_BEFORE="$(sha256sum "$VG2" | awk '{print $1}')"
WORKSPACE_TAR_SHA="$(sha256sum "$WORKSPACE_TAR" | awk '{print $1}')"

echo "WORKSPACE_TAR_SHA256=$WORKSPACE_TAR_SHA"
echo "PHS_SHA256_BEFORE=$PHS_SHA_BEFORE"
echo "VG2_SHA256_BEFORE=$VG2_SHA_BEFORE"

if [[ "$PHS_SHA_BEFORE" != "$EXPECTED_PHS_SHA" ]]; then
  echo "ERROR: PHS hash mismatch" >&2
  echo "EXPECTED=$EXPECTED_PHS_SHA" >&2
  echo "OBSERVED=$PHS_SHA_BEFORE" >&2
  exit 3
fi

if [[ "$VG2_SHA_BEFORE" != "$EXPECTED_VG2_SHA" ]]; then
  echo "ERROR: VG2 hash mismatch" >&2
  echo "EXPECTED=$EXPECTED_VG2_SHA" >&2
  echo "OBSERVED=$VG2_SHA_BEFORE" >&2
  exit 3
fi

echo
echo "===== EFFECTIVE PROCESS.SIN ====="
nl -ba "$SCRATCH/process.sin"

echo
echo "===== GENERATION-ONLY INTEGRATION.INC ====="
nl -ba "$SCRATCH/common/integration.inc"

echo
echo "===== EVENT_OUTPUT.INC ====="
nl -ba "$SCRATCH/common/event_output.inc"

if [[ "$DRY_RUN" == 1 ]]; then
  echo
  echo "PHASE11C_R0_DRY_RUN=PASS"
  exit 0
fi

DEST="$OUTPUT_ROOT/$MODE"

if [[ -e "$DEST" ]]; then
  echo "ERROR: output already exists: $DEST" >&2
  exit 2
fi

mkdir -p "$DEST"

START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
START_EPOCH="$(date +%s)"

cd "$SCRATCH"

set +e
timeout 12h whizard process.sin 2>&1 | tee console.log
WHIZARD_RC=${PIPESTATUS[0]}
set -e

END_EPOCH="$(date +%s)"
END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
WALL_SECONDS=$((END_EPOCH - START_EPOCH))

PHS_SHA_AFTER="$(sha256sum "$PHS" | awk '{print $1}')"
VG2_SHA_AFTER="$(sha256sum "$VG2" | awk '{print $1}')"

GRID_UNCHANGED=1

if [[ "$PHS_SHA_AFTER" != "$PHS_SHA_BEFORE" ]]; then
  GRID_UNCHANGED=0
fi

if [[ "$VG2_SHA_AFTER" != "$VG2_SHA_BEFORE" ]]; then
  GRID_UNCHANGED=0
fi

# Only actual integration activity is forbidden.
# Process-library compilation messages alone are not treated as integration.
INTEGRATION_EVIDENCE_COUNT="$(
  grep -Ec \
    'Starting integration for process|Integrate: iterations[[:space:]]*=|VAMP2: Initialize new grids' \
    console.log \
    || true
)"

mapfile -t LHE_FILES < <(
  find "$SCRATCH" \
    -maxdepth 1 \
    -type f \
    -name "${SAMPLE_NAME}*.lhe" \
    | sort
)

EVENTS_WRITTEN=0
LHE_FILE=""

if (( ${#LHE_FILES[@]} == 1 )); then
  LHE_FILE="${LHE_FILES[0]}"
  EVENTS_WRITTEN="$(
    grep -c '<event>' "$LHE_FILE" || true
  )"
fi

EFFICIENCY_LINE="$(
  grep -E \
    'Events: actual unweighting efficiency' \
    console.log \
    | tail -n 1 \
    || true
)"

{
  echo "MODE=$MODE"
  echo "WHIZARD_RC=$WHIZARD_RC"
  echo "START_UTC=$START_UTC"
  echo "END_UTC=$END_UTC"
  echo "WALL_SECONDS=$WALL_SECONDS"
  echo "EVENTS_REQUESTED=$EVENTS"
  echo "EVENTS_WRITTEN=$EVENTS_WRITTEN"
  echo "LHE_FILE=$LHE_FILE"
  echo "INTEGRATION_EVIDENCE_COUNT=$INTEGRATION_EVIDENCE_COUNT"
  echo "PHS_SHA256_BEFORE=$PHS_SHA_BEFORE"
  echo "PHS_SHA256_AFTER=$PHS_SHA_AFTER"
  echo "VG2_SHA256_BEFORE=$VG2_SHA_BEFORE"
  echo "VG2_SHA256_AFTER=$VG2_SHA_AFTER"
  echo "GRID_UNCHANGED=$GRID_UNCHANGED"
  echo "EFFICIENCY_LINE=$EFFICIENCY_LINE"
} > reuse_checks.txt

grep -Ein \
  'excess|overweight|weight.*exceed|unweighting efficiency|maximum weight|max weight' \
  console.log \
  > generation_diagnostics.txt \
  || true

FAILURES=()

if (( WHIZARD_RC != 0 )); then
  FAILURES+=("whizard_rc_${WHIZARD_RC}")
fi

if (( INTEGRATION_EVIDENCE_COUNT != 0 )); then
  FAILURES+=("unexpected_integration")
fi

if (( GRID_UNCHANGED != 1 )); then
  FAILURES+=("private_workspace_mutated")
fi

if (( ${#LHE_FILES[@]} != 1 )); then
  FAILURES+=("lhe_file_count_${#LHE_FILES[@]}")
elif (( EVENTS_WRITTEN != EVENTS )); then
  FAILURES+=("event_count_${EVENTS_WRITTEN}_expected_${EVENTS}")
fi

STATUS="PASS"

if (( ${#FAILURES[@]} != 0 )); then
  STATUS="FAIL"
fi

FAILURE_TEXT="$(
  IFS=';'
  echo "${FAILURES[*]:-}"
)"

cp -a \
  console.log \
  process.sin \
  reuse_checks.txt \
  generation_diagnostics.txt \
  "$DEST/"

mkdir -p "$DEST/effective_common"

cp -a \
  common/integration.inc \
  common/event_output.inc \
  "$DEST/effective_common/"

[[ -f render_context.json ]] \
  && cp -a render_context.json "$DEST/" \
  || true

[[ -f whizard.log ]] \
  && cp -a whizard.log "$DEST/" \
  || true

if [[ -n "$LHE_FILE" && -f "$LHE_FILE" ]]; then
  cp -a "$LHE_FILE" "$DEST/"
fi

find "$SCRATCH" \
  -maxdepth 1 \
  -type f \
  -name "${SAMPLE_NAME}*.evx" \
  -exec cp -a {} "$DEST/" \;

printf '%s\n' "$WHIZARD_RC" \
  > "$DEST/whizard_return_code.txt"

printf '%s\n' "$WORKSPACE_TAR_SHA" \
  > "$DEST/source_workspace_tar.sha256"

printf '%s  proc_epmum.i1.phs\n' "$PHS_SHA_BEFORE" \
  > "$DEST/staged_workspace_before.sha256"

printf '%s  proc_epmum.m1.vg2\n' "$VG2_SHA_BEFORE" \
  >> "$DEST/staged_workspace_before.sha256"

printf '%s  proc_epmum.i1.phs\n' "$PHS_SHA_AFTER" \
  > "$DEST/staged_workspace_after.sha256"

printf '%s  proc_epmum.m1.vg2\n' "$VG2_SHA_AFTER" \
  >> "$DEST/staged_workspace_after.sha256"

python3 - \
  "$DEST/run_metadata.json" \
  "$MODE" \
  "$STATUS" \
  "$FAILURE_TEXT" \
  "$WORKSPACE_TAR" \
  "$WORKSPACE_TAR_SHA" \
  "$SOURCE_CARD" \
  "$GENERATION_SEED" \
  "$EVENTS" \
  "$EVENTS_WRITTEN" \
  "$WALL_SECONDS" \
  "$WHIZARD_RC" \
  "$INTEGRATION_EVIDENCE_COUNT" \
  "$GRID_UNCHANGED" \
  "$PHS_SHA_BEFORE" \
  "$PHS_SHA_AFTER" \
  "$VG2_SHA_BEFORE" \
  "$VG2_SHA_AFTER" \
  "$EFFICIENCY_LINE" \
  "$WHIZARD_VERSION_LINE" <<'PY'
import json
from pathlib import Path
import sys

(
    output,
    mode,
    status,
    failure_text,
    workspace_tar,
    workspace_tar_sha,
    source_card,
    generation_seed,
    events_requested,
    events_written,
    wall_seconds,
    whizard_rc,
    integration_evidence_count,
    grid_unchanged,
    phs_before,
    phs_after,
    vg2_before,
    vg2_after,
    efficiency_line,
    whizard_version,
) = sys.argv[1:]

payload = {
    "schema_version": 1,
    "phase": "11C-R0",
    "mode": mode,
    "status": status,
    "failures": [
        x for x in failure_text.split(";") if x
    ],
    "workspace_source": {
        "path": workspace_tar,
        "sha256": workspace_tar_sha,
    },
    "source_card": source_card,
    "generation_seed": int(generation_seed),
    "events_requested": int(events_requested),
    "events_written": int(events_written),
    "wall_seconds": int(wall_seconds),
    "whizard_rc": int(whizard_rc),
    "integration_evidence_count": int(
        integration_evidence_count
    ),
    "private_workspace_unchanged": bool(
        int(grid_unchanged)
    ),
    "workspace_hashes": {
        "phs_before": phs_before,
        "phs_after": phs_after,
        "vg2_before": vg2_before,
        "vg2_after": vg2_after,
    },
    "unweighting_efficiency_line": efficiency_line,
    "whizard_version": whizard_version,
}

Path(output).write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n"
)
PY

(
  cd "$DEST"

  find . \
    -type f \
    ! -name 'OUTPUT_SHA256SUMS.txt' \
    -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > OUTPUT_SHA256SUMS.txt
)

if [[ "$STATUS" == "PASS" ]]; then
  touch "$DEST/EXECUTION_SUCCESS"
  touch "$DEST/REUSE_PASS"

  echo
  echo "============================================================"
  echo "PHASE11C_R0_REUSE=PASS"
  echo "MODE=$MODE"
  echo "EVENTS_WRITTEN=$EVENTS_WRITTEN"
  echo "WALL_SECONDS=$WALL_SECONDS"
  echo "$EFFICIENCY_LINE"
  echo "OUTPUT=$DEST"
  echo "============================================================"
  exit 0
else
  touch "$DEST/REUSE_FAIL"

  echo
  echo "============================================================"
  echo "PHASE11C_R0_REUSE=FAIL"
  echo "MODE=$MODE"
  echo "FAILURES=$FAILURE_TEXT"
  echo "OUTPUT=$DEST"
  echo "============================================================"
  exit 1
fi
