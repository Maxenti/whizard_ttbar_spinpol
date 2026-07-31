#!/usr/bin/env bash
# Condor wrapper for one WHIZARD integration point.
set -euo pipefail
CARD=${1:?usage: integration_job.sh CARD OUTDIR}; OUTDIR=${2:?usage: integration_job.sh CARD OUTDIR}; mkdir -p "$OUTDIR"
command -v whizard >/dev/null 2>&1 || { echo "ERROR: whizard not found" >&2; exit 127; }
cp "$CARD" "$OUTDIR/process.sin"; (cd "$OUTDIR" && whizard process.sin > whizard.log 2>&1)
