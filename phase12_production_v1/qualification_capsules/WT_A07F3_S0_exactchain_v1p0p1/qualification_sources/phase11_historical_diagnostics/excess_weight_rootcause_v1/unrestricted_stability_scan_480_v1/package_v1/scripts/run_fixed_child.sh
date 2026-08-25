#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage:
  run_fixed_child.sh \
    --mode MODE \
    --parent-mode PARENT_MODE \
    --adaptive-id AXX \
    --fixed-id FX \
    --seed-id SX \
    --campaign-dir DIR \
    --output-root EOS_DIR
USAGE
}

MODE=""
PARENT_MODE=""
ADAPTIVE_ID=""
FIXED_ID=""
SEED_ID=""
CAMPAIGN_DIR=""
OUTPUT_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --parent-mode) PARENT_MODE="$2"; shift 2 ;;
    --adaptive-id) ADAPTIVE_ID="$2"; shift 2 ;;
    --fixed-id) FIXED_ID="$2"; shift 2 ;;
    --seed-id) SEED_ID="$2"; shift 2 ;;
    --campaign-dir) CAMPAIGN_DIR="$2"; shift 2 ;;
    --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for V in MODE PARENT_MODE ADAPTIVE_ID FIXED_ID SEED_ID CAMPAIGN_DIR OUTPUT_ROOT; do
  if [[ -z "${!V}" ]]; then
    echo "ERROR: missing $V" >&2
    usage >&2
    exit 2
  fi
done

CAMPAIGN_ENV="$CAMPAIGN_DIR/campaign.env"
ADAPT_TSV="$CAMPAIGN_DIR/frozen_config/adaptive_prescriptions.tsv"
FIXED_TSV="$CAMPAIGN_DIR/frozen_config/fixed_prescriptions.tsv"
SEEDS_TSV="$CAMPAIGN_DIR/frozen_config/seeds.tsv"

for F in "$CAMPAIGN_ENV" "$ADAPT_TSV" "$FIXED_TSV" "$SEEDS_TSV"; do
  [[ -f "$F" ]] || { echo "ERROR: missing campaign input: $F" >&2; exit 2; }
done

# shellcheck disable=SC1090
source "$CAMPAIGN_ENV"

ADAPTIVE_SCHEDULE=$(awk -F '\t' -v id="$ADAPTIVE_ID" 'NR>1 && $1==id {print $2; exit}' "$ADAPT_TSV")
FIXED_SCHEDULE=$(awk -F '\t' -v id="$FIXED_ID" 'NR>1 && $1==id {print $2; exit}' "$FIXED_TSV")
FIXED_SEED=$(awk -F '\t' -v id="$SEED_ID" 'NR>1 && $1==id {print $3; exit}' "$SEEDS_TSV")

[[ -n "$ADAPTIVE_SCHEDULE" ]] || { echo "ERROR: unknown adaptive id $ADAPTIVE_ID" >&2; exit 2; }
[[ -n "$FIXED_SCHEDULE" ]] || { echo "ERROR: unknown fixed id $FIXED_ID" >&2; exit 2; }
[[ -n "$FIXED_SEED" ]] || { echo "ERROR: unknown seed id $SEED_ID" >&2; exit 2; }

FULL_SCHEDULE="${ADAPTIVE_SCHEDULE},${FIXED_SCHEDULE}"
PARENT_TAR="$OUTPUT_ROOT/adaptive/$PARENT_MODE/integration_artifacts.tar.gz"
DEST="$OUTPUT_ROOT/fixed/$PARENT_MODE/$FIXED_ID"

[[ -f "$SOURCE_CARD" ]] || { echo "ERROR: SOURCE_CARD missing: $SOURCE_CARD" >&2; exit 2; }
[[ -f "$PARENT_TAR" ]] || { echo "ERROR: parent workspace missing: $PARENT_TAR" >&2; exit 3; }

mkdir -p "$DEST"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

# Use a private subdirectory even under Condor scratch so cleanup cannot remove
# the scheduler-owned scratch root.
SCRATCH_PARENT="${_CONDOR_SCRATCH_DIR:-/tmp}"
WORK=$(mktemp -d "$SCRATCH_PARENT/${USER:-user}_${MODE}_XXXXXX")
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

mkdir -p "$WORK/common"

cp -a "$SOURCE_CARD" "$WORK/process.sin"
cp -a "$(dirname "$SOURCE_CARD")/common/." "$WORK/common/"
if [[ -f "$(dirname "$SOURCE_CARD")/render_context.json" ]]; then
  cp -a "$(dirname "$SOURCE_CARD")/render_context.json" "$WORK/render_context.json"
fi

python3 - "$WORK/process.sin" "$(dirname "$SOURCE_CARD")/common" <<'PY'
from pathlib import Path
import re
import sys
card = Path(sys.argv[1])
source_common = Path(sys.argv[2])
text = card.read_text()
pattern = re.compile(r'include\("' + re.escape(str(source_common)) + r'/([^\"]+)"\)')
text, n = pattern.subn(lambda m: f'include("common/{m.group(1)}")', text)
if n < 5:
    raise SystemExit(f"ERROR: expected >=5 localized common includes, got {n}")
