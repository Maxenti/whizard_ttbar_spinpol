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
python3 - "$CAMPAIGN_DIR/campaign_manifest.tsv" <<'PY_STATUS'
import csv,sys
from collections import Counter
from pathlib import Path
rows=list(csv.DictReader(Path(sys.argv[1]).open(),delimiter='\t'))
for stage in sorted(set(r['stage'] for r in rows)):
 x=[r for r in rows if r['stage']==stage]; p=f=0
 for r in x:
  sf=Path(r['output_dir'])/'STATUS.txt'
  if sf.is_file():
   s=sf.read_text().strip();p += s=='PASS';f += s!='PASS'
 print(f'{stage.upper()}_EXPECTED={len(x)} PASS={p} FAILED_OUTPUT={f} REMAINING={len(x)-p-f}')
PY_STATUS
echo
echo "NOTE: no condor_history call is used by this status script."
