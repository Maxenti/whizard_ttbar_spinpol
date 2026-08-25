#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage:
  run_adaptive_parent.sh \
    --mode AXX_SX \
    --adaptive-id AXX \
    --seed-id SX \
    --campaign-dir DIR \
    --output-root EOS_DIR \
    [--preflight-only]
USAGE
}

MODE=""
ADAPTIVE_ID=""
SEED_ID=""
CAMPAIGN_DIR=""
OUTPUT_ROOT=""
PREFLIGHT_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --adaptive-id) ADAPTIVE_ID="$2"; shift 2 ;;
    --seed-id) SEED_ID="$2"; shift 2 ;;
    --campaign-dir) CAMPAIGN_DIR="$2"; shift 2 ;;
    --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
    --preflight-only) PREFLIGHT_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for V in MODE ADAPTIVE_ID SEED_ID CAMPAIGN_DIR OUTPUT_ROOT; do
  [[ -n "${!V}" ]] || { echo "ERROR: missing $V" >&2; exit 2; }
done

CAMPAIGN_ENV="$CAMPAIGN_DIR/campaign.env"
ADAPT_TSV="$CAMPAIGN_DIR/frozen_config/adaptive_prescriptions.tsv"
SEEDS_TSV="$CAMPAIGN_DIR/frozen_config/seeds.tsv"
[[ -f "$CAMPAIGN_ENV" ]] || { echo "ERROR: missing $CAMPAIGN_ENV" >&2; exit 2; }
# shellcheck disable=SC1090
source "$CAMPAIGN_ENV"

ADAPTIVE_SCHEDULE=$(awk -F '\t' -v id="$ADAPTIVE_ID" 'NR>1 && $1==id {print $2; exit}' "$ADAPT_TSV")
ADAPTIVE_SEED=$(awk -F '\t' -v id="$SEED_ID" 'NR>1 && $1==id {print $2; exit}' "$SEEDS_TSV")
[[ -n "$ADAPTIVE_SCHEDULE" ]] || { echo "ERROR: unknown adaptive id $ADAPTIVE_ID" >&2; exit 2; }
[[ -n "$ADAPTIVE_SEED" ]] || { echo "ERROR: unknown seed id $SEED_ID" >&2; exit 2; }

[[ -f "$SOURCE_CARD" ]] || { echo "ERROR: frozen SOURCE_CARD missing: $SOURCE_CARD" >&2; exit 2; }
ACTUAL_SOURCE_SHA=$(sha256sum "$SOURCE_CARD" | awk '{print $1}')
if [[ "$ACTUAL_SOURCE_SHA" != "$FROZEN_SOURCE_CARD_SHA256" ]]; then
  echo "ERROR: frozen source-card SHA mismatch" >&2
  echo "got=$ACTUAL_SOURCE_SHA" >&2
  echo "expected=$FROZEN_SOURCE_CARD_SHA256" >&2
  exit 2
fi

DEST="$OUTPUT_ROOT/adaptive/$MODE"
mkdir -p "$DEST"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

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
text, n_evt = re.subn(r'^.*include\("common/event_output\.inc"\).*$\n?', '', text, flags=re.M)
if n_evt != 1:
    raise SystemExit(f"ERROR: expected exactly one event_output include, removed {n_evt}")
card.write_text(text)
print(f"LOCALIZED_INCLUDE_REPLACEMENTS={n}")
print("EVENT_OUTPUT_INCLUDE_REMOVED=PASS")
PY

cat > "$WORK/common/integration.inc" <<EOF2
\$integration_method = "vamp2"
\$rng_method = "rng_stream"
\$vamp_parallel_method = "simple"

?omega_openmp = false
openmp_num_threads = 1

seed = $ADAPTIVE_SEED

iterations = $ADAPTIVE_SCHEDULE

integrate (proc_epmum)
EOF2

# shellcheck disable=SC1090
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"
WHIZARD_REALPATH=$(readlink -f "$(command -v whizard)")
EXPECTED_WHIZARD=$(readlink -f "$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/whizard")
[[ "$WHIZARD_REALPATH" == "$EXPECTED_WHIZARD" ]] || {
  echo "ERROR: qualified WHIZARD path mismatch" >&2
  echo "got=$WHIZARD_REALPATH" >&2
  echo "expected=$EXPECTED_WHIZARD" >&2
  exit 5
}

