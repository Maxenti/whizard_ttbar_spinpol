#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: status_campaign.sh <campaign_dir>" >&2
  exit 2
fi

CAMPAIGN_DIR=$(readlink -f "$1")
RUNTIME="$CAMPAIGN_DIR/submission_runtime.env"
[[ -f "$RUNTIME" ]] || { echo "ERROR: missing $RUNTIME" >&2; exit 2; }
# shellcheck disable=SC1090
source "$RUNTIME"

Q=(condor_q)
if [[ -n "${SCAN_SCHEDD:-}" ]]; then
  Q+=( -name "$SCAN_SCHEDD" )
fi

echo "===== DAGMAN ====="
"${Q[@]}" "$DAG_CLUSTER" -af ClusterId ProcId JobStatus GlobalJobId 2>/dev/null || true

echo
echo "===== ACTIVE DAG NODE STATUS COUNTS ====="
"${Q[@]}" -constraint "DAGManJobId == $DAG_CLUSTER" -af JobStatus 2>/dev/null \
  | sort | uniq -c || true

echo
echo "===== ACTIVE DAG NODES ====="
"${Q[@]}" -constraint "DAGManJobId == $DAG_CLUSTER" \
  -af ClusterId ProcId JobStatus RemoteWallClockTime MemoryUsage ResidentSetSize Cmd Args RemoteHost 2>/dev/null \
  | head -n 80 || true

echo
echo "===== HELD NODES ====="
"${Q[@]}" -constraint "DAGManJobId == $DAG_CLUSTER && JobStatus == 5" \
  -af ClusterId ProcId HoldReason 2>/dev/null || true

echo
echo "===== OUTPUT COMPLETION COUNTS ====="
python3 - "$CAMPAIGN_DIR/campaign_manifest.tsv" <<'PY'
import csv, sys
from pathlib import Path
p=Path(sys.argv[1])
rows=list(csv.DictReader(p.open(), delimiter='\t'))
for stage in ('adaptive','fixed'):
    subset=[r for r in rows if r['stage']==stage]
    complete=0
    failed=0
    for r in subset:
        d=Path(r['output_dir'])
        if (d/'integration_artifacts.tar.gz').is_file() and (d/'STATUS.txt').is_file():
            status=(d/'STATUS.txt').read_text().strip()
            if status == 'PASS': complete += 1
            else: failed += 1
        elif (d/'STATUS.txt').is_file():
            failed += 1
    print(f'{stage.upper()}_EXPECTED={len(subset)} PASS={complete} FAILED_OUTPUT={failed} REMAINING={len(subset)-complete-failed}')
PY

echo
echo "NOTE: no condor_history call is used by this status script."