# This campaign is integration-only. Never simulate events in these 480 nodes.
text, n_evt = re.subn(r'^.*include\("common/event_output\.inc"\).*$\n?', '', text, flags=re.M)
if n_evt != 1:
    raise SystemExit(f"ERROR: expected exactly one event_output include, removed {n_evt}")
card.write_text(text)
print(f"LOCALIZED_INCLUDE_REPLACEMENTS={n}")
print("EVENT_OUTPUT_INCLUDE_REMOVED=PASS")
PY

# Restore the exact adaptive-parent PHS/VG2 into the fresh scratch workspace.
tar -xzf "$PARENT_TAR" -C "$WORK"

PHS="$WORK/proc_epmum.i1.phs"
VG2="$WORK/proc_epmum.m1.vg2"
[[ -f "$PHS" ]] || { echo "ERROR: parent PHS missing after extract" >&2; exit 4; }
[[ -f "$VG2" ]] || { echo "ERROR: parent VG2 missing after extract" >&2; exit 4; }

PARENT_TAR_SHA=$(sha256sum "$PARENT_TAR" | awk '{print $1}')
PARENT_PHS_SHA=$(sha256sum "$PHS" | awk '{print $1}')
PARENT_VG2_SHA=$(sha256sum "$VG2" | awk '{print $1}')

cat > "$WORK/common/integration.inc" <<EOF2
\$integration_method = "vamp2"
\$rng_method = "rng_stream"
\$vamp_parallel_method = "simple"

?omega_openmp = false
openmp_num_threads = 1

seed = $FIXED_SEED

iterations = $FULL_SCHEDULE

integrate (proc_epmum)
EOF2

cat > "$WORK/fixed_child_contract.txt" <<EOF2
MODE=$MODE
PARENT_MODE=$PARENT_MODE
ADAPTIVE_ID=$ADAPTIVE_ID
FIXED_ID=$FIXED_ID
SEED_ID=$SEED_ID
FIXED_SEED=$FIXED_SEED
ADAPTIVE_SCHEDULE=$ADAPTIVE_SCHEDULE
FIXED_SCHEDULE=$FIXED_SCHEDULE
FULL_SCHEDULE=$FULL_SCHEDULE
PARENT_TAR=$PARENT_TAR
PARENT_TAR_SHA256=$PARENT_TAR_SHA
PARENT_PHS_SHA256=$PARENT_PHS_SHA
PARENT_VG2_SHA256=$PARENT_VG2_SHA
EOF2

# Runtime setup is deliberately identical to the qualified Phase-11 MPI/VAMP2 runtime.
# shellcheck disable=SC1090
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

WHIZARD_REALPATH=$(readlink -f "$(command -v whizard)")
EXPECTED_WHIZARD="$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/whizard"
EXPECTED_WHIZARD=$(readlink -f "$EXPECTED_WHIZARD")
if [[ "$WHIZARD_REALPATH" != "$EXPECTED_WHIZARD" ]]; then
  echo "ERROR: qualified WHIZARD path mismatch" >&2
  echo "got=$WHIZARD_REALPATH" >&2
  echo "expected=$EXPECTED_WHIZARD" >&2
  exit 5
fi

echo "============================================================"
echo "PHASE11_UNRESTRICTED_STABILITY_FIXED_CHILD_V1"
echo "MODE=$MODE"
echo "PARENT_MODE=$PARENT_MODE"
echo "ADAPTIVE_ID=$ADAPTIVE_ID"
echo "FIXED_ID=$FIXED_ID"
echo "SEED_ID=$SEED_ID"
echo "FIXED_SEED=$FIXED_SEED"
echo "ADAPTIVE_SCHEDULE=$ADAPTIVE_SCHEDULE"
echo "FIXED_SCHEDULE=$FIXED_SCHEDULE"
echo "FULL_SCHEDULE=$FULL_SCHEDULE"
echo "PARENT_TAR=$PARENT_TAR"
echo "WORK=$WORK"
echo "WHIZARD=$($(command -v whizard) --version | head -1)"
echo "============================================================"

echo "===== EFFECTIVE integration.inc ====="
cat "$WORK/common/integration.inc"
echo "===== EFFECTIVE process.sin ====="
cat "$WORK/process.sin"

cd "$WORK"
set +e
set -o pipefail
whizard process.sin 2>&1 | tee console.log
WHIZARD_RC=${PIPESTATUS[0]}
set +o pipefail
set -e

echo "WHIZARD_RC=$WHIZARD_RC" | tee -a console.log

REUSE_COUNT=$(grep -c 'VAMP2: Using grids and results from file' console.log || true)
INIT_COUNT=$(grep -c 'VAMP2: Initialize new grids' console.log || true)

FINAL_PHS_PRESENT=0
FINAL_VG2_PRESENT=0
[[ -f "$PHS" ]] && FINAL_PHS_PRESENT=1
[[ -f "$VG2" ]] && FINAL_VG2_PRESENT=1