echo "============================================================"
echo "PHASE11_TTBAR_SUITE_ADAPTIVE_PARENT_V1"
echo "MODE=$MODE"
echo "ADAPTIVE_ID=$ADAPTIVE_ID"
echo "SEED_ID=$SEED_ID"
echo "ADAPTIVE_SEED=$ADAPTIVE_SEED"
echo "ADAPTIVE_SCHEDULE=$ADAPTIVE_SCHEDULE"
echo "SOURCE_CARD=$SOURCE_CARD"
echo "WORK=$WORK"
echo "PREFLIGHT_ONLY=$PREFLIGHT_ONLY"
echo "WHIZARD=$($(command -v whizard) --version | head -1)"
echo "============================================================"
echo "===== EFFECTIVE integration.inc ====="
cat "$WORK/common/integration.inc"
echo "===== EFFECTIVE process.sin ====="
cat "$WORK/process.sin"

if [[ "$PREFLIGHT_ONLY" -eq 1 ]]; then
  echo "ADAPTIVE_PARENT_PREFLIGHT=PASS"
  exit 0
fi

cd "$WORK"
set +e
set -o pipefail
whizard process.sin 2>&1 | tee console.log
WHIZARD_RC=${PIPESTATUS[0]}
set +o pipefail
set -e

echo "WHIZARD_RC=$WHIZARD_RC" | tee -a console.log

PHS=proc_epmum.i1.phs
VG2=proc_epmum.m1.vg2
INIT_COUNT=$(grep -c 'VAMP2: Initialize new grids' console.log || true)
REUSE_COUNT=$(grep -c 'VAMP2: Using grids and results from file' console.log || true)

STATUS=PASS
[[ "$WHIZARD_RC" -eq 0 ]] || STATUS=FAIL_WHIZARD
[[ -f "$PHS" && -f "$VG2" ]] || STATUS=FAIL_MISSING_ARTIFACT
[[ "$INIT_COUNT" -ge 1 ]] || STATUS=FAIL_NO_NEW_GRID_INIT

PHS_SHA=""
VG2_SHA=""
[[ -f "$PHS" ]] && PHS_SHA=$(sha256sum "$PHS" | awk '{print $1}')
[[ -f "$VG2" ]] && VG2_SHA=$(sha256sum "$VG2" | awk '{print $1}')

python3 - \
  metadata.json \
  "$STATUS" \
  "$MODE" \
  "$ADAPTIVE_ID" \
  "$SEED_ID" \
  "$ADAPTIVE_SEED" \
  "$ADAPTIVE_SCHEDULE" \
  "$PHS_SHA" \
  "$VG2_SHA" \
  "$INIT_COUNT" \
  "$REUSE_COUNT" \
  "$WHIZARD_RC" \
  "$WHIZARD_REALPATH" <<'PY_META'
import json
from pathlib import Path
import sys
(
    out, status, mode, adaptive_id, seed_id, adaptive_seed,
    adaptive_schedule, phs_sha, vg2_sha, init_count,
    reuse_count, whizard_rc, whizard_realpath,
) = sys.argv[1:]
payload = {
    "schema": "phase11_ttbar_suite_adaptive_parent_v1",
    "status": status,
    "mode": mode,
    "adaptive_id": adaptive_id,
    "seed_id": seed_id,
    "adaptive_seed": int(adaptive_seed),
    "adaptive_schedule": adaptive_schedule,
    "phs_sha256": phs_sha,
    "vg2_sha256": vg2_sha,
    "new_grid_init_count": int(init_count),
    "reuse_message_count": int(reuse_count),
    "whizard_rc": int(whizard_rc),
    "whizard_realpath": whizard_realpath,
}
Path(out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY_META

cp -a console.log metadata.json process.sin "$DEST/"
rm -rf "$DEST/common"
cp -a common "$DEST/common"
[[ -f render_context.json ]] && cp -a render_context.json "$DEST/"

if [[ -f "$PHS" && -f "$VG2" ]]; then
  tar -czf integration_artifacts.tar.gz "$PHS" "$VG2"
  cp -a integration_artifacts.tar.gz "$DEST/"
  sha256sum "$PHS" "$VG2" integration_artifacts.tar.gz > SHA256SUMS
  cp -a SHA256SUMS "$DEST/"
fi

printf '%s\n' "$STATUS" > "$DEST/STATUS.txt"
if [[ "$STATUS" != "PASS" ]]; then
  echo "ADAPTIVE_PARENT_STATUS=$STATUS" >&2
  exit 20
fi

touch "$DEST/EXECUTION_SUCCESS"
echo "ADAPTIVE_PARENT_STATUS=PASS"
