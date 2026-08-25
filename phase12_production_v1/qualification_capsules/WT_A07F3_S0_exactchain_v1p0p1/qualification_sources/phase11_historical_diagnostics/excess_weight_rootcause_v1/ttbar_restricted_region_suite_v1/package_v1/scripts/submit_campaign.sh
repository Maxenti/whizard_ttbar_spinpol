#!/usr/bin/env bash
# Generic DAG submission helper for both suite campaigns.
# It intentionally knows nothing about the names of the individual .sub files;
# campaign.dag is the authoritative graph and condor_submit_dag validates every
# referenced submit descriptor during the no-submit check.
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: submit_campaign.sh <campaign_dir> [--bump-schedd]" >&2
  exit 2
fi
CAMPAIGN_DIR=$(readlink -f "$1")
BUMP=0
if [[ ${2:-} == --bump-schedd ]]; then BUMP=1; elif [[ $# -eq 2 ]]; then echo "ERROR unknown option $2" >&2; exit 2; fi
cd "$CAMPAIGN_DIR"
for F in campaign.dag PRE_SUBMISSION_INPUTS.sha256 campaign_manifest.tsv CAMPAIGN_DESIGN.json; do
  [[ -f "$F" ]] || { echo "ERROR: missing $CAMPAIGN_DIR/$F" >&2; exit 2; }
done
sha256sum -c PRE_SUBMISSION_INPUTS.sha256
rm -f campaign.dag.condor.sub
echo "===== DAG STATIC BUILD CHECK ====="
condor_submit_dag -no_submit -force campaign.dag | tee dag_no_submit.out
if [[ $BUMP -eq 1 ]]; then
  echo "===== MYSCHEdd BUMP ====="
  myschedd bump | tee myschedd_bump.out
fi
echo "===== DAG SUBMISSION ====="
condor_submit_dag -force campaign.dag | tee condor_submit_dag.out
DAG_CLUSTER=$(grep -Eo 'cluster[[:space:]]+[0-9]+' condor_submit_dag.out | tail -1 | awk '{print $2}')
[[ "$DAG_CLUSTER" =~ ^[0-9]+$ ]] || { echo 'ERROR could not parse DAG cluster' >&2; exit 3; }
# Because the submission has just occurred on the current schedd, this lookup
# recovers the schedd hostname before a later terminal/session loses it.
GLOBAL_ID=$(condor_q "$DAG_CLUSTER" -af GlobalJobId 2>/dev/null | head -1 || true)
SCAN_SCHEDD=${GLOBAL_ID%%#*}; [[ -n "$SCAN_SCHEDD" && "$SCAN_SCHEDD" != "$GLOBAL_ID" ]] || SCAN_SCHEDD=""
NODES=$(grep -c '^JOB ' campaign.dag)
cat > submission_runtime.env <<EOF
DAG_CLUSTER='$DAG_CLUSTER'
SCAN_SCHEDD='$SCAN_SCHEDD'
CAMPAIGN_DIR='$CAMPAIGN_DIR'
EOF
cat > SUBMISSION_RECORD.txt <<EOF
Phase 11 ttbar restricted/region suite campaign
===============================================
DAGMan cluster: $DAG_CLUSTER
Schedd: ${SCAN_SCHEDD:-UNKNOWN}
Campaign directory: $CAMPAIGN_DIR
DAG nodes: $NODES
Submission UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF
sha256sum condor_submit_dag.out SUBMISSION_RECORD.txt submission_runtime.env > POST_SUBMISSION_PROVENANCE.sha256
cat SUBMISSION_RECORD.txt
echo "DAG_CLUSTER=$DAG_CLUSTER"; echo "SCAN_SCHEDD=$SCAN_SCHEDD"; echo CAMPAIGN_SUBMISSION=PASS
