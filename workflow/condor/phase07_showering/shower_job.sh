#!/usr/bin/env bash
# Condor wrapper for one PYTHIA/HepMC shower shard.
set -euo pipefail
REPO=${REPO:?REPO must be exported}; LHE=${1:?usage: shower_job.sh LHE CONFIG OUT}; CONFIG=${2:?usage: shower_job.sh LHE CONFIG OUT}; OUT=${3:?usage: shower_job.sh LHE CONFIG OUT}
bash "$REPO/scripts/showering/run_external_pythia.sh" --lhe "$LHE" --config "$CONFIG" --out "$OUT"
