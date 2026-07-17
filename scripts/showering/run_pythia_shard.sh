#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: run_pythia_shard.sh --input LHE --output-root EOS_DIR --sample-id ID
       --campaign-id ID --seed N --executable PATH --settings PATH [options]

Options:
  --shard-id ID                  Output shard ID (default: merged)
  --max-events N                 Maximum events, -1 for all (default: -1)
  --key4hep-setup PATH           Project environment setup script
  --qed-shower-by-gamma on|off   PYTHIA gamma->fermion shower switch (default: on)
USAGE
}

INPUT= OUTPUT_ROOT= SAMPLE_ID= CAMPAIGN_ID= SEED= EXECUTABLE= SETTINGS=
SHARD_ID=merged
MAX_EVENTS=-1
KEY4HEP_SETUP=${KEY4HEP_SETUP:-}
QED_SHOWER_BY_GAMMA=on

while (($#)); do
  case "$1" in
    --input) INPUT=$2; shift 2;;
    --output-root) OUTPUT_ROOT=$2; shift 2;;
    --sample-id) SAMPLE_ID=$2; shift 2;;
    --campaign-id) CAMPAIGN_ID=$2; shift 2;;
    --seed) SEED=$2; shift 2;;
    --executable) EXECUTABLE=$2; shift 2;;
    --settings) SETTINGS=$2; shift 2;;
    --shard-id) SHARD_ID=$2; shift 2;;
    --max-events) MAX_EVENTS=$2; shift 2;;
    --key4hep-setup) KEY4HEP_SETUP=$2; shift 2;;
    --qed-shower-by-gamma) QED_SHOWER_BY_GAMMA=$2; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2;;
  esac
done

for value in INPUT OUTPUT_ROOT SAMPLE_ID CAMPAIGN_ID SEED EXECUTABLE SETTINGS; do
  [[ -n ${!value} ]] || { echo "ERROR: missing $value" >&2; exit 2; }
done
[[ $QED_SHOWER_BY_GAMMA == on || $QED_SHOWER_BY_GAMMA == off ]] \
  || { echo "ERROR: --qed-shower-by-gamma must be on or off" >&2; exit 2; }
