#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$HERE/submission_runtime.env"

echo "============================================================"
echo "PHASE 11 UNRESTRICTED STABILITY SCAN"
echo "============================================================"
echo "DAG_CLUSTER=$DAG_CLUSTER"
echo "SCAN_SCHEDD=$SCAN_SCHEDD"
echo

echo "===== QUEUE ====="

condor_q \
  -name "$SCAN_SCHEDD" \
  "$DAG_CLUSTER"

echo
echo "===== RUNNING PARENTS: LATEST ITERATION ====="

while read -r CLUSTER PROC NODE; do

  [[ -n "$CLUSTER" ]] || continue

  LAST=$(
    condor_tail \
      -name "$SCAN_SCHEDD" \
      "${CLUSTER}.${PROC}" \
      2>/dev/null \
    | grep -E \
        '^[[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9.+-]+E[+-][0-9]+' \
    | tail -n 1
  )

  printf '%-18s %-14s %s\n' \
    "$NODE" \
    "${CLUSTER}.${PROC}" \
    "$LAST"

done < <(
  condor_q \
    -name "$SCAN_SCHEDD" \
    -constraint "DAGManJobId == $DAG_CLUSTER && JobStatus == 2" \
    -af ClusterId ProcId DAGNodeName \
  | grep ' P_' \
  | sort -k3
)

echo
echo "===== ACTIVE CHILDREN ====="

condor_q \
  -name "$SCAN_SCHEDD" \
  -constraint "DAGManJobId == $DAG_CLUSTER && JobStatus == 2" \
  -af ClusterId ProcId DAGNodeName RemoteWallClockTime \
| grep ' C_' \
| sort -k3 \
| head -n 50

echo
echo "===== HELD NODES ====="

condor_q \
  -name "$SCAN_SCHEDD" \
  -constraint "DAGManJobId == $DAG_CLUSTER && JobStatus == 5" \
  -af \
    ClusterId \
    ProcId \
    DAGNodeName \
    HoldReason

