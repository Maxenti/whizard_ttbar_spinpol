#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run_r0v2_generation_reuse.sh \
    --repo PATH \
    --mode NAME \
    --checkpoint-kind G1|G2 \
    --workspace-tar PATH \
    --expected-vg2-sha SHA256 \
    --expected-phs-sha SHA256 \
    --source-card PATH \
    --output-root PATH \
    --grid-seed N \
    --generation-seed N \
    --events N \
    [--dry-run 0|1]
USAGE
}

REPO=""
MODE=""
CHECKPOINT_KIND=""
WORKSPACE_TAR=""
EXPECTED_VG2_SHA=""
EXPECTED_PHS_SHA=""
SOURCE_CARD=""
OUTPUT_ROOT=""
GRID_SEED=""
GENERATION_SEED=""
EVENTS=""
DRY_RUN=0

while (($#)); do
  case "$1" in
    --repo)
      REPO=${2:?}; shift 2 ;;
    --mode)
      MODE=${2:?}; shift 2 ;;
    --checkpoint-kind)
      CHECKPOINT_KIND=${2:?}; shift 2 ;;
    --workspace-tar)
      WORKSPACE_TAR=${2:?}; shift 2 ;;
    --expected-vg2-sha)
      EXPECTED_VG2_SHA=${2:?}; shift 2 ;;
    --expected-phs-sha)
      EXPECTED_PHS_SHA=${2:?}; shift 2 ;;
    --source-card)
      SOURCE_CARD=${2:?}; shift 2 ;;
    --output-root)
      OUTPUT_ROOT=${2:?}; shift 2 ;;
    --grid-seed)
      GRID_SEED=${2:?}; shift 2 ;;
    --generation-seed)
      GENERATION_SEED=${2:?}; shift 2 ;;
    --events)
      EVENTS=${2:?}; shift 2 ;;
    --dry-run)
      DRY_RUN=${2:?}; shift 2 ;;
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
  REPO MODE CHECKPOINT_KIND WORKSPACE_TAR \
  EXPECTED_VG2_SHA EXPECTED_PHS_SHA \
  SOURCE_CARD OUTPUT_ROOT GRID_SEED \
  GENERATION_SEED EVENTS
do
  [[ -n "${!V}" ]] || {
    echo "ERROR: $V unset" >&2
    exit 2
  }
done

case "$CHECKPOINT_KIND" in
  G1)
    STORED_ITERATIONS='5:50000:"gw", 5:100000:""'
    ;;
  G2)
    STORED_ITERATIONS='5:50000:"gw", 3:200000:""'
    ;;
  *)
    echo "ERROR: checkpoint kind must be G1 or G2" >&2
    exit 2
    ;;
esac

[[ -f "$WORKSPACE_TAR" ]] || {
  echo "ERROR: missing workspace tar: $WORKSPACE_TAR" >&2
  exit 2
}

[[ -f "$SOURCE_CARD" ]] || {
  echo "ERROR: missing source card: $SOURCE_CARD" >&2
  exit 2
}

SOURCE_DIR="$(dirname "$SOURCE_CARD")"
SOURCE_COMMON="$SOURCE_DIR/common"

source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

if [[ -n "${_CONDOR_SCRATCH_DIR:-}" ]]; then
  SCRATCH="$_CONDOR_SCRATCH_DIR/phase11c_r0v2_${MODE}"
  rm -rf "$SCRATCH"
  mkdir -p "$SCRATCH"
else
  SCRATCH="$(mktemp -d "/tmp/${USER}_phase11c_r0v2_${MODE}_XXXXXX")"
fi

cleanup() {
  rm -rf "$SCRATCH" || true
}
trap cleanup EXIT

cp -a "$SOURCE_CARD" "$SCRATCH/process.sin"
cp -a "$SOURCE_COMMON" "$SCRATCH/common"

[[ -f "$SOURCE_DIR/render_context.json" ]] \
  && cp -a "$SOURCE_DIR/render_context.json" "$SCRATCH/" \
  || true

python3 - \
  "$SCRATCH/process.sin" \
  "$SOURCE_COMMON" <<'PY'
from pathlib import Path
import re
import sys

card = Path(sys.argv[1])
common = Path(sys.argv[2])

text = card.read_text()

pattern = re.compile(
    r'include\("' + re.escape(str(common)) + r'/([^"]+)"\)'
)

text, n = pattern.subn(
    lambda m: f'include("common/{m.group(1)}")',
    text,
)

if str(common) in text:
    raise SystemExit("ERROR: absolute common path remains")

card.write_text(text)

print(f"LOCALIZED_INCLUDE_REPLACEMENTS={n}")
PY

tar -xzf "$WORKSPACE_TAR" -C "$SCRATCH"

