#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: run_pythia_shard.sh --input LHE --output-root EOS_DIR --sample-id ID
       --campaign-id ID --seed N --executable PATH --settings PATH [options]
USAGE
}

INPUT= OUTPUT_ROOT= SAMPLE_ID= CAMPAIGN_ID= SEED= EXECUTABLE= SETTINGS=
SHARD_ID=merged MAX_EVENTS=-1 KEY4HEP_SETUP=${KEY4HEP_SETUP:-}
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
    -h|--help) usage; exit 0;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2;;
  esac
done
for value in INPUT OUTPUT_ROOT SAMPLE_ID CAMPAIGN_ID SEED EXECUTABLE SETTINGS; do
  [[ -n ${!value} ]] || { echo "ERROR: missing $value" >&2; exit 2; }
done
[[ -r $INPUT ]] || { echo "ERROR: unreadable LHE: $INPUT" >&2; exit 3; }
[[ -x $EXECUTABLE ]] || { echo "ERROR: shower executable is not executable: $EXECUTABLE" >&2; exit 4; }
[[ -r $SETTINGS ]] || { echo "ERROR: unreadable settings: $SETTINGS" >&2; exit 5; }
[[ $OUTPUT_ROOT == /eos/* ]] || { echo "ERROR: output root must be EOS: $OUTPUT_ROOT" >&2; exit 6; }

if [[ -n $KEY4HEP_SETUP ]]; then
  [[ -r $KEY4HEP_SETUP ]] || { echo "ERROR: unreadable environment setup: $KEY4HEP_SETUP" >&2; exit 7; }
  nounset_was_on=0
  errexit_was_on=0
  case $- in *u*) nounset_was_on=1; set +u;; esac
  case $- in *e*) errexit_was_on=1; set +e;; esac
  # shellcheck disable=SC1090
  source "$KEY4HEP_SETUP"
  setup_rc=$?
  (( errexit_was_on == 0 )) || set -e
  (( nounset_was_on == 0 )) || set -u
  (( setup_rc == 0 )) || { echo "ERROR: environment setup failed rc=$setup_rc" >&2; exit 7; }
fi

SCRATCH_BASE=${_CONDOR_SCRATCH_DIR:-${TMPDIR:-/tmp/${USER:-unknown}}}
WORK=$(mktemp -d "$SCRATCH_BASE/qis_shower_${SAMPLE_ID}_${SHARD_ID}_XXXXXX")
cleanup(){ rm -rf "$WORK"; }
trap cleanup EXIT
LOCAL_LHE=$WORK/input.lhe
LOCAL_OUT=$WORK/output.hepmc3
LOCAL_META=$WORK/output.hepmc3.metadata.json
cp -p "$INPUT" "$LOCAL_LHE"

"$EXECUTABLE" \
  --input "$LOCAL_LHE" --output "$LOCAL_OUT" --metadata "$LOCAL_META" \
  --settings "$SETTINGS" --sample-id "$SAMPLE_ID" --campaign-id "$CAMPAIGN_ID" \
  --shard-id "$SHARD_ID" --seed "$SEED" --max-events "$MAX_EVENTS"

FINAL_DIR=$OUTPUT_ROOT/hepmc3/$SAMPLE_ID
META_DIR=$OUTPUT_ROOT/metadata/$SAMPLE_ID
LOG_DIR=$OUTPUT_ROOT/logs/$SAMPLE_ID
for directory in "$FINAL_DIR" "$META_DIR" "$LOG_DIR"; do
  for attempt in 1 2 3 4 5; do
    mkdir -p "$directory" 2>/dev/null || true
    [[ -d $directory ]] && break
    sleep "$attempt"
  done
  [[ -d $directory ]] || { echo "ERROR: cannot prepare $directory" >&2; exit 8; }
done
BASE=${SAMPLE_ID}__${SHARD_ID}
TMP_OUT=$FINAL_DIR/.${BASE}.hepmc3.partial.$$
TMP_META=$META_DIR/.${BASE}.json.partial.$$
cp -p "$LOCAL_OUT" "$TMP_OUT"
cp -p "$LOCAL_META" "$TMP_META"
mv -f "$TMP_OUT" "$FINAL_DIR/${BASE}.hepmc3"
mv -f "$TMP_META" "$META_DIR/${BASE}.json"
echo "STAGED $FINAL_DIR/${BASE}.hepmc3"
