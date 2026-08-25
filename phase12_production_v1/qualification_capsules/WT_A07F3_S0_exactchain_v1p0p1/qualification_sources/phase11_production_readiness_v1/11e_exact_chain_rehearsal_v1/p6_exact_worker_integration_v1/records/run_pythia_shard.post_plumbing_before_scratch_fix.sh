#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run_pythia_shard.p6_candidate.sh \
    --input LHE_SHARD \
    --input-sha256 SHA256 \
    --parent-lhe AUTHORITATIVE_LHE \
    --source-event-start N \
    --source-event-stop N \
    --output-root EOS_DIR \
    --sample-id ID \
    --campaign-id ID \
    --shard-id ID \
    --seed N \
    --max-events N \
    --executable PATH \
    --settings PATH \
    [options]

Options:
  --repo-root PATH
      Authoritative project root on shared storage.

  --helper-dir PATH
      Directory containing the P6 preparation helpers.
      Defaults to REPO_ROOT/scripts/showering.

  --key4hep-setup PATH
      Project environment setup script used only if an inherited
      qualified runtime is unavailable.

  --qed-shower-by-gamma on|off
      PYTHIA gamma->fermion shower switch.
USAGE
}

INPUT=
INPUT_SHA256=
PARENT_LHE=
SOURCE_EVENT_START=
SOURCE_EVENT_STOP=
OUTPUT_ROOT=
SAMPLE_ID=
CAMPAIGN_ID=
SHARD_ID=
SEED=
MAX_EVENTS=
EXECUTABLE=
SETTINGS=
PROJECT_ROOT=
HELPER_DIR_OVERRIDE=

KEY4HEP_SETUP=${KEY4HEP_SETUP:-}
QED_SHOWER_BY_GAMMA=on

while (($#)); do
  case "$1" in
    --input)
      INPUT=$2
      shift 2
      ;;
    --input-sha256)
      INPUT_SHA256=$2
      shift 2
      ;;
    --parent-lhe)
      PARENT_LHE=$2
      shift 2
      ;;
    --source-event-start)
      SOURCE_EVENT_START=$2
      shift 2
      ;;
    --source-event-stop)
      SOURCE_EVENT_STOP=$2
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT=$2
      shift 2
      ;;
    --sample-id)
      SAMPLE_ID=$2
      shift 2
      ;;
    --campaign-id)
      CAMPAIGN_ID=$2
      shift 2
      ;;
    --shard-id)
      SHARD_ID=$2
      shift 2
      ;;
    --seed)
      SEED=$2
      shift 2
      ;;
    --max-events)
      MAX_EVENTS=$2
      shift 2
      ;;
    --executable)
      EXECUTABLE=$2
      shift 2
      ;;
    --settings)
      SETTINGS=$2
      shift 2
      ;;
    --repo-root)
      PROJECT_ROOT=$2
      shift 2
      ;;
    --helper-dir)
      HELPER_DIR_OVERRIDE=$2
      shift 2
      ;;
    --key4hep-setup)
      KEY4HEP_SETUP=$2
      shift 2
      ;;
    --qed-shower-by-gamma)
      QED_SHOWER_BY_GAMMA=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

for value in \
  INPUT \
  INPUT_SHA256 \
  PARENT_LHE \
  SOURCE_EVENT_START \
  SOURCE_EVENT_STOP \
  OUTPUT_ROOT \
  SAMPLE_ID \
  CAMPAIGN_ID \
  SHARD_ID \
  SEED \
  MAX_EVENTS \
  EXECUTABLE \
  SETTINGS
do
  [[ -n ${!value} ]] \
    || {
      echo "ERROR: missing $value" >&2
      exit 2
    }
done

[[ \
  $QED_SHOWER_BY_GAMMA == on \
  || $QED_SHOWER_BY_GAMMA == off \
]] \
  || {
    echo \
      "ERROR: --qed-shower-by-gamma must be on or off" \
      >&2
    exit 2
  }

[[ $MAX_EVENTS =~ ^[0-9]+$ ]] \
  && (( MAX_EVENTS > 0 )) \
  || {
    echo "ERROR: --max-events must be positive" >&2
    exit 2
  }

