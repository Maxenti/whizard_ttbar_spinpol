#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF_USAGE'
Usage:
  run_full6f_production_job.sh \
    --repo PATH \
    --campaign-id ID \
    --sample-id ID \
    --subprocess-id ID \
    --source-card PATH \
    --shard-index N \
    --whizard-seed N \
    --events N \
    --iterations SPEC \
    --campaign-root PATH \
    --archive-workspace 0|1 \
    --timeout-minutes N \
    [--mpi-ranks N] \
    [--vamp-parallel-method simple|load]

Defaults:
  --mpi-ranks 1
  --vamp-parallel-method simple

mpi-ranks=1 preserves the historical serial production path.

mpi-ranks>1 selects the qualified WHIZARD 3.1.8 MPI runtime and delegates
MPI/VAMP2 execution to run_full6f_production_shard.sh.
EOF_USAGE
}

REPO=""
CAMPAIGN_ID=""
SAMPLE_ID=""
SUBPROCESS_ID=""
SOURCE_CARD=""
SHARD_INDEX=""
WHIZARD_SEED=""
EVENTS=""
ITERATIONS=""
CAMPAIGN_ROOT=""
ARCHIVE_WORKSPACE=""
TIMEOUT_MINUTES=""

MPI_RANKS=1
VAMP_PARALLEL_METHOD="simple"

while (($#)); do
  case "$1" in
    --repo)
      REPO=${2:?}
      shift 2
      ;;
    --campaign-id)
      CAMPAIGN_ID=${2:?}
      shift 2
      ;;
    --sample-id)
      SAMPLE_ID=${2:?}
      shift 2
      ;;
    --subprocess-id)
      SUBPROCESS_ID=${2:?}
      shift 2
      ;;
    --source-card)
      SOURCE_CARD=${2:?}
      shift 2
      ;;
    --shard-index)
      SHARD_INDEX=${2:?}
      shift 2
      ;;
    --whizard-seed)
      WHIZARD_SEED=${2:?}
      shift 2
      ;;
    --events)
      EVENTS=${2:?}
      shift 2
      ;;
    --iterations)
      ITERATIONS=${2:?}
      shift 2
      ;;
    --campaign-root)
      CAMPAIGN_ROOT=${2:?}
      shift 2
      ;;
    --archive-workspace)
      ARCHIVE_WORKSPACE=${2:?}
      shift 2
      ;;
    --timeout-minutes)
      TIMEOUT_MINUTES=${2:?}
      shift 2
      ;;
    --mpi-ranks)
      MPI_RANKS=${2:?}
      shift 2
      ;;
    --vamp-parallel-method)
      VAMP_PARALLEL_METHOD=${2:?}
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

for variable in \
  REPO \
  CAMPAIGN_ID \
  SAMPLE_ID \
  SUBPROCESS_ID \
  SOURCE_CARD \
  SHARD_INDEX \
  WHIZARD_SEED \
  EVENTS \
  ITERATIONS \
  CAMPAIGN_ROOT \
  ARCHIVE_WORKSPACE \
  TIMEOUT_MINUTES
do
  if [[ -z "${!variable}" ]]; then
    echo "ERROR: missing $variable" >&2
    exit 2
  fi
done

if [[ ! "$MPI_RANKS" =~ ^[0-9]+$ ]] || (( MPI_RANKS < 1 )); then
  echo "ERROR: --mpi-ranks must be a positive integer: $MPI_RANKS" >&2
  exit 2
fi

case "$VAMP_PARALLEL_METHOD" in
  simple|load)
    ;;
  *)
    echo \
      "ERROR: --vamp-parallel-method must be simple or load: " \
      "$VAMP_PARALLEL_METHOD" >&2
    exit 2
    ;;
esac

cd "$REPO" || {
  echo "ERROR: cannot enter repository: $REPO" >&2
  exit 1
}

SERIAL_SETUP="$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh"
MPI_SETUP="$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

WORKER="$REPO/scripts/production/run_full6f_production_shard.sh"

if (( MPI_RANKS > 1 )); then
  SETUP="$MPI_SETUP"
  EXECUTION_MODE="mpi_vamp2"
else
  SETUP="$SERIAL_SETUP"
  EXECUTION_MODE="serial"
fi

[[ -s "$SETUP" ]] || {
  echo "ERROR: missing runtime setup: $SETUP" >&2
  exit 1
}

[[ -x "$WORKER" ]] || {
  echo "ERROR: missing worker: $WORKER" >&2
  exit 1
}

# Some CVMFS setup scripts reference unset variables internally.
set +u
source "$SETUP"
set -u

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

if (( MPI_RANKS > 1 )); then
  command -v mpirun >/dev/null 2>&1 || {
    echo "ERROR: MPI execution requested but mpirun is unavailable" >&2
    exit 1
  }

  if [[ -z "${WHIZARD_MPI_ROOT:-}" ]]; then
    echo "ERROR: MPI runtime setup did not define WHIZARD_MPI_ROOT" >&2
    exit 1
  fi

  EXPECTED_MPI_ROOT="$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811"

  if [[ "$WHIZARD_MPI_ROOT" != "$EXPECTED_MPI_ROOT" ]]; then
    echo "ERROR: unexpected WHIZARD_MPI_ROOT" >&2
    echo "Expected: $EXPECTED_MPI_ROOT" >&2
    echo "Observed: $WHIZARD_MPI_ROOT" >&2
    exit 1
  fi
fi

echo "============================================================"
echo "FULL6F_CONDOR_JOB"
echo "HOST=$(hostname -f 2>/dev/null || hostname)"
echo "CONDOR_CLUSTER=${ClusterId:-UNSET}"
echo "CONDOR_PROCESS=${ProcId:-UNSET}"
echo "_CONDOR_SCRATCH_DIR=${_CONDOR_SCRATCH_DIR:-UNSET}"
echo "CAMPAIGN_ID=$CAMPAIGN_ID"
echo "SAMPLE_ID=$SAMPLE_ID"
echo "SUBPROCESS_ID=$SUBPROCESS_ID"
echo "SHARD_INDEX=$SHARD_INDEX"
echo "WHIZARD_SEED=$WHIZARD_SEED"
echo "EVENTS=$EVENTS"
echo "ITERATIONS=$ITERATIONS"
echo "CAMPAIGN_ROOT=$CAMPAIGN_ROOT"
echo "EXECUTION_MODE=$EXECUTION_MODE"
echo "MPI_RANKS=$MPI_RANKS"
echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "VAMP_PARALLEL_METHOD=$VAMP_PARALLEL_METHOD"
echo "WHIZARD=$(command -v whizard)"
echo "MPIRUN=$(command -v mpirun 2>/dev/null || true)"
echo "WHIZARD_MPI_ROOT=${WHIZARD_MPI_ROOT:-UNSET}"
whizard --version | sed -n '1p'
echo "============================================================"

exec "$WORKER" \
  --campaign-id "$CAMPAIGN_ID" \
  --sample-id "$SAMPLE_ID" \
  --subprocess-id "$SUBPROCESS_ID" \
  --source-card "$SOURCE_CARD" \
  --shard-index "$SHARD_INDEX" \
  --whizard-seed "$WHIZARD_SEED" \
  --events "$EVENTS" \
  --iterations "$ITERATIONS" \
  --campaign-root "$CAMPAIGN_ROOT" \
  --archive-workspace "$ARCHIVE_WORKSPACE" \
  --timeout-minutes "$TIMEOUT_MINUTES" \
  --mpi-ranks "$MPI_RANKS" \
  --vamp-parallel-method "$VAMP_PARALLEL_METHOD"
