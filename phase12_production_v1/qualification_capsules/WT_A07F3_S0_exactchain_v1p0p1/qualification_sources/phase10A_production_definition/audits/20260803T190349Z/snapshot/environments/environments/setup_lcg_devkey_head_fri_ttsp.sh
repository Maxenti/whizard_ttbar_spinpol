#!/usr/bin/env bash
# Pinned candidate runtime for WHIZARD ttbar spin/polarization campaign.
# Do not replace this with a floating latest view without rerunning Phase 2.

set +u
source /cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/setup.sh
set -u

export REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"
export PYTHONPATH="$REPO/src${PYTHONPATH:+:$PYTHONPATH}"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export MALLOC_ARENA_MAX="${MALLOC_ARENA_MAX:-2}"

echo "TTSP pinned runtime loaded"
echo "REPO=$REPO"
echo "whizard=$(command -v whizard || true)"
whizard --version | head -1 || true
echo "pythia8-config=$(command -v pythia8-config || true)"
pythia8-config --version || true
echo "HepMC3-config=$(command -v HepMC3-config || true)"
HepMC3-config --version || true
