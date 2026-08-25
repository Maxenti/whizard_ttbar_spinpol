#!/usr/bin/env bash
set -euo pipefail

if [[ "${WHIZARD_TTBAR_ENV_READY:-0}" != "1" ]]; then
    echo "RUNTIME_PREFLIGHT=FAIL"
    echo "ERROR: WHIZARD_TTBAR_ENV_READY is not 1." >&2
    exit 90
fi

if [[ -z "${LD_LIBRARY_PATH:-}" ]]; then
    echo "RUNTIME_PREFLIGHT=FAIL"
    echo "ERROR: inherited LD_LIBRARY_PATH is empty." >&2
    exit 91
fi

echo "RUNTIME_PREFLIGHT=PASS"
echo "RUNTIME_ENV mode=inherited_submit_host"
echo "WHIZARD_TTBAR_ENV_READY=$WHIZARD_TTBAR_ENV_READY"
echo "python=$(command -v python3)"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS:-UNSET}"

exec "/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/scripts/showering/run_pythia_shard.sh" "$@"
