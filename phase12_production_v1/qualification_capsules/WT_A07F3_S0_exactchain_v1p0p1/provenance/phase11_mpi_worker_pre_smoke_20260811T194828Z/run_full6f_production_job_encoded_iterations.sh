#!/usr/bin/env bash

set -Eeuo pipefail

###############################################################################
# Thin transport wrapper around the authoritative full6f worker.
#
# Integration schedules contain commas and quotes, e.g.
#
#   5:50000:"gw",5:100000:""
#
# They are transported through HTCondor as lowercase hexadecimal and decoded
# here before invoking run_full6f_production_job.sh.
#
# MPI options are ordinary scalar fields and do not require encoding.
###############################################################################

decode_hex() {
    local encoded="$1"

    python3 - "$encoded" <<'PY'
import sys

encoded = sys.argv[1]

if not encoded:
    raise SystemExit("ERROR: empty hexadecimal integration schedule")

try:
    raw = bytes.fromhex(encoded)
except ValueError as exc:
    raise SystemExit(
        f"ERROR: invalid hexadecimal integration schedule: {exc}"
    )

try:
    text = raw.decode("utf-8")
except UnicodeDecodeError as exc:
    raise SystemExit(
        f"ERROR: integration schedule is not valid UTF-8: {exc}"
    )

print(text)
PY
}

###############################################################################
# Diagnostic decode mode.
###############################################################################

if [[ "${1:-}" == "--decode-only" ]]; then
    if (( $# != 2 )); then
        echo "Usage: $0 --decode-only HEX" >&2
        exit 64
    fi

    decode_hex "$2"
    exit 0
fi

###############################################################################
# Parse arguments.
###############################################################################

REPO=""
CAMPAIGN_ID=""
SAMPLE_ID=""
SUBPROCESS_ID=""
SOURCE_CARD=""
SHARD_INDEX=""
WHIZARD_SEED=""
EVENTS=""
ITERATIONS_HEX=""
CAMPAIGN_ROOT=""
ARCHIVE_WORKSPACE=""
TIMEOUT_MINUTES=""

MPI_RANKS=1
VAMP_PARALLEL_METHOD="simple"

while (( $# > 0 )); do
    case "$1" in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --campaign-id)
            CAMPAIGN_ID="$2"
            shift 2
            ;;
        --sample-id)
            SAMPLE_ID="$2"
            shift 2
            ;;
        --subprocess-id)
            SUBPROCESS_ID="$2"
            shift 2
            ;;
        --source-card)
            SOURCE_CARD="$2"
            shift 2
            ;;
        --shard-index)
            SHARD_INDEX="$2"
            shift 2
            ;;
        --whizard-seed)
            WHIZARD_SEED="$2"
            shift 2
            ;;
        --events)
            EVENTS="$2"
            shift 2
            ;;
        --iterations-hex)
            ITERATIONS_HEX="$2"
            shift 2
            ;;
        --campaign-root)
            CAMPAIGN_ROOT="$2"
            shift 2
            ;;
        --archive-workspace)
            ARCHIVE_WORKSPACE="$2"
            shift 2
            ;;
        --timeout-minutes)
            TIMEOUT_MINUTES="$2"
            shift 2
            ;;
        --mpi-ranks)
            MPI_RANKS="$2"
            shift 2
            ;;
        --vamp-parallel-method)
            VAMP_PARALLEL_METHOD="$2"
            shift 2
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 64
            ;;
    esac
done

###############################################################################
# Required transport fields.
###############################################################################

declare -A REQUIRED_VALUES=(
    [REPO]="$REPO"
    [CAMPAIGN_ID]="$CAMPAIGN_ID"
    [SAMPLE_ID]="$SAMPLE_ID"
    [SUBPROCESS_ID]="$SUBPROCESS_ID"
    [SOURCE_CARD]="$SOURCE_CARD"
    [SHARD_INDEX]="$SHARD_INDEX"
    [WHIZARD_SEED]="$WHIZARD_SEED"
    [EVENTS]="$EVENTS"
    [ITERATIONS_HEX]="$ITERATIONS_HEX"
    [CAMPAIGN_ROOT]="$CAMPAIGN_ROOT"
    [ARCHIVE_WORKSPACE]="$ARCHIVE_WORKSPACE"
    [TIMEOUT_MINUTES]="$TIMEOUT_MINUTES"
)

for key in "${!REQUIRED_VALUES[@]}"; do
    if [[ -z "${REQUIRED_VALUES[$key]}" ]]; then
        echo "ERROR: required argument is empty: $key" >&2
        exit 64
    fi
done

if [[ ! "$MPI_RANKS" =~ ^[0-9]+$ ]] || (( MPI_RANKS < 1 )); then
    echo "ERROR: invalid MPI rank count: $MPI_RANKS" >&2
    exit 64
fi

case "$VAMP_PARALLEL_METHOD" in
    simple|load)
        ;;
    *)
        echo \
            "ERROR: invalid VAMP parallel method: " \
            "$VAMP_PARALLEL_METHOD" >&2
        exit 64
        ;;
esac

###############################################################################
# Decode integration schedule.
###############################################################################

if [[ ! "$ITERATIONS_HEX" =~ ^[0-9A-Fa-f]+$ ]]; then
    echo "ERROR: --iterations-hex contains non-hexadecimal characters." >&2
    echo "VALUE=$ITERATIONS_HEX" >&2
    exit 64
fi

if (( ${#ITERATIONS_HEX} % 2 != 0 )); then
    echo "ERROR: --iterations-hex has odd length." >&2
    exit 64
fi

INTEGRATION_ITERATIONS="$(decode_hex "$ITERATIONS_HEX")"

if [[ -z "$INTEGRATION_ITERATIONS" ]]; then
    echo "ERROR: decoded integration schedule is empty." >&2
    exit 64
fi

echo "ENCODED_ITERATION_TRANSPORT=1"
echo "INTEGRATION_ITERATIONS_HEX=$ITERATIONS_HEX"
echo "INTEGRATION_ITERATIONS_DECODED=$INTEGRATION_ITERATIONS"
echo "MPI_RANKS=$MPI_RANKS"
echo "VAMP_PARALLEL_METHOD=$VAMP_PARALLEL_METHOD"

###############################################################################
# Delegate to authoritative worker.
###############################################################################

AUTHORITATIVE_WORKER="$REPO/scripts/condor/run_full6f_production_job.sh"

if [[ ! -x "$AUTHORITATIVE_WORKER" ]]; then
    echo "ERROR: authoritative worker is missing/not executable:" >&2
    echo "  $AUTHORITATIVE_WORKER" >&2
    exit 66
fi

exec "$AUTHORITATIVE_WORKER" \
    --repo "$REPO" \
    --campaign-id "$CAMPAIGN_ID" \
    --sample-id "$SAMPLE_ID" \
    --subprocess-id "$SUBPROCESS_ID" \
    --source-card "$SOURCE_CARD" \
    --shard-index "$SHARD_INDEX" \
    --whizard-seed "$WHIZARD_SEED" \
    --events "$EVENTS" \
    --iterations "$INTEGRATION_ITERATIONS" \
    --campaign-root "$CAMPAIGN_ROOT" \
    --archive-workspace "$ARCHIVE_WORKSPACE" \
    --timeout-minutes "$TIMEOUT_MINUTES" \
    --mpi-ranks "$MPI_RANKS" \
    --vamp-parallel-method "$VAMP_PARALLEL_METHOD"