[[ \
  $SOURCE_EVENT_START =~ ^[0-9]+$ \
  && $SOURCE_EVENT_STOP =~ ^[0-9]+$ \
]] \
  || {
    echo \
      "ERROR: source event range must be non-negative integers" \
      >&2
    exit 2
  }

(( \
  SOURCE_EVENT_STOP \
  - SOURCE_EVENT_START \
  == MAX_EVENTS \
)) \
  || {
    echo "ERROR: source range/count mismatch" >&2
    exit 2
  }

[[ $INPUT_SHA256 =~ ^[0-9a-fA-F]{64}$ ]] \
  || {
    echo "ERROR: invalid --input-sha256" >&2
    exit 2
  }

[[ -r $INPUT ]] \
  || {
    echo "ERROR: unreadable LHE shard: $INPUT" >&2
    exit 3
  }

[[ -r $PARENT_LHE ]] \
  || {
    echo "ERROR: unreadable parent LHE: $PARENT_LHE" >&2
    exit 3
  }

[[ -x $EXECUTABLE ]] \
  || {
    echo \
      "ERROR: shower executable is not executable: $EXECUTABLE" \
      >&2
    exit 4
  }

[[ -r $SETTINGS ]] \
  || {
    echo "ERROR: unreadable settings: $SETTINGS" >&2
    exit 5
  }

