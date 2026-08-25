#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo 'usage: show_live_tails.sh CAMPAIGN_DIR [grep_regex]' >&2; exit 2; }
C=$(readlink -f "$1"); PAT=${2:-'^[[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9.+-]+E[+-][0-9]+|FATAL ERROR|WHIZARD_RC='}; source "$C/submission_runtime.env"
while read -r CL PR NODE; do
 echo; echo "===== $NODE ${CL}.${PR} ====="; condor_tail -name "$SCAN_SCHEDD" "${CL}.${PR}" 2>/dev/null | grep -E "$PAT" | tail -n 20 || true
done < <(condor_q -name "$SCAN_SCHEDD" -constraint "DAGManJobId == $DAG_CLUSTER && JobStatus == 2" -af ClusterId ProcId DAGNodeName | sort -k3)