PHS="$SCRATCH/proc_epmum.i1.phs"
VG2="$SCRATCH/proc_epmum.m1.vg2"

[[ -f "$PHS" ]] || {
  echo "ERROR: staged PHS missing" >&2
  exit 3
}

[[ -f "$VG2" ]] || {
  echo "ERROR: staged VG2 missing" >&2
  exit 3
}

PHS_BEFORE="$(sha256sum "$PHS" | awk '{print $1}')"
VG2_BEFORE="$(sha256sum "$VG2" | awk '{print $1}')"

[[ "$PHS_BEFORE" == "$EXPECTED_PHS_SHA" ]] || {
  echo "ERROR: PHS input hash mismatch" >&2
  exit 3
}

[[ "$VG2_BEFORE" == "$EXPECTED_VG2_SHA" ]] || {
  echo "ERROR: VG2 input hash mismatch" >&2
  exit 3
}

cat > "$SCRATCH/common/integration.inc" <<EOF_INTEGRATION
\$integration_method = "vamp2"
\$rng_method = "rng_stream"
\$vamp_parallel_method = "simple"

?omega_openmp = false
openmp_num_threads = 1

seed = $GRID_SEED

iterations = $STORED_ITERATIONS
integrate (proc_epmum)
EOF_INTEGRATION

SAMPLE="phase11c_${MODE}_seed${GENERATION_SEED}"

cat > "$SCRATCH/common/event_output.inc" <<EOF_EVENT
! Independent Phase-11 validation-event RNG.
seed = $GENERATION_SEED

simulate (proc_epmum) {
  n_events = $EVENTS
  sample_format = lhef
  \$sample = "$SAMPLE"
}
EOF_EVENT

echo "============================================================"
echo "MODE=$MODE"
echo "CHECKPOINT_KIND=$CHECKPOINT_KIND"
echo "GRID_SEED=$GRID_SEED"
echo "GENERATION_SEED=$GENERATION_SEED"
echo "EVENTS=$EVENTS"
echo "STORED_ITERATIONS=$STORED_ITERATIONS"
echo "PHS_SHA256_BEFORE=$PHS_BEFORE"
echo "VG2_SHA256_BEFORE=$VG2_BEFORE"
echo "============================================================"

echo
echo "===== INTEGRATION.INC ====="
cat "$SCRATCH/common/integration.inc"

echo
echo "===== EVENT_OUTPUT.INC ====="
cat "$SCRATCH/common/event_output.inc"

if [[ "$DRY_RUN" == 1 ]]; then
  echo "R0V2_DRY_RUN=PASS"
  exit 0
fi

DEST="$OUTPUT_ROOT/$MODE"

[[ ! -e "$DEST" ]] || {
  echo "ERROR: output already exists: $DEST" >&2
  exit 2
}

mkdir -p "$DEST"

cd "$SCRATCH"

START_EPOCH=$(date +%s)

set +e
timeout 12h whizard process.sin 2>&1 | tee console.log
WHIZARD_RC=${PIPESTATUS[0]}
set -e

END_EPOCH=$(date +%s)
WALL_SECONDS=$((END_EPOCH - START_EPOCH))

PHS_AFTER="$(sha256sum "$PHS" | awk '{print $1}')"
VG2_AFTER="$(sha256sum "$VG2" | awk '{print $1}')"

WORKSPACE_UNCHANGED=1

[[ "$PHS_AFTER" == "$PHS_BEFORE" ]] || WORKSPACE_UNCHANGED=0
[[ "$VG2_AFTER" == "$VG2_BEFORE" ]] || WORKSPACE_UNCHANGED=0

# A new numerical integration that checkpoints state would mutate the VG2.
# The explicit integration/replay messages themselves are expected.
NEW_GRID_INIT_COUNT="$(
  grep -Ec \
    'VAMP2: Initialize new grids' \
    console.log \
    || true
)"

mapfile -t LHE_FILES < <(
  find . \
    -maxdepth 1 \
    -type f \
    -name "${SAMPLE}*.lhe" \
    | sort
)

EVENTS_WRITTEN=0
LHE_FILE=""