[[ $OUTPUT_ROOT == /eos/* ]] \
  || {
    echo "ERROR: output root must be EOS: $OUTPUT_ROOT" >&2
    exit 6
  }

SCRIPT_DIR=$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" \
    && pwd
)

if [[ -n $PROJECT_ROOT ]]; then
  [[ -d $PROJECT_ROOT ]] \
    || {
      echo \
        "ERROR: project root does not exist: $PROJECT_ROOT" \
        >&2
      exit 7
    }

  REPO_ROOT=$(
    cd -- "$PROJECT_ROOT" \
      && pwd
  )
else
  REPO_ROOT=$(
    cd -- "$SCRIPT_DIR/../.." \
      && pwd
  )
fi

if [[ -n $HELPER_DIR_OVERRIDE ]]; then
  [[ -d $HELPER_DIR_OVERRIDE ]] \
    || {
      echo \
        "ERROR: helper directory does not exist: " \
        "$HELPER_DIR_OVERRIDE" \
        >&2
      exit 7
    }

  HELPER_DIR=$(
    cd -- "$HELPER_DIR_OVERRIDE" \
      && pwd
  )
else
  HELPER_DIR="$REPO_ROOT/scripts/showering"
fi

CANONICALIZER="$HELPER_DIR/canonicalize_whizard_lhe_for_pythia.py"
SERIALIZER="$HELPER_DIR/reorder_lhe_history_for_pythia_v1.py"
SERIALIZATION_VALIDATOR="$HELPER_DIR/validate_lhe_history_serialization_v1.py"
METADATA_AUGMENTER="$HELPER_DIR/augment_shower_metadata.py"

for helper in \
  "$CANONICALIZER" \
  "$SERIALIZER" \
  "$SERIALIZATION_VALIDATOR" \
  "$METADATA_AUGMENTER"
do
  [[ -x $helper ]] \
    || {
      echo \
        "ERROR: missing executable helper: $helper" \
        >&2
      exit 7
    }
done

echo \
  "PREPARATION_HELPERS " \
  "canonicalizer=$CANONICALIZER " \
  "serializer=$SERIALIZER " \
  "validator=$SERIALIZATION_VALIDATOR " \
  "metadata=$METADATA_AUGMENTER"

# Prefer the already-qualified environment inherited from the
# submit host. Fall back to the project setup only when necessary.
if [[ ${WHIZARD_TTBAR_ENV_READY:-0} == 1 ]]; then
  echo "RUNTIME_ENV mode=inherited_submit_host"

elif [[ -n $KEY4HEP_SETUP ]]; then
  echo "RUNTIME_ENV mode=worker_fallback_setup"

  [[ -r $KEY4HEP_SETUP ]] \
    || {
      echo \
        "ERROR: unreadable environment setup: $KEY4HEP_SETUP" \
        >&2
      exit 8
    }

  nounset_was_on=0
  errexit_was_on=0

  case $- in
    *u*)
      nounset_was_on=1
      set +u
      ;;
  esac

  case $- in
    *e*)
      errexit_was_on=1
      set +e
      ;;
  esac

  # shellcheck disable=SC1090
  source "$KEY4HEP_SETUP"

  setup_rc=$?

  (( errexit_was_on == 0 )) \
    || set -e

  (( nounset_was_on == 0 )) \
    || set -u

  (( setup_rc == 0 )) \
    || {
      echo \
        "ERROR: environment setup failed rc=$setup_rc" \
        >&2
      exit 8
    }

else
  echo \
    "ERROR: no inherited Key4HEP runtime and no fallback setup script" \
    >&2
  exit 8
fi

for command in \
  python3 \
  sha256sum \
  ldd \
  grep
do
  command -v "$command" \
    >/dev/null 2>&1 \
    || {
      echo \
        "ERROR: runtime command missing after environment setup: " \
        "$command" \
        >&2
      exit 8
    }
done

missing_libraries=$(
  ldd "$EXECUTABLE" 2>&1 \
    | awk '/not found/ {print}'
)

if [[ -n $missing_libraries ]]; then
  echo \
    "ERROR: shower executable has unresolved shared libraries:" \
    >&2

  printf '%s\n' \
    "$missing_libraries" \
    >&2

  exit 8
fi

export PYTHONDONTWRITEBYTECODE=1

SCRATCH_BASE=${
  _CONDOR_SCRATCH_DIR:-${TMPDIR:-/tmp/${USER:-unknown}}
}

WORK=$(
  mktemp -d \
    "$SCRATCH_BASE/qis_shower_${SAMPLE_ID}_${SHARD_ID}_XXXXXX"
)

cleanup() {
  rm -rf "$WORK"
}

trap cleanup EXIT

LOCAL_SOURCE="$WORK/source_shard.lhe"

LOCAL_CANON="$WORK/canonical_isr_v2.lhe"
LOCAL_CANON_SUMMARY="$WORK/canonical_isr_v2.summary.json"

LOCAL_SERIALIZED="$WORK/history_serialized_v1.lhe"
LOCAL_SERIALIZER_SUMMARY="$WORK/history_serializer_v1.summary.json"
LOCAL_SERIALIZATION_VALIDATION="$WORK/history_serialization.validation.txt"

LOCAL_PREP_HASHES="$WORK/preparation_hashes.txt"

LOCAL_OUT="$WORK/output.hepmc3"
LOCAL_META="$WORK/output.hepmc3.metadata.json"
LOCAL_LOG="$WORK/pythia.log"

cp -p \
  "$INPUT" \
  "$LOCAL_SOURCE"

actual_sha=$(
  sha256sum "$LOCAL_SOURCE" \
    | awk '{print $1}'
)

[[ $actual_sha == "$INPUT_SHA256" ]] \
  || {
    echo "ERROR: input shard checksum mismatch" >&2
    exit 9
  }

echo \
  "INPUT_SHA256_VERIFIED sha256=$actual_sha"

python3 \
  "$CANONICALIZER" \
  --input "$LOCAL_SOURCE" \
  --output "$LOCAL_CANON" \
  --summary "$LOCAL_CANON_SUMMARY"

python3 \
  "$SERIALIZER" \
  --input "$LOCAL_CANON" \
  --output "$LOCAL_SERIALIZED" \
  --summary "$LOCAL_SERIALIZER_SUMMARY"

set +e

python3 \
  "$SERIALIZATION_VALIDATOR" \
  --input "$LOCAL_CANON" \
  --output "$LOCAL_SERIALIZED" \
  2>&1 \
| tee "$LOCAL_SERIALIZATION_VALIDATION"

validation_rc=${PIPESTATUS[0]}

set -e

if (( validation_rc != 0 )); then
  echo \
    "ERROR: history serialization validator failed " \
    "rc=$validation_rc" \
    >&2

  exit 10
fi

grep -qx \
  "EVENTS_CHECKED=$MAX_EVENTS" \
  "$LOCAL_SERIALIZATION_VALIDATION" \
  || {
    echo \
      "ERROR: serializer validation event-count marker missing" \
      >&2
    exit 10
  }

grep -qx \
  "HISTORY_SERIALIZATION_VALIDATION=PASS" \
  "$LOCAL_SERIALIZATION_VALIDATION" \
  || {
    echo \
      "ERROR: strict history serialization validation did not PASS" \
      >&2
    exit 10
  }

python3 - \
  "$LOCAL_CANON_SUMMARY" \
  "$LOCAL_SERIALIZER_SUMMARY" \
  "$MAX_EVENTS" <<'PY'
import json
import sys
from pathlib import Path

canonical = json.loads(
    Path(sys.argv[1]).read_text()
)

serializer = json.loads(
    Path(sys.argv[2]).read_text()
)

expected = int(
    sys.argv[3]
)

canonical_events = int(
    canonical.get(
        "total_events",
        -1,
    )
)

serializer_events = int(
    serializer.get(
        "total_events",
        -1,
    )
)

if canonical_events != expected:
    raise SystemExit(
        "canonicalizer processed "
        f"{canonical_events} events; "
        f"expected {expected}"
    )

if serializer_events != expected:
    raise SystemExit(
        "serializer processed "
        f"{serializer_events} events; "
        f"expected {expected}"
    )

for field in (
    "particles_added",
    "particles_removed",
    "resonances_added",
    "resonances_removed",
):
    value = int(
        serializer.get(
            field,
            -1,
        )
    )

    if value != 0:
        raise SystemExit(
            "serializer invariant failure: "
            f"{field}={value}"
        )

print(
    "PREPARATION EVENT LIMIT PASS "
    f"events={expected} "
    f"reordered="
    f"{serializer.get('reordered_events')} "
    f"moved_particles="
    f"{serializer.get('total_moved_particles')} "
    f"max_displacement="
    f"{serializer.get('max_particle_displacement')}"
)
PY

canonical_sha=$(
  sha256sum "$LOCAL_CANON" \
    | awk '{print $1}'
)

serialized_sha=$(
  sha256sum "$LOCAL_SERIALIZED" \
    | awk '{print $1}'
)

{
  printf \
    'input_shard_sha256=%s\n' \
    "$actual_sha"

  printf \
    'canonical_isr_v2_sha256=%s\n' \
    "$canonical_sha"

  printf \
    'history_serialized_v1_sha256=%s\n' \
    "$serialized_sha"
} > "$LOCAL_PREP_HASHES"

cat "$LOCAL_PREP_HASHES"

PYTHIA_OVERRIDES=()

if [[ $QED_SHOWER_BY_GAMMA == off ]]; then
  PYTHIA_OVERRIDES+=(
    --set \
    "TimeShower:QEDshowerByGamma = off"
  )
fi

set +e

"$EXECUTABLE" \
  --input "$LOCAL_SERIALIZED" \
  --output "$LOCAL_OUT" \
  --metadata "$LOCAL_META" \
  --settings "$SETTINGS" \
  --sample-id "$SAMPLE_ID" \
  --campaign-id "$CAMPAIGN_ID" \
  --shard-id "$SHARD_ID" \
  --seed "$SEED" \
  --max-events "$MAX_EVENTS" \
  "${PYTHIA_OVERRIDES[@]}" \
  2>&1 \
| tee "$LOCAL_LOG"

shower_rc=${PIPESTATUS[0]}

set -e

if (( shower_rc != 0 )); then
  echo \
    "ERROR: PYTHIA/HepMC conversion failed rc=$shower_rc" \
    >&2

  exit "$shower_rc"
fi

[[ -s $LOCAL_OUT ]] \
  || {
    echo \
      "ERROR: missing/empty local HepMC output" \
      >&2
    exit 11
  }

[[ -s $LOCAL_META ]] \
  || {
    echo \
      "ERROR: missing/empty local metadata" \
      >&2
    exit 12
  }

python3 \
  "$METADATA_AUGMENTER" \
  --metadata "$LOCAL_META" \
  --input-shard "$LOCAL_SOURCE" \
  --input-shard-path "$INPUT" \
  --input-shard-expected-sha256 "$INPUT_SHA256" \
  --parent-lhe-path "$PARENT_LHE" \
  --source-event-start "$SOURCE_EVENT_START" \
  --source-event-stop-exclusive "$SOURCE_EVENT_STOP" \
  --expected-events "$MAX_EVENTS" \
  --canonical-lhe "$LOCAL_CANON" \
  --canonical-summary "$LOCAL_CANON_SUMMARY" \
  --serialized-lhe "$LOCAL_SERIALIZED" \
  --serializer-summary "$LOCAL_SERIALIZER_SUMMARY" \
  --serialization-validation "$LOCAL_SERIALIZATION_VALIDATION" \
  --canonicalizer-tool "$CANONICALIZER" \
  --serializer-tool "$SERIALIZER" \
  --serialization-validator-tool "$SERIALIZATION_VALIDATOR" \
  --metadata-augmenter-tool "$METADATA_AUGMENTER" \
  --worker-log "$LOCAL_LOG" \
  --qed-shower-by-gamma "$QED_SHOWER_BY_GAMMA"

FINAL_DIR="$OUTPUT_ROOT/hepmc3/$SAMPLE_ID"
META_DIR="$OUTPUT_ROOT/metadata/$SAMPLE_ID"
LOG_DIR="$OUTPUT_ROOT/logs/$SAMPLE_ID"
PREP_DIR="$OUTPUT_ROOT/preparation/$SAMPLE_ID"

for directory in \
  "$FINAL_DIR" \
  "$META_DIR" \
  "$LOG_DIR" \
  "$PREP_DIR"
do
  for attempt in 1 2 3 4 5; do
    mkdir -p \
      "$directory" \
      2>/dev/null \
      || true

    [[ -d $directory ]] \
      && break

    sleep "$attempt"
  done

  [[ -d $directory ]] \
    || {
      echo \
        "ERROR: cannot prepare $directory" \
        >&2
      exit 13
    }
done

BASE="${SAMPLE_ID}__${SHARD_ID}"

stage_atomic() {
  local source=$1
  local destination=$2
  local directory
  local temporary

  directory=$(
    dirname -- "$destination"
  )

  temporary="$directory/.$(basename -- "$destination").partial.$$"

  cp -p \
    "$source" \
    "$temporary"

  mv -f \
    "$temporary" \
    "$destination"
}

stage_atomic \
  "$LOCAL_OUT" \
  "$FINAL_DIR/${BASE}.hepmc3"

stage_atomic \
  "$LOCAL_META" \
  "$META_DIR/${BASE}.json"

stage_atomic \
  "$LOCAL_LOG" \
  "$LOG_DIR/${BASE}.log"

stage_atomic \
  "$LOCAL_CANON_SUMMARY" \
  "$PREP_DIR/${BASE}.canonical_isr_v2.json"

stage_atomic \
  "$LOCAL_SERIALIZER_SUMMARY" \
  "$PREP_DIR/${BASE}.history_serializer_v1.json"

stage_atomic \
  "$LOCAL_SERIALIZATION_VALIDATION" \
  "$PREP_DIR/${BASE}.history_serialization_validation.txt"

stage_atomic \
  "$LOCAL_PREP_HASHES" \
  "$PREP_DIR/${BASE}.preparation_hashes.txt"

echo \
  "STAGED $FINAL_DIR/${BASE}.hepmc3"

echo \
  "METADATA $META_DIR/${BASE}.json"

echo \
  "SOURCE_RANGE " \
  "[$SOURCE_EVENT_START,$SOURCE_EVENT_STOP) " \
  "events=$MAX_EVENTS"

echo \
  "POLICY " \
  "canonical_isr_v2+history_serializer_v1 " \
  "explicit_w_adapter=off " \
  "qed_shower_by_gamma=$QED_SHOWER_BY_GAMMA " \
  "repo=$REPO_ROOT " \
  "helpers=$HELPER_DIR"
