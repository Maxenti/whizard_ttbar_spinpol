#!/usr/bin/env bash

set -Eeuo pipefail
set -o pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 RUN_TAG"
    exit 2
fi

RUN_TAG="$1"

export REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
export PKG="$REPO/mpi_qualification/full6f_365gev_load_balance_v1"

export SOURCE="$PKG/benchmark_source"

export EOS_BASE=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/mpi_qualification/full6f_365gev_load_balance_v1
export EOS_RUN="$EOS_BASE/$RUN_TAG"

SCRATCH_BASE="${_CONDOR_SCRATCH_DIR:-${TMPDIR:-/tmp/${USER}/whizard_load_${RUN_TAG}}}"

mkdir -p \
    "$EOS_RUN" \
    "$EOS_RUN/provenance" \
    "$SCRATCH_BASE"

source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1

{
    echo "RUN_TAG=$RUN_TAG"
    echo "START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "HOST=$(hostname)"
    echo "WHIZARD=$WHIZARD_MPI_ROOT/bin/whizard"
    echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
    echo
    lscpu || true
} > "$EOS_RUN/provenance/runtime.txt"

RANKS_LIST=(8 16)

for N in "${RANKS_LIST[@]}"; do

    echo
    echo "================================================================"
    echo "VAMP2 LOAD BALANCING: NP=$N"
    echo "================================================================"

    WORK="$SCRATCH_BASE/np${N}"
    OUT="$EOS_RUN/np${N}"

    rm -rf "$WORK"
    mkdir -p "$WORK" "$OUT"

    cp -a "$SOURCE/." "$WORK/"

    cd "$WORK"

    set +e
    set -o pipefail

    /usr/bin/time \
        -o time.txt \
        -f 'WALL_SECONDS=%e
USER_SECONDS=%U
SYS_SECONDS=%S
MAX_RSS_KB=%M
EXIT_CODE=%x' \
        mpirun \
            -np "$N" \
            --bind-to core \
            --map-by core \
            "$WHIZARD_MPI_ROOT/bin/whizard" \
            process.sin \
        2>&1 \
        | tee run.log

    RC=${PIPESTATUS[0]}

    set -e

    echo "$RC" > return_code.txt

    grep -E \
        '^[[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9.Ee+-]+' \
        run.log \
        | tail -1 \
        > final_integration_row.txt \
        || true

    grep -E \
        'MPI: Using|MPI: master|MPI: slave|Integrator: VAMP2|VAMP2: .*Request Balancing|WHIZARD run finished' \
        run.log \
        > runtime_markers.txt \
        || true

    cp -a \
        process.sin \
        common \
        run.log \
        whizard.log \
        time.txt \
        return_code.txt \
        final_integration_row.txt \
        runtime_markers.txt \
        "$OUT/" \
        2>/dev/null || true

    echo
    echo "NP=$N"
    cat time.txt
    cat final_integration_row.txt || true

    if [[ "$RC" -ne 0 ]]; then
        {
            echo "STATUS=FAIL"
            echo "FAILED_NP=$N"
            echo "RC=$RC"
        } > "$EOS_RUN/STATUS.txt"

        exit "$RC"
    fi
done

{
    echo "STATUS=PASS"
    echo "BALANCING=load"
    echo "RANKS=8,16"
    echo "END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$EOS_RUN/STATUS.txt"