if (( ${#LHE_FILES[@]} == 1 )); then
  LHE_FILE="${LHE_FILES[0]}"
  EVENTS_WRITTEN="$(grep -c '<event>' "$LHE_FILE" || true)"
fi

EFFICIENCY_LINE="$(
  grep -E \
    'Events: actual unweighting efficiency' \
    console.log \
    | tail -1 \
    || true
)"

grep -Ein \
  'excess|overweight|weight.*exceed|actual unweighting efficiency|max.*weight|maximum.*weight' \
  console.log \
  > generation_diagnostics.txt \
  || true

FAILURES=()

(( WHIZARD_RC == 0 )) \
  || FAILURES+=("whizard_rc_${WHIZARD_RC}")

(( WORKSPACE_UNCHANGED == 1 )) \
  || FAILURES+=("workspace_mutated")

(( NEW_GRID_INIT_COUNT == 0 )) \
  || FAILURES+=("new_grid_initialization")

(( ${#LHE_FILES[@]} == 1 )) \
  || FAILURES+=("lhe_file_count_${#LHE_FILES[@]}")

if (( ${#LHE_FILES[@]} == 1 )); then
  (( EVENTS_WRITTEN == EVENTS )) \
    || FAILURES+=("event_count_${EVENTS_WRITTEN}_expected_${EVENTS}")
fi

STATUS=PASS

(( ${#FAILURES[@]} == 0 )) || STATUS=FAIL

{
  echo "MODE=$MODE"
  echo "CHECKPOINT_KIND=$CHECKPOINT_KIND"
  echo "STATUS=$STATUS"
  echo "WHIZARD_RC=$WHIZARD_RC"
  echo "GRID_SEED=$GRID_SEED"
  echo "GENERATION_SEED=$GENERATION_SEED"
  echo "EVENTS_REQUESTED=$EVENTS"
  echo "EVENTS_WRITTEN=$EVENTS_WRITTEN"
  echo "WALL_SECONDS=$WALL_SECONDS"
  echo "WORKSPACE_UNCHANGED=$WORKSPACE_UNCHANGED"
  echo "NEW_GRID_INIT_COUNT=$NEW_GRID_INIT_COUNT"
  echo "PHS_SHA256_BEFORE=$PHS_BEFORE"
  echo "PHS_SHA256_AFTER=$PHS_AFTER"
  echo "VG2_SHA256_BEFORE=$VG2_BEFORE"
  echo "VG2_SHA256_AFTER=$VG2_AFTER"
  echo "EFFICIENCY_LINE=$EFFICIENCY_LINE"
  echo "FAILURES=$(IFS=';'; echo "${FAILURES[*]:-}")"
} > reuse_checks.txt

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

[[ -f whizard.log ]] \
  && cp -a whizard.log "$DEST/" \
  || true

[[ -f "$LHE_FILE" ]] \
  && cp -a "$LHE_FILE" "$DEST/" \
  || true

find . \
  -maxdepth 1 \
  -type f \
  -name "${SAMPLE}*.evx" \
  -exec cp -a {} "$DEST/" \;

python3 - \
  "$DEST/run_metadata.json" \
  "$MODE" \
  "$CHECKPOINT_KIND" \
  "$STATUS" \
  "$GRID_SEED" \
  "$GENERATION_SEED" \
  "$EVENTS" \
  "$EVENTS_WRITTEN" \
  "$WALL_SECONDS" \
  "$WHIZARD_RC" \
  "$WORKSPACE_UNCHANGED" \
  "$NEW_GRID_INIT_COUNT" \
  "$PHS_BEFORE" \
  "$PHS_AFTER" \
  "$VG2_BEFORE" \
  "$VG2_AFTER" \
  "$EFFICIENCY_LINE" <<'PY'
import json
from pathlib import Path
import sys

(
    out,
    mode,
    checkpoint_kind,
    status,
    grid_seed,
    generation_seed,
    requested,
    written,
    wall,
    rc,
    unchanged,
    new_grid,
    phs_before,
    phs_after,
    vg2_before,
    vg2_after,
    efficiency,
) = sys.argv[1:]

obj = {
    "schema_version": 2,
    "phase": "11C-R0v2",
    "mode": mode,
    "checkpoint_kind": checkpoint_kind,
    "status": status,
    "grid_seed": int(grid_seed),
    "generation_seed": int(generation_seed),
    "events_requested": int(requested),
    "events_written": int(written),
    "wall_seconds": int(wall),
    "whizard_rc": int(rc),
    "workspace_unchanged": bool(int(unchanged)),
    "new_grid_initialization_count": int(new_grid),
    "phs_sha256_before": phs_before,
    "phs_sha256_after": phs_after,
    "vg2_sha256_before": vg2_before,
    "vg2_sha256_after": vg2_after,
    "unweighting_efficiency_line": efficiency,
}

Path(out).write_text(
    json.dumps(obj, indent=2, sort_keys=True) + "\n"
)
PY

(
  cd "$DEST"

  find . \
    -type f \
    ! -name OUTPUT_SHA256SUMS.txt \
    -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > OUTPUT_SHA256SUMS.txt
)

if [[ "$STATUS" == PASS ]]; then
  touch "$DEST/REUSE_PASS"

  echo
  echo "============================================================"
  echo "R0V2=PASS"
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
  echo "R0V2=FAIL"
  cat reuse_checks.txt
  echo "OUTPUT=$DEST"
  echo "============================================================"
  exit 1
fi
