#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run_d1d2_integration_v3.sh MODE OUT_ROOT [--preflight-only]

MODE:
  G1_S2
  D2_vamp_np1
USAGE
}

MODE="${1:-}"
OUT_ROOT="${2:-}"
PREFLIGHT_ONLY=0

if [[ "${3:-}" == "--preflight-only" ]]; then
  PREFLIGHT_ONLY=1
elif [[ -n "${3:-}" ]]; then
  echo "ERROR: unknown third argument: $3" >&2
  usage >&2
  exit 2
fi

if [[ -z "$MODE" || -z "$OUT_ROOT" ]]; then
  usage >&2
  exit 2
fi

case "$MODE" in
  G1_S2)
    INTEGRATION_METHOD="vamp2"
    ;;
  D2_vamp_np1)
    INTEGRATION_METHOD="vamp"
    ;;
  *)
    echo "ERROR: unsupported MODE=$MODE" >&2
    exit 2
    ;;
esac

REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
CAMPAIGN_ID=full6f_365gev_ee_ttbar_spinpol_v1

SOURCE_CARD="$REPO/sindarin/generated/$CAMPAIGN_ID/f6f365_ee_LR100_epmum/epmum/process.sin"
SOURCE_CARD="$(readlink -f "$SOURCE_CARD")"
SOURCE_DIR="$(dirname "$SOURCE_CARD")"
SOURCE_COMMON="$SOURCE_DIR/common"
SOURCE_CONTEXT="$SOURCE_DIR/render_context.json"

SEED=1885084773
ITERATIONS='5:50000:"gw",5:100000:""'

echo "============================================================"
echo "PHASE11_CANDIDATE_A_STRESS_V1_G1_S2"
echo "MODE=$MODE"
echo "INTEGRATION_METHOD=$INTEGRATION_METHOD"
echo "SEED=$SEED"
echo "ITERATIONS=$ITERATIONS"
echo "SOURCE_CARD=$SOURCE_CARD"
echo "SOURCE_DIR=$SOURCE_DIR"
echo "SOURCE_COMMON=$SOURCE_COMMON"
echo "SOURCE_CONTEXT=$SOURCE_CONTEXT"
echo "PREFLIGHT_ONLY=$PREFLIGHT_ONLY"
echo "HOST=$(hostname -f 2>/dev/null || hostname)"
echo "============================================================"

#
# 1. Validate canonical source dependencies.
#
for required_path in \
  "$SOURCE_CARD" \
  "$SOURCE_COMMON" \
  "$SOURCE_CONTEXT" \
  "$SOURCE_COMMON/model.inc" \
  "$SOURCE_COMMON/beams.inc" \
  "$SOURCE_COMMON/isr.inc" \
  "$SOURCE_COMMON/polarization.inc" \
  "$SOURCE_COMMON/integration.inc" \
  "$SOURCE_COMMON/event_output.inc"
do
  if [[ ! -e "$required_path" ]]; then
    echo "ERROR: missing source dependency: $required_path" >&2
    exit 3
  fi
done

echo "SOURCE_DEPENDENCIES=PASS"

#
# 2. Load the same qualified custom WHIZARD 3.1.8 build for D1 and D2.
#
set +u
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"
set -u

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

WHIZARD_BIN="$(command -v whizard)"
WHIZARD_REALPATH="$(readlink -f "$WHIZARD_BIN")"

EXPECTED_ROOT="$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811"

