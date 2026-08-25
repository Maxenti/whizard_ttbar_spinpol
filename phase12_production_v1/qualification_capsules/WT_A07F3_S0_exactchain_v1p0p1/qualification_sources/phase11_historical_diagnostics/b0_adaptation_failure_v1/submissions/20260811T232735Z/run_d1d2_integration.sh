#!/usr/bin/env bash
set -u
set -o pipefail

MODE="${1:?missing MODE}"
OUT_ROOT="${2:?missing OUT_ROOT}"

REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
CAMPAIGN_ID=full6f_365gev_ee_ttbar_spinpol_v1

CANON_ROOT="$REPO/sindarin/generated/$CAMPAIGN_ID/f6f365_ee_LR100_epmum"

SEED=1740114216
ITERATIONS='10:100000:"gw",2:200000:""'

if [[ ! -d "$CANON_ROOT" ]]; then
  echo "ERROR: canonical sample root does not exist: $CANON_ROOT" >&2
  exit 3
fi

mapfile -t PROCESS_CANDIDATES < <(
  find -L "$CANON_ROOT" \
    -maxdepth 5 \
    -type f \
    -name 'process.sin' \
    -print \
  | sort
)

if [[ "${#PROCESS_CANDIDATES[@]}" -ne 1 ]]; then
  echo "ERROR: expected exactly one resolvable process.sin under:" >&2
  echo "  $CANON_ROOT" >&2
  echo "Found ${#PROCESS_CANDIDATES[@]} candidates:" >&2
  printf '  %s\n' "${PROCESS_CANDIDATES[@]}" >&2
  exit 3
fi

PROCESS_SOURCE="${PROCESS_CANDIDATES[0]}"
BASE="$(dirname "$PROCESS_SOURCE")"

case "$MODE" in
  D1_vamp2_np1)
    INTEGRATION_METHOD="vamp2"
    ;;
  D2_vamp_np1)
    INTEGRATION_METHOD="vamp"
    ;;
  *)
    echo "ERROR: unknown MODE=$MODE" >&2
    exit 2
    ;;
esac

echo "============================================================"
echo "PHASE11_B0_ADAPTATION_DIAGNOSTIC"
echo "MODE=$MODE"
echo "HOST=$(hostname -f)"
echo "REPO=$REPO"
echo "CANON_ROOT=$CANON_ROOT"
echo "PROCESS_SOURCE=$PROCESS_SOURCE"
echo "BASE=$BASE"
echo "SEED=$SEED"
echo "ITERATIONS=$ITERATIONS"
echo "INTEGRATION_METHOD=$INTEGRATION_METHOD"
echo "_CONDOR_SCRATCH_DIR=${_CONDOR_SCRATCH_DIR:-UNSET}"
echo "============================================================"


# Use the SAME qualified custom WHIZARD binary for both tests.
# This keeps the executable/build fixed and isolates VAMP vs VAMP2.
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

WHIZARD_BIN="$(command -v whizard)"
WHIZARD_REALPATH="$(readlink -f "$WHIZARD_BIN")"

echo "WHIZARD_BIN=$WHIZARD_BIN"
echo "WHIZARD_REALPATH=$WHIZARD_REALPATH"
whizard --version | head -5

EXPECTED_ROOT="$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811"

