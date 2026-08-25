#!/usr/bin/env bash
set -euo pipefail

PROC=$1
MANIFEST=$2
REPO=$3
FROZEN=$4
OUTPUT_ROOT=$5
PARENT_LHE=$6
SAMPLE_ID=$7

row=$(
  awk -F '\t' \
    -v proc="$PROC" \
    'NR > 1 && $1 == proc {print; exit}' \
    "$MANIFEST"
)

[[ -n $row ]] \
  || {
    echo "ERROR: no manifest row for proc=$PROC" >&2
    exit 2
  }

IFS=$'\t' read -r \
  PROC_CHECK \
  SHARD_ID \
  INPUT_LHE \
  INPUT_SHA \
  SOURCE_START \
  SOURCE_STOP \
  PYTHIA_SEED \
<<< "$row"

[[ $PROC_CHECK == "$PROC" ]] \
  || {
    echo "ERROR: manifest proc mismatch" >&2
    exit 2
  }

MAX_EVENTS=$(( SOURCE_STOP - SOURCE_START ))

echo "============================================================"
echo "PHASE 12B P6 EXACT 25K WORKER"
echo "============================================================"
echo "HOST=$(hostname -f)"
echo "PROC=$PROC"
echo "SHARD_ID=$SHARD_ID"
echo "INPUT_LHE=$INPUT_LHE"
echo "INPUT_SHA=$INPUT_SHA"
echo "SOURCE_RANGE=[$SOURCE_START,$SOURCE_STOP)"
echo "MAX_EVENTS=$MAX_EVENTS"
echo "PYTHIA_SEED=$PYTHIA_SEED"
echo "OUTPUT_ROOT=$OUTPUT_ROOT"
echo "PARENT_LHE=$PARENT_LHE"
echo "FROZEN=$FROZEN"
echo "READY=${WHIZARD_TTBAR_ENV_READY:-UNSET}"
echo "============================================================"

[[ $MAX_EVENTS -eq 25000 ]] \
  || {
    echo \
      "ERROR: expected 25000 events, got $MAX_EVENTS" \
      >&2
    exit 3
  }

EXPECTED_SEED=$(( 812100001 + PROC ))

[[ $PYTHIA_SEED -eq $EXPECTED_SEED ]] \
  || {
    echo \
      "ERROR: PYTHIA seed mismatch: " \
      "$PYTHIA_SEED != $EXPECTED_SEED" \
      >&2
    exit 4
  }

exec "$FROZEN/run_pythia_shard.sh" \
  --input "$INPUT_LHE" \
  --input-sha256 "$INPUT_SHA" \
  --parent-lhe "$PARENT_LHE" \
  --source-event-start "$SOURCE_START" \
  --source-event-stop "$SOURCE_STOP" \
  --output-root "$OUTPUT_ROOT" \
  --sample-id "$SAMPLE_ID" \
  --campaign-id phase12b_1m_p6_exact_v1 \
  --shard-id "$SHARD_ID" \
  --seed "$PYTHIA_SEED" \
  --max-events "$MAX_EVENTS" \
  --executable "$REPO/build/qis_lhe_to_hepmc3" \
  --settings "$REPO/configs/pythia/level_a.cmnd" \
  --repo-root "$REPO" \
  --helper-dir "$FROZEN/helpers" \
  --key4hep-setup "$REPO/setup_lxplus.sh" \
  --qed-shower-by-gamma off
