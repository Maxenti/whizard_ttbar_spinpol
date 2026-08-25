#!/usr/bin/env bash

export REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"

export WHIZARD_MPI_ROOT="${WHIZARD_MPI_ROOT:-$REPO/local/whizard-3.1.8-mpi-omp}"

export BASE_ENV="${BASE_ENV:-$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh}"

if [[ ! -r "$BASE_ENV" ]]; then
    echo "ERROR: cannot read base environment:" >&2
    echo "  $BASE_ENV" >&2
    return 1 2>/dev/null || exit 1
fi

source "$BASE_ENV"

export OCAML_ROOT=/cvmfs/sft.cern.ch/lcg/releases/ocaml/4.14.2-7a890/x86_64-el9-gcc14-opt
export PATH="$OCAML_ROOT/bin:$WHIZARD_MPI_ROOT/bin:$PATH"

export LD_LIBRARY_PATH="$WHIZARD_MPI_ROOT/lib:${LD_LIBRARY_PATH:-}"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

hash -r

if [[ ! -x "$WHIZARD_MPI_ROOT/bin/whizard" ]]; then
    echo "ERROR: WHIZARD MPI install not found:" >&2
    echo "  $WHIZARD_MPI_ROOT" >&2
    return 1 2>/dev/null || exit 1
fi

echo "================================================================"
echo "WHIZARD 3.1.8 MPI/OpenMP environment"
echo "================================================================"
echo "root=$WHIZARD_MPI_ROOT"
echo "whizard=$(command -v whizard)"
echo "mpirun=$(command -v mpirun)"
echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"

whizard --version
