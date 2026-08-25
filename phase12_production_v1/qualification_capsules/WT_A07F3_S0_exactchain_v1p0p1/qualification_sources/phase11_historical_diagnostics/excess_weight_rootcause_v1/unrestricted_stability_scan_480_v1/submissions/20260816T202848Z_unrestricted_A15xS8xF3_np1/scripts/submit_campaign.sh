#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: submit_campaign.sh <campaign_dir> [--bump-schedd]" >&2
  exit 2
fi

CAMPAIGN_DIR=$(readlink -f "$1")
BUMP=0
if [[ ${2:-} == "--bump-schedd" ]]; then BUMP=1; elif [[ $# -eq 2 ]]; then echo "ERROR: unknown option $2" >&2; exit 2; fi

cd "$CAMPAIGN_DIR"

for F in campaign.dag adaptive_parent.sub fixed_child.sub PRE_SUBMISSION_INPUTS.sha256; do
  [[ -f "$F" ]] || { echo "ERROR: missing $CAMPAIGN_DIR/$F" >&2; exit 2; }
done

sha256sum -c PRE_SUBMISSION_INPUTS.sha256

echo "===== DAG STATIC BUILD CHECK ====="
rm -f campaign.dag.condor.sub
condor_submit_dag -no_submit -force campaign.dag | tee dag_no_submit.out

if [[ "$BUMP" -eq 1 ]]; then
  echo "===== MYSCHEdd BUMP ====="
  myschedd bump | tee myschedd_bump.out
fi

echo "===== DAG SUBMISSION ====="
condor_submit_dag -force campaign.dag | tee condor_submit_dag.out

DAG_CLUSTER=$(grep -Eo 'cluster[[:space:]]+[0-9]+' condor_submit_dag.out | tail -1 | awk '{print $2}')
if [[ ! "$DAG_CLUSTER" =~ ^[0-9]+$ ]]; then
  echo "ERROR: could not parse DAGMan cluster id" >&2
  exit 3
fi

GLOBAL_ID=$(condor_q "$DAG_CLUSTER" -af GlobalJobId 2>/dev/null | head -1 || true)
SCAN_SCHEDD=${GLOBAL_ID%%#*}
if [[ -z "$SCAN_SCHEDD" || "$SCAN_SCHEDD" == "$GLOBAL_ID" ]]; then
  SCAN_SCHEDD=""
fi

cat > submission_runtime.env <<EOF2
DAG_CLUSTER='$DAG_CLUSTER'
SCAN_SCHEDD='$SCAN_SCHEDD'
CAMPAIGN_DIR='$CAMPAIGN_DIR'
EOF2

cat > SUBMISSION_RECORD.txt <<EOF2
Phase 11 unrestricted integration-stability scan v1
===================================================
DAGMan cluster: $DAG_CLUSTER
Schedd: ${SCAN_SCHEDD:-UNKNOWN}
Campaign directory: $CAMPAIGN_DIR
DAG nodes: 480
Adaptive parents: 120
Fixed children: 360
Submission UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF2

sha256sum condor_submit_dag.out SUBMISSION_RECORD.txt submission_runtime.env > POST_SUBMISSION_PROVENANCE.sha256

cat SUBMISSION_RECORD.txt

echo
printf 'DAG_CLUSTER=%s\n' "$DAG_CLUSTER"
printf 'SCAN_SCHEDD=%s\n' "$SCAN_SCHEDD"
echo "CAMPAIGN_SUBMISSION=PASS"
