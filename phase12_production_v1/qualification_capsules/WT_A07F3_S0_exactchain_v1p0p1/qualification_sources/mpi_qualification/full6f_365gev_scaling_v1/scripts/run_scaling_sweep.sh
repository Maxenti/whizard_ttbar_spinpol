#!/usr/bin/env bash

set -Eeuo pipefail
set -o pipefail

##############################################################################
# Full-6f 365 GeV WHIZARD MPI/VAMP2 scaling benchmark
#
# One execute node, sequential rank counts:
#
#   1, 2, 4, 8, 16
#
# OMP threads remain fixed at 1.
##############################################################################

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 RUN_TAG"
    exit 2
fi

RUN_TAG="$1"

export REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

export PKG="$REPO/mpi_qualification/full6f_365gev_scaling_v1"

export EOS_BASE=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/mpi_qualification/full6f_365gev_scaling_v1
export EOS_RUN="$EOS_BASE/$RUN_TAG"

export SOURCE="$PKG/benchmark_source"

SCRATCH_BASE="${_CONDOR_SCRATCH_DIR:-${TMPDIR:-/tmp/${USER}/whizard_scaling_${RUN_TAG}}}"

mkdir -p \
    "$EOS_RUN" \
    "$EOS_RUN/provenance" \
    "$SCRATCH_BASE"

##############################################################################
# Runtime
##############################################################################

source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1

##############################################################################
# Initial provenance
##############################################################################

{
    echo "RUN_TAG=$RUN_TAG"
    echo "START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "HOST=$(hostname)"
    echo "FQDN=$(hostname -f || true)"
    echo "SCRATCH_BASE=$SCRATCH_BASE"
    echo "EOS_RUN=$EOS_RUN"
    echo
    echo "WHIZARD_MPI_ROOT=$WHIZARD_MPI_ROOT"
    echo "WHIZARD=$(command -v whizard)"
    whizard --version || true
    echo
    echo "MPIRUN=$(command -v mpirun)"
    mpirun --version | head -5 || true
    echo
    echo "NPROC=$(nproc)"
    echo
    echo "CPUSET:"
    taskset -pc $$ || true
    echo
    echo "CPU MODEL:"
    grep -m1 '^model name' /proc/cpuinfo || true
    echo
    echo "LSCPU:"
    lscpu || true
    echo
    echo "ENV THREAD SETTINGS:"
    env | grep -E '^(OMP|OPENBLAS|MKL|BLIS)_' | sort
} | tee "$EOS_RUN/provenance/runtime.txt"

cp -a \
    "$SOURCE/SOURCE_PROVENANCE.txt" \
    "$SOURCE/SHA256SUMS" \
    "$EOS_RUN/provenance/"

##############################################################################
# Rank sweep
##############################################################################

RANKS_LIST=(1 2 4 8 16)

for N in "${RANKS_LIST[@]}"; do

    echo
    echo "================================================================"
    echo "FULL6F MPI SCALING: NP=$N"
    echo "================================================================"

    WORK="$SCRATCH_BASE/np${N}"
    OUT="$EOS_RUN/np${N}"

    rm -rf "$WORK"
    mkdir -p "$WORK" "$OUT"

    cp -a \
        "$SOURCE/." \
        "$WORK/"

    cd "$WORK"

    {
        echo "NP=$N"
        echo "HOST=$(hostname)"
        echo "START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
        echo
        taskset -pc $$ || true
    } > metadata.txt

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
            --report-bindings \
            "$WHIZARD_MPI_ROOT/bin/whizard" \
            process.sin \
        2>&1 \
        | tee run.log

    RC=${PIPESTATUS[0]}

    set -e

    {
        echo
        echo "END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "WHIZARD_RC=$RC"
    } >> metadata.txt

    echo "$RC" > return_code.txt

    ##########################################################################
    # Compact numerical result
    ##########################################################################

    grep -E \
        '^[[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9.Ee+-]+' \
        run.log \
        | tail -1 \
        > final_integration_row.txt \
        || true

    ##########################################################################
    # Important runtime markers
    ##########################################################################

    grep -E \
        'MPI: Using|MPI: master|MPI: slave|Integrator: VAMP2|VAMP2: .*Request Balancing|There were|WHIZARD run finished' \
        run.log \
        > runtime_markers.txt \
        || true

    ##########################################################################
    # Grid checksums
    ##########################################################################

    find . \
        -maxdepth 1 \
        -type f \
        \( -name '*.vg2' -o -name '*.vg2.bin' \) \
        -print0 \
        | sort -z \
        | xargs -0 -r sha256sum \
        > grid_sha256.txt

    ##########################################################################
    # Persist immediately to EOS before moving to the next rank count
    ##########################################################################

    cp -a \
        process.sin \
        common \
        run.log \
        whizard.log \
        metadata.txt \
        time.txt \
        return_code.txt \
        final_integration_row.txt \
        runtime_markers.txt \
        grid_sha256.txt \
        "$OUT/" \
        2>/dev/null || true

    find . \
        -maxdepth 1 \
        -type f \
        \( -name '*.vg2' -o -name '*.vg2.bin' -o -name '*.phs' \) \
        -exec cp -a {} "$OUT/" \;

    echo
    echo "NP=$N"
    cat time.txt
    cat final_integration_row.txt || true

    if [[ "$RC" -ne 0 ]]; then
        echo
        echo "ERROR: NP=$N failed with RC=$RC"
        echo "Stopping scaling sweep."

        {
            echo "STATUS=FAIL"
            echo "FAILED_NP=$N"
            echo "RC=$RC"
            echo "END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        } > "$EOS_RUN/STATUS.txt"

        exit "$RC"
    fi

done

##############################################################################
# Success
##############################################################################

{
    echo "STATUS=PASS"
    echo "RANKS=1,2,4,8,16"
    echo "END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$EOS_RUN/STATUS.txt"

echo
echo "================================================================"
echo "FULL6F MPI SCALING SWEEP COMPLETE"
echo "================================================================"
echo "EOS_RUN=$EOS_RUN"

cat "$EOS_RUN/STATUS.txt"