case "$WHIZARD_REALPATH" in
  "$EXPECTED_ROOT"/*)
    echo "QUALIFIED_WHIZARD_PATH_CHECK=PASS"
    ;;
  *)
    echo "ERROR: unexpected WHIZARD binary:" >&2
    echo "  $WHIZARD_REALPATH" >&2
    exit 4
    ;;
esac

SCRATCH_BASE="${_CONDOR_SCRATCH_DIR:-/tmp}"
WORK="$SCRATCH_BASE/phase11_b0_diag_${MODE}_$$"

rm -rf "$WORK"
mkdir -p "$WORK"

# Dereference generated-card symlinks while staging into Condor scratch.
# This makes the scratch tree self-contained and prevents relative
# generated-card symlinks from becoming dangling after relocation.
cp -aL "$BASE"/. "$WORK"/

if [[ ! -f "$WORK/process.sin" ]]; then
  echo "ERROR: process.sin missing after copy" >&2
  exit 5
fi

if [[ ! -d "$WORK/common" ]]; then
  echo "ERROR: common/ missing after copy" >&2
  exit 6
fi

#
# Replace ONLY the integration configuration and disable simulation.
#
if [[ "$MODE" == "D1_vamp2_np1" ]]; then
  cat > "$WORK/common/integration.inc" <<'SIN'
$integration_method = "vamp2"
$rng_method = "rng_stream"
$vamp_parallel_method = "simple"
?omega_openmp = false
openmp_num_threads = 1

seed = 1740114216
iterations = 10:100000:"gw",2:200000:""
integrate (proc_epmum)
SIN
else
  cat > "$WORK/common/integration.inc" <<'SIN'
$integration_method = "vamp"
$rng_method = "rng_stream"
?omega_openmp = false
openmp_num_threads = 1

seed = 1740114216
iterations = 10:100000:"gw",2:200000:""
integrate (proc_epmum)
SIN
fi

# Integration-only diagnostic.  No simulate() call.
: > "$WORK/common/event_output.inc"

echo
echo "=== EFFECTIVE integration.inc ==="
cat "$WORK/common/integration.inc"

echo
echo "=== EFFECTIVE event_output.inc ==="
wc -c "$WORK/common/event_output.inc"

JOB_OUT="$OUT_ROOT/$MODE"
mkdir -p "$JOB_OUT"

cp "$WORK/process.sin" \
   "$JOB_OUT/process.sin"

cp "$WORK/common/integration.inc" \
   "$JOB_OUT/integration.inc"

cp "$WORK/common/event_output.inc" \
   "$JOB_OUT/event_output.inc"

START_EPOCH=$(date +%s)
START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo
echo "START_UTC=$START_UTC"
echo "Running one-rank diagnostic..."
echo

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

END_EPOCH=$(date +%s)
END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
WALL_SECONDS=$((END_EPOCH - START_EPOCH))

echo
echo "WHIZARD_RC=$WHIZARD_RC"
echo "WALL_SECONDS=$WALL_SECONDS"
echo "END_UTC=$END_UTC"

cp "$WORK/console.log" \
   "$JOB_OUT/console.log"

#
# Preserve integration products.
#
cd "$WORK"

find . -type f \
  \( \
     -name '*.vg2' \
     -o -name '*.phs' \
     -o -name '*.log' \
  \) \
  -print \
  | sort \
  > "$JOB_OUT/integration_artifacts.list"

if [[ -s "$JOB_OUT/integration_artifacts.list" ]]; then
  tar -czf "$JOB_OUT/integration_artifacts.tar.gz" \
    -T "$JOB_OUT/integration_artifacts.list"
fi

#
# Machine-readable metadata via Python.
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
  "$END_UTC" <<'PY'
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

payload = {
    "diagnostic": "phase11_b0_adaptation_failure_v1",
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
    "condor_cluster_id": os.environ.get("ClusterId"),
    "condor_proc_id": os.environ.get("ProcId"),
}

tmp = out + ".tmp"
with open(tmp, "w") as f:
    json.dump(payload, f, indent=2, sort_keys=True)
    f.write("\n")

os.replace(tmp, out)
PY

(
  cd "$JOB_OUT"
  sha256sum \
    process.sin \
    integration.inc \
    event_output.inc \
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
else
  touch "$JOB_OUT/FAILED"
fi

echo
echo "JOB_OUT=$JOB_OUT"
echo "WHIZARD_RC=$WHIZARD_RC"
echo "DIAGNOSTIC_COMPLETE=1"

exit "$WHIZARD_RC"