FINAL_PHS_SHA=""
FINAL_VG2_SHA=""
[[ -f "$PHS" ]] && FINAL_PHS_SHA=$(sha256sum "$PHS" | awk '{print $1}')
[[ -f "$VG2" ]] && FINAL_VG2_SHA=$(sha256sum "$VG2" | awk '{print $1}')

PHS_UNCHANGED=0
[[ "$FINAL_PHS_SHA" == "$PARENT_PHS_SHA" ]] && PHS_UNCHANGED=1

STATUS=PASS
if [[ "$WHIZARD_RC" -ne 0 ]]; then STATUS=FAIL_WHIZARD; fi
if [[ "$REUSE_COUNT" -lt 1 ]]; then STATUS=FAIL_NO_REUSE_EVIDENCE; fi
if [[ "$INIT_COUNT" -ne 0 ]]; then STATUS=FAIL_NEW_GRID_INITIALIZED; fi
if [[ "$FINAL_PHS_PRESENT" -ne 1 || "$FINAL_VG2_PRESENT" -ne 1 ]]; then STATUS=FAIL_MISSING_ARTIFACT; fi
if [[ "$PHS_UNCHANGED" -ne 1 ]]; then STATUS=FAIL_PHS_CHANGED; fi

python3 - \
  fixed_child_metadata.json \
  "$STATUS" \
  "$MODE" \
  "$PARENT_MODE" \
  "$ADAPTIVE_ID" \
  "$FIXED_ID" \
  "$SEED_ID" \
  "$FIXED_SEED" \
  "$ADAPTIVE_SCHEDULE" \
  "$FIXED_SCHEDULE" \
  "$FULL_SCHEDULE" \
  "$PARENT_TAR" \
  "$PARENT_TAR_SHA" \
  "$PARENT_PHS_SHA" \
  "$PARENT_VG2_SHA" \
  "$FINAL_PHS_SHA" \
  "$FINAL_VG2_SHA" \
  "$PHS_UNCHANGED" \
  "$REUSE_COUNT" \
  "$INIT_COUNT" \
  "$WHIZARD_RC" \
  "$WHIZARD_REALPATH" <<'PY_META'
import json
from pathlib import Path
import sys
(
    out, status, mode, parent_mode, adaptive_id, fixed_id, seed_id,
    fixed_seed, adaptive_schedule, fixed_schedule, full_schedule,
    parent_tar, parent_tar_sha, parent_phs_sha, parent_vg2_sha,
    final_phs_sha, final_vg2_sha, phs_unchanged, reuse_count,
    init_count, whizard_rc, whizard_realpath,
) = sys.argv[1:]
payload = {
    "schema": "phase11_unrestricted_stability_fixed_child_v1",
    "status": status,
    "mode": mode,
    "parent_mode": parent_mode,
    "adaptive_id": adaptive_id,
    "fixed_id": fixed_id,
    "seed_id": seed_id,
    "fixed_seed": int(fixed_seed),
    "adaptive_schedule": adaptive_schedule,
    "fixed_schedule": fixed_schedule,
    "full_schedule": full_schedule,
    "parent_workspace_tar": parent_tar,
    "parent_workspace_tar_sha256": parent_tar_sha,
    "parent_phs_sha256": parent_phs_sha,
    "parent_vg2_sha256": parent_vg2_sha,
    "final_phs_sha256": final_phs_sha,
    "final_vg2_sha256": final_vg2_sha,
    "phs_unchanged": int(phs_unchanged),
    "reuse_message_count": int(reuse_count),
    "new_grid_init_count": int(init_count),
    "whizard_rc": int(whizard_rc),
    "whizard_realpath": whizard_realpath,
}
Path(out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY_META

# Preserve every diagnostic even on a failed node.
mkdir -p "$DEST"
cp -a console.log fixed_child_contract.txt fixed_child_metadata.json process.sin "$DEST/"
rm -rf "$DEST/common"
cp -a common "$DEST/common"

if [[ "$FINAL_PHS_PRESENT" -eq 1 && "$FINAL_VG2_PRESENT" -eq 1 ]]; then
  tar -czf integration_artifacts.tar.gz \
    proc_epmum.i1.phs \
    proc_epmum.m1.vg2
  cp -a integration_artifacts.tar.gz "$DEST/"
  sha256sum \
    proc_epmum.i1.phs \
    proc_epmum.m1.vg2 \
    integration_artifacts.tar.gz \
    > artifact_hashes.sha256
  cp -a artifact_hashes.sha256 "$DEST/"
fi

printf '%s\n' "$STATUS" > "$DEST/STATUS.txt"

if [[ "$STATUS" != "PASS" ]]; then
  echo "FIXED_CHILD_STATUS=$STATUS" >&2
  exit 20
fi

echo "REUSE_COUNT=$REUSE_COUNT"
echo "NEW_GRID_INIT_COUNT=$INIT_COUNT"
echo "PHS_UNCHANGED=$PHS_UNCHANGED"
echo "FIXED_CHILD_STATUS=PASS"
