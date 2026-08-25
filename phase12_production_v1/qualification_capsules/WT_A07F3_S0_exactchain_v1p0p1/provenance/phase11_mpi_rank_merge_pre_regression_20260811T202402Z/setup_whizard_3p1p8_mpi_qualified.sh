#!/usr/bin/env bash

export REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

source "$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh"

export WHIZARD_MPI_ROOT="$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811"

export PATH="$WHIZARD_MPI_ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$WHIZARD_MPI_ROOT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

echo "Qualified WHIZARD MPI runtime loaded"
echo "WHIZARD_MPI_ROOT=$WHIZARD_MPI_ROOT"
echo "whizard=$(command -v whizard)"
whizard --version