[[ -r $INPUT ]] || { echo "ERROR: unreadable LHE: $INPUT" >&2; exit 3; }
[[ -x $EXECUTABLE ]] || { echo "ERROR: shower executable is not executable: $EXECUTABLE" >&2; exit 4; }
[[ -r $SETTINGS ]] || { echo "ERROR: unreadable settings: $SETTINGS" >&2; exit 5; }
[[ $OUTPUT_ROOT == /eos/* ]] || { echo "ERROR: output root must be EOS: $OUTPUT_ROOT" >&2; exit 6; }

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
CANONICALIZER="$SCRIPT_DIR/canonicalize_whizard_lhe_for_pythia.py"
EXPLICIT_W_ADAPTER="$SCRIPT_DIR/insert_explicit_w_resonances.py"
METADATA_AUGMENTER="$SCRIPT_DIR/augment_shower_metadata.py"

for helper in "$CANONICALIZER" "$EXPLICIT_W_ADAPTER" "$METADATA_AUGMENTER"; do
  [[ -x $helper ]] || { echo "ERROR: missing executable helper: $helper" >&2; exit 7; }
done

if [[ -n $KEY4HEP_SETUP ]]; then
  [[ -r $KEY4HEP_SETUP ]] || { echo "ERROR: unreadable environment setup: $KEY4HEP_SETUP" >&2; exit 8; }
  nounset_was_on=0
  errexit_was_on=0
  case $- in *u*) nounset_was_on=1; set +u;; esac
  case $- in *e*) errexit_was_on=1; set +e;; esac
  # shellcheck disable=SC1090
  source "$KEY4HEP_SETUP"
  setup_rc=$?
  (( errexit_was_on == 0 )) || set -e
  (( nounset_was_on == 0 )) || set -u
  (( setup_rc == 0 )) || { echo "ERROR: environment setup failed rc=$setup_rc" >&2; exit 8; }
fi

export PYTHONDONTWRITEBYTECODE=1

SCRATCH_BASE=${_CONDOR_SCRATCH_DIR:-${TMPDIR:-/tmp/${USER:-unknown}}}
WORK=$(mktemp -d "$SCRATCH_BASE/qis_shower_${SAMPLE_ID}_${SHARD_ID}_XXXXXX")
cleanup(){ rm -rf "$WORK"; }
trap cleanup EXIT

LOCAL_SOURCE=$WORK/source_whizard.lhe
LOCAL_V2=$WORK/canonical_v2.lhe
LOCAL_V2_SUMMARY=$WORK/canonical_v2.summary.json
LOCAL_V3=$WORK/explicit_w_v3.lhe
LOCAL_V3_SUMMARY=$WORK/explicit_w_v3.summary.json
LOCAL_OUT=$WORK/output.hepmc3
LOCAL_META=$WORK/output.hepmc3.metadata.json
LOCAL_LOG=$WORK/pythia.log

cp -p "$INPUT" "$LOCAL_SOURCE"

python3 "$CANONICALIZER" \
  --input "$LOCAL_SOURCE" \
  --output "$LOCAL_V2" \
  --summary "$LOCAL_V2_SUMMARY"

python3 "$EXPLICIT_W_ADAPTER" \
  --input "$LOCAL_V2" \
  --output "$LOCAL_V3" \
  --summary "$LOCAL_V3_SUMMARY"

PYTHIA_OVERRIDES=()
if [[ $QED_SHOWER_BY_GAMMA == off ]]; then
  PYTHIA_OVERRIDES+=(--set "TimeShower:QEDshowerByGamma = off")
fi

set +e
"$EXECUTABLE" \
  --input "$LOCAL_V3" \
  --output "$LOCAL_OUT" \
  --metadata "$LOCAL_META" \
  --settings "$SETTINGS" \
  --sample-id "$SAMPLE_ID" \
  --campaign-id "$CAMPAIGN_ID" \
  --shard-id "$SHARD_ID" \
  --seed "$SEED" \
  --max-events "$MAX_EVENTS" \
  "${PYTHIA_OVERRIDES[@]}" \
  2>&1 | tee "$LOCAL_LOG"
shower_rc=${PIPESTATUS[0]}
set -e

if (( shower_rc != 0 )); then
  echo "ERROR: PYTHIA/HepMC conversion failed rc=$shower_rc" >&2
  exit "$shower_rc"
fi

[[ -s $LOCAL_OUT ]] || { echo "ERROR: missing/empty local HepMC output" >&2; exit 9; }
[[ -s $LOCAL_META ]] || { echo "ERROR: missing/empty local metadata" >&2; exit 10; }

python3 "$METADATA_AUGMENTER" \
  --metadata "$LOCAL_META" \
  --source-lhe "$LOCAL_SOURCE" \
  --source-lhe-path "$INPUT" \
  --canonical-summary "$LOCAL_V2_SUMMARY" \
  --explicit-w-summary "$LOCAL_V3_SUMMARY" \
  --worker-log "$LOCAL_LOG" \
  --qed-shower-by-gamma "$QED_SHOWER_BY_GAMMA"

FINAL_DIR=$OUTPUT_ROOT/hepmc3/$SAMPLE_ID
META_DIR=$OUTPUT_ROOT/metadata/$SAMPLE_ID
LOG_DIR=$OUTPUT_ROOT/logs/$SAMPLE_ID
PREP_DIR=$OUTPUT_ROOT/preparation/$SAMPLE_ID
for directory in "$FINAL_DIR" "$META_DIR" "$LOG_DIR" "$PREP_DIR"; do
  for attempt in 1 2 3 4 5; do
    mkdir -p "$directory" 2>/dev/null || true
    [[ -d $directory ]] && break
    sleep "$attempt"
  done
  [[ -d $directory ]] || { echo "ERROR: cannot prepare $directory" >&2; exit 11; }
done

BASE=${SAMPLE_ID}__${SHARD_ID}

stage_atomic() {
  local source=$1
  local destination=$2
  local directory
  directory=$(dirname -- "$destination")
  local temporary="$directory/.$(basename -- "$destination").partial.$$"
  cp -p "$source" "$temporary"
  mv -f "$temporary" "$destination"
}

stage_atomic "$LOCAL_OUT" "$FINAL_DIR/${BASE}.hepmc3"
stage_atomic "$LOCAL_META" "$META_DIR/${BASE}.json"
stage_atomic "$LOCAL_LOG" "$LOG_DIR/${BASE}.log"
stage_atomic "$LOCAL_V2_SUMMARY" "$PREP_DIR/${BASE}.canonical_v2.json"
stage_atomic "$LOCAL_V3_SUMMARY" "$PREP_DIR/${BASE}.explicit_w_v3.json"

echo "STAGED $FINAL_DIR/${BASE}.hepmc3"
echo "METADATA $META_DIR/${BASE}.json"
echo "PREPARATION $PREP_DIR/${BASE}.canonical_v2.json"
echo "PREPARATION $PREP_DIR/${BASE}.explicit_w_v3.json"
echo "POLICY explicit_w_v3 qed_shower_by_gamma=$QED_SHOWER_BY_GAMMA repo=$REPO_ROOT"
