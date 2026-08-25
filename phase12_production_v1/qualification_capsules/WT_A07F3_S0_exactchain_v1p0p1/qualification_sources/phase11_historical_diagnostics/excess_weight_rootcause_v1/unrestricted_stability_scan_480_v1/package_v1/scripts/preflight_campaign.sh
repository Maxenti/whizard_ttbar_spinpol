#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: preflight_campaign.sh <campaign_dir>" >&2
  exit 2
fi
CAMPAIGN_DIR=$(readlink -f "$1")

cd "$CAMPAIGN_DIR"
sha256sum -c PRE_SUBMISSION_INPUTS.sha256
bash -n scripts/run_adaptive_parent.sh
bash -n scripts/run_fixed_child.sh
bash -n scripts/submit_campaign.sh
bash -n scripts/status_campaign.sh
python3 -m py_compile scripts/collect_results.py

echo "===== MANIFEST CARDINALITY ====="
python3 - "$CAMPAIGN_DIR/campaign_manifest.tsv" <<'PY'
import csv, sys
rows=list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
a=[r for r in rows if r['stage']=='adaptive']
f=[r for r in rows if r['stage']=='fixed']
assert len(rows)==480, len(rows)
assert len(a)==120, len(a)
assert len(f)==360, len(f)
assert len({(r['adaptive_id'],r['seed_id']) for r in a})==120
assert len({r['mode'] for r in rows})==480
print('MANIFEST_CARDINALITY=PASS')
PY

echo "===== REPRESENTATIVE PARENT PREFLIGHTS: S0 FOR ALL 15 Axx ====="
mkdir -p preflight
for A in $(awk -F '\t' 'NR>1 {print $1}' frozen_config/adaptive_prescriptions.tsv); do
  MODE="${A}_S0"
  echo "----- $MODE -----"
  scripts/run_adaptive_parent.sh \
    --mode "$MODE" \
    --adaptive-id "$A" \
    --seed-id S0 \
    --campaign-dir "$CAMPAIGN_DIR" \
    --output-root /tmp/phase11_unrestricted_stability_preflight_unused \
    --preflight-only \
    2>&1 | tee "preflight/${MODE}.txt"
  grep -q 'ADAPTIVE_PARENT_PREFLIGHT=PASS' "preflight/${MODE}.txt"
done

echo "===== DAG PARSE / NO-SUBMIT CHECK ====="
rm -f campaign.dag.condor.sub
condor_submit_dag -no_submit -force campaign.dag | tee preflight/dag_no_submit.txt

echo "CAMPAIGN_PREFLIGHT=PASS"
