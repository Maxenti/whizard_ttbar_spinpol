#!/usr/bin/env bash
set -euo pipefail
C=$(readlink -f "$1"); cd "$C"; sha256sum -c PRE_SUBMISSION_INPUTS.sha256
for f in scripts/*.sh; do bash -n "$f"; done
for f in scripts/*.py; do python3 -m py_compile "$f"; done
rm -f campaign.dag.condor.sub; condor_submit_dag -no_submit -force campaign.dag
echo STATIC_PREFLIGHT=PASS