case "$WHIZARD_REALPATH" in
  "$EXPECTED_ROOT"/*)
    echo "QUALIFIED_WHIZARD_PATH_CHECK=PASS"
    ;;
  *)
    echo "ERROR: unexpected WHIZARD binary: $WHIZARD_REALPATH" >&2
    exit 4
    ;;
esac

echo "WHIZARD_REALPATH=$WHIZARD_REALPATH"
whizard --version | sed -n '1p'

#
# 3. Create isolated scratch area.
#
if [[ -n "${_CONDOR_SCRATCH_DIR:-}" ]]; then
  SCRATCH_BASE="$_CONDOR_SCRATCH_DIR"
elif [[ -n "${TMPDIR:-}" ]]; then
  SCRATCH_BASE="$TMPDIR"
else
  SCRATCH_BASE="/tmp/${USER:-unknown}"
fi

mkdir -p "$SCRATCH_BASE"

WORK="$(mktemp -d "$SCRATCH_BASE/d1d2_${MODE}_XXXXXX")"

cleanup() {
  local rc=$?
  if [[ "${KEEP_D1D2_SCRATCH:-0}" == "1" ]]; then
    echo "KEEPING_SCRATCH=$WORK"
  else
    rm -rf -- "$WORK"
  fi
  exit "$rc"
}
trap cleanup EXIT

echo "WORK=$WORK"

#
# 4. Use the proven production staging pattern.
#
cp -a "$SOURCE_CARD" "$WORK/process.sin"
cp -a "$SOURCE_COMMON" "$WORK/common"
cp -a "$SOURCE_CONTEXT" "$WORK/render_context.json"

test -s "$WORK/process.sin" || {
  echo "ERROR: staged process.sin missing/empty" >&2
  exit 5
}

test -d "$WORK/common" || {
  echo "ERROR: staged common directory missing" >&2
  exit 6
}

test -s "$WORK/render_context.json" || {
  echo "ERROR: staged render_context.json missing/empty" >&2
  exit 7
}

echo "PROCESS_SIN_COPY=PASS"
echo "COMMON_COPY=PASS"
echo "CONTEXT_COPY=PASS"

#
# 5. Localize generated-tree includes, matching the production worker contract.
#
python3 - "$WORK/process.sin" "$SOURCE_COMMON" <<'PY_LOCALIZE'
from pathlib import Path
import re
import sys

card = Path(sys.argv[1])
source_common = str(Path(sys.argv[2]).resolve())

text = card.read_text(encoding="utf-8")

pattern = re.compile(
    r'include\("' + re.escape(source_common) + r'/([^"]+)"\)'
)

matches = pattern.findall(text)

required = {
    "model.inc",
    "beams.inc",
    "isr.inc",
    "polarization.inc",
    "integration.inc",
    "event_output.inc",
}

if not matches:
    raise SystemExit(
        "ERROR: no generated-tree common includes found"
    )

missing = sorted(required - set(matches))
if missing:
    raise SystemExit(
        "ERROR: source process card lacks required includes: "
        + ",".join(missing)
    )

text, count = pattern.subn(
    lambda m: f'include("common/{m.group(1)}")',
    text,
)

card.write_text(text, encoding="utf-8")

print("LOCALIZED_COMMON_INCLUDES=" + ",".join(matches))
print(f"LOCALIZED_COMMON_INCLUDE_COUNT={count}")
PY_LOCALIZE

#
# 6. Install diagnostic-specific integration configuration.
#
if [[ "$INTEGRATION_METHOD" == "vamp2" ]]; then
  cat > "$WORK/common/integration.inc" <<'SIN'
$integration_method = "vamp2"
$rng_method = "rng_stream"
$vamp_parallel_method = "simple"

?omega_openmp = false
openmp_num_threads = 1

seed = 1885084773

iterations = 5:50000:"gw",5:100000:""

integrate (proc_epmum)
SIN
else
  cat > "$WORK/common/integration.inc" <<'SIN'
$integration_method = "vamp"
$rng_method = "rng_stream"

?omega_openmp = false
openmp_num_threads = 1

seed = 1885084773

iterations = 5:50000:"gw",5:100000:""

integrate (proc_epmum)
SIN
fi

#
# Integration-only diagnostic.
#
# There is no simulate command in D1/D2.  Remove the event-output include
# entirely rather than asking WHIZARD to parse an empty included file.
#
python3 - "$WORK/process.sin" <<'PY_REMOVE_EVENT_OUTPUT'
from pathlib import Path
import re
import sys

card = Path(sys.argv[1])
text = card.read_text(encoding="utf-8")

pattern = re.compile(
    r'(?m)^[ \t]*include\("common/event_output\.inc"\)[ \t]*(?:\r?\n|$)'
)

text, count = pattern.subn("", text)

if count != 1:
    raise SystemExit(
        f"ERROR: expected exactly one event_output.inc include, found {count}"
    )

card.write_text(text, encoding="utf-8")

print("EVENT_OUTPUT_INCLUDE_REMOVED=PASS")
PY_REMOVE_EVENT_OUTPUT

#
# 7. Validate the effective localized card.
#
python3 - "$WORK/process.sin" "$WORK/common" <<'PY_VALIDATE'
from pathlib import Path
import re
import sys

process = Path(sys.argv[1])
common = Path(sys.argv[2])

text = process.read_text(encoding="utf-8")

includes = re.findall(
    r'include\("common/([^"]+)"\)',
    text,
)

required = {
    "model.inc",
    "beams.inc",
    "isr.inc",
    "polarization.inc",
    "integration.inc",
}

if "event_output.inc" in includes:
    raise SystemExit(
        "ERROR: event_output.inc remains included in integration-only card"
    )

missing_markers = sorted(required - set(includes))
missing_files = sorted(
    name for name in includes
    if not (common / name).is_file()
)

if missing_markers:
    raise SystemExit(
        "ERROR: missing local include markers: "
        + ",".join(missing_markers)
    )

if missing_files:
    raise SystemExit(
        "ERROR: missing localized include files: "
        + ",".join(missing_files)
    )

if "/sindarin/generated/" in text:
    raise SystemExit(
        "ERROR: absolute generated-tree include remains"
    )

print("LOCAL_INCLUDES=" + ",".join(includes))
print("LOCALIZED_CARD_CONTRACT=PASS")
PY_VALIDATE

if grep -Fq 'include("common/event_output.inc")' "$WORK/process.sin"; then
  echo "ERROR: event_output.inc remains included" >&2
  exit 8
fi

echo "EVENT_GENERATION_DISABLED=PASS"

echo
echo "=== EFFECTIVE integration.inc ==="
cat "$WORK/common/integration.inc"

echo
echo "=== EFFECTIVE process includes ==="
grep -n 'include(' "$WORK/process.sin"

#
# 8. Preflight mode ends HERE.
#
if [[ "$PREFLIGHT_ONLY" -eq 1 ]]; then
  echo "PREFLIGHT_ONLY=PASS"
  exit 0
fi

#
# 9. Establish persistent output only for the real diagnostic.
#
JOB_OUT="$OUT_ROOT/$MODE"
mkdir -p "$JOB_OUT"

cp -a "$WORK/process.sin" "$JOB_OUT/effective_process.sin"
cp -a "$WORK/common" "$JOB_OUT/effective_common"
cp -a "$WORK/render_context.json" "$JOB_OUT/render_context.json"

START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
START_EPOCH="$(date +%s)"

echo "START_UTC=$START_UTC"
echo "MPI_RANKS=1"
echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "EXECUTION_START=1"

cd "$WORK"

set +e

mpirun \
  -np 1 \
  --nooversubscribe \
  --bind-to core \
  --map-by core \
  "$WHIZARD_REALPATH" process.sin \
  2>&1 | tee "$WORK/console.log"

WHIZARD_RC=${PIPESTATUS[0]}

set -e

END_EPOCH="$(date +%s)"
END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
WALL_SECONDS=$((END_EPOCH - START_EPOCH))

cp -a "$WORK/console.log" "$JOB_OUT/console.log"

#
# 10. Archive the final integration workspace/grid products.
#
find "$WORK" \
  -maxdepth 3 \
  -type f \
  \( \
    -name '*.vg2' \
    -o -name '*.phs' \
  \) \
  -printf '%P\n' \
  | sort \
  > "$JOB_OUT/integration_artifacts.list"

if [[ -s "$JOB_OUT/integration_artifacts.list" ]]; then
  (
    cd "$WORK"
    tar -czf "$JOB_OUT/integration_artifacts.tar.gz" \
      -T "$JOB_OUT/integration_artifacts.list"
  )
fi

#
# 11. Metadata.
#
python3 - \
  "$JOB_OUT/metadata.json" \
  "$MODE" \
  "$INTEGRATION_METHOD" \
  "$SEED" \
  "$ITERATIONS" \
  "$WHIZARD_REALPATH" \
  "$WHIZARD_RC" \
  "$WALL_SECONDS" \
  "$START_UTC" \
  "$END_UTC" <<'PY_META'
import json
import os
import socket
import sys

(
    out,
    mode,
    method,
    seed,
    iterations,
    whizard,
    rc,
    wall,
    start,
    end,
) = sys.argv[1:]

def _coerce_job_id(value):
    if value is None:
        return None

    value = str(value).strip()

    if (
        len(value) >= 2
        and value[0] == '"'
        and value[-1] == '"'
    ):
        value = value[1:-1]

    try:
        return int(value)
    except ValueError:
        return value


def _read_condor_job_ad():
    values = {}

    path = os.environ.get("_CONDOR_JOB_AD")

    if not path or not os.path.isfile(path):
        return values

    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                lhs, sep, rhs = raw.partition("=")

                if not sep:
                    continue

                key = lhs.strip()

                if key not in {"ClusterId", "ProcId"}:
                    continue

                values[key] = _coerce_job_id(rhs.strip())

    except OSError:
        pass

    return values


job_ad = _read_condor_job_ad()

condor_cluster_id = _coerce_job_id(
    os.environ.get("ClusterId")
)

condor_proc_id = _coerce_job_id(
    os.environ.get("ProcId")
)

if condor_cluster_id is None:
    condor_cluster_id = job_ad.get("ClusterId")

if condor_proc_id is None:
    condor_proc_id = job_ad.get("ProcId")


payload = {
    "diagnostic": "phase11_candidate_A_stress_v1",
    "worker_version": "candidate_A_stress_v1/G1_S2",
    "mode": mode,
    "integration_method": method,
    "mpi_ranks": 1,
    "omp_threads": 1,
    "rng_method": "rng_stream",
    "seed": int(seed),
    "iterations": iterations,
    "event_generation": False,
    "whizard_binary": whizard,
    "whizard_rc": int(rc),
    "wall_seconds": int(wall),
    "start_utc": start,
    "end_utc": end,
    "host": socket.getfqdn(),
    "condor_cluster_id": condor_cluster_id,
    "condor_proc_id": condor_proc_id,
    "execution_status": "PASS" if int(rc) == 0 else "FAIL",
    "integration_status": "UNASSESSED",
    "integration_status_semantics": "post_run_qualification_required",
    "success_marker_semantics": "execution_only",
}

tmp = out + ".tmp"

with open(tmp, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, sort_keys=True)
    f.write("\n")

os.replace(tmp, out)
PY_META

(
  cd "$JOB_OUT"

  sha256sum \
    effective_process.sin \
    effective_common/integration.inc \
    effective_common/event_output.inc \
    render_context.json \
    console.log \
    metadata.json \
    > SHA256SUMS.txt

  if [[ -f integration_artifacts.tar.gz ]]; then
    sha256sum integration_artifacts.tar.gz \
      >> SHA256SUMS.txt
  fi
)

if [[ "$WHIZARD_RC" -eq 0 ]]; then
  touch "$JOB_OUT/SUCCESS"
  touch "$JOB_OUT/EXECUTION_SUCCESS"
  EXECUTION_STATUS="PASS"
else
  touch "$JOB_OUT/FAILED"
  touch "$JOB_OUT/EXECUTION_FAILED"
  EXECUTION_STATUS="FAIL"
fi

echo "WHIZARD_RC=$WHIZARD_RC"
echo "EXECUTION_STATUS=$EXECUTION_STATUS"
echo "INTEGRATION_STATUS=UNASSESSED"
echo "WALL_SECONDS=$WALL_SECONDS"
echo "END_UTC=$END_UTC"
echo "JOB_OUT=$JOB_OUT"
echo "DIAGNOSTIC_COMPLETE=1"

exit "$WHIZARD_RC"
