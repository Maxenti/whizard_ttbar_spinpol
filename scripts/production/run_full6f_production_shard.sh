#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_full6f_production_shard.sh \
    --campaign-id ID \
    --sample-id ID \
    --subprocess-id ID \
    --source-card PATH \
    --shard-index N \
    --whizard-seed N \
    --events N \
    --iterations SPEC \
    --campaign-root PATH \
    [--archive-workspace 0|1] \
    [--timeout-minutes N] \
    [--force]

Runs one direct-full6f WHIZARD production shard.

The supplied WHIZARD seed is inserted before integration and controls both
integration-grid construction and event generation. PYTHIA showering is not
performed by this worker and must use a separate seed stream.
EOF
}

CAMPAIGN_ID=""
SAMPLE_ID=""
SUBPROCESS_ID=""
SOURCE_CARD=""
SHARD_INDEX=""
WHIZARD_SEED=""
EVENTS=""
ITERATIONS=""
CAMPAIGN_ROOT=""
ARCHIVE_WORKSPACE=1
TIMEOUT_MINUTES=180
FORCE=0

while (($#)); do
  case "$1" in
    --campaign-id)
      CAMPAIGN_ID=${2:?}
      shift 2
      ;;
    --sample-id)
      SAMPLE_ID=${2:?}
      shift 2
      ;;
    --subprocess-id)
      SUBPROCESS_ID=${2:?}
      shift 2
      ;;
    --source-card)
      SOURCE_CARD=${2:?}
      shift 2
      ;;
    --shard-index)
      SHARD_INDEX=${2:?}
      shift 2
      ;;
    --whizard-seed)
      WHIZARD_SEED=${2:?}
      shift 2
      ;;
    --events)
      EVENTS=${2:?}
      shift 2
      ;;
    --iterations)
      ITERATIONS=${2:?}
      shift 2
      ;;
    --campaign-root)
      CAMPAIGN_ROOT=${2:?}
      shift 2
      ;;
    --archive-workspace)
      ARCHIVE_WORKSPACE=${2:?}
      shift 2
      ;;
    --timeout-minutes)
      TIMEOUT_MINUTES=${2:?}
      shift 2
      ;;
    --force)
      FORCE=1
      shift
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

required_values=(
  CAMPAIGN_ID
  SAMPLE_ID
  SUBPROCESS_ID
  SOURCE_CARD
  SHARD_INDEX
  WHIZARD_SEED
  EVENTS
  ITERATIONS
  CAMPAIGN_ROOT
)

for variable in "${required_values[@]}"; do
  if [[ -z "${!variable}" ]]; then
    echo "ERROR: missing required value: $variable" >&2
    usage >&2
    exit 2
  fi
done

for numeric in SHARD_INDEX WHIZARD_SEED EVENTS TIMEOUT_MINUTES; do
  if [[ ! "${!numeric}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: $numeric must be a nonnegative integer: ${!numeric}" >&2
    exit 2
  fi
done

if (( EVENTS <= 0 )); then
  echo "ERROR: EVENTS must be positive" >&2
  exit 2
fi

if (( WHIZARD_SEED <= 0 )); then
  echo "ERROR: WHIZARD_SEED must be positive" >&2
  exit 2
fi

if [[ "$ARCHIVE_WORKSPACE" != 0 && "$ARCHIVE_WORKSPACE" != 1 ]]; then
  echo "ERROR: --archive-workspace must be 0 or 1" >&2
  exit 2
fi

SOURCE_CARD="$(readlink -f "$SOURCE_CARD")"
CAMPAIGN_ROOT="${CAMPAIGN_ROOT%/}"

if [[ ! -s "$SOURCE_CARD" ]]; then
  echo "ERROR: source card is missing or empty: $SOURCE_CARD" >&2
  exit 1
fi

SOURCE_DIR="$(dirname "$SOURCE_CARD")"
SOURCE_COMMON="$SOURCE_DIR/common"
SOURCE_CONTEXT="$SOURCE_DIR/render_context.json"

for required_path in \
  "$SOURCE_COMMON" \
  "$SOURCE_CONTEXT" \
  "$SOURCE_COMMON/integration.inc" \
  "$SOURCE_COMMON/event_output.inc"
do
  if [[ ! -e "$required_path" ]]; then
    echo "ERROR: missing source-card dependency: $required_path" >&2
    exit 1
  fi
done

if ! command -v whizard >/dev/null 2>&1; then
  echo "ERROR: whizard is not available in PATH" >&2
  exit 1
fi

WHIZARD_VERSION_LINE="$(whizard --version 2>&1 | head -n 1)"

if [[ "$WHIZARD_VERSION_LINE" != *"3.1.8"* ]]; then
  echo "ERROR: expected WHIZARD 3.1.8" >&2
  echo "Observed: $WHIZARD_VERSION_LINE" >&2
  exit 1
fi

SHARD_LABEL="$(printf 'shard_%04d' "$SHARD_INDEX")"
OUTPUT_BASENAME="${SAMPLE_ID}__${SUBPROCESS_ID}__${SHARD_LABEL}"

RUN_DIR="$CAMPAIGN_ROOT/runs/$SAMPLE_ID/$SUBPROCESS_ID/$SHARD_LABEL"
RAW_LHE_DIR="$CAMPAIGN_ROOT/lhe_raw/$SAMPLE_ID/$SUBPROCESS_ID"
RAW_LHE="$RAW_LHE_DIR/${OUTPUT_BASENAME}.lhe"
METADATA="$RUN_DIR/run_metadata.json"
SUCCESS_MARKER="$RUN_DIR/SUCCESS"

if [[ -e "$SUCCESS_MARKER" && "$FORCE" -ne 1 ]]; then
  echo "ERROR: shard already completed: $SUCCESS_MARKER" >&2
  echo "Use --force only for an intentional replacement." >&2
  exit 1
fi

if [[ -e "$RUN_DIR" && "$FORCE" -ne 1 ]]; then
  echo "ERROR: shard run directory already exists: $RUN_DIR" >&2
  exit 1
fi

if [[ -e "$RAW_LHE" && "$FORCE" -ne 1 ]]; then
  echo "ERROR: raw LHE already exists: $RAW_LHE" >&2
  exit 1
fi

if [[ "$FORCE" -eq 1 ]]; then
  rm -rf -- "$RUN_DIR"
  rm -f -- "$RAW_LHE"
fi

mkdir -p "$RUN_DIR"
mkdir -p "$RAW_LHE_DIR"

if [[ -n "${_CONDOR_SCRATCH_DIR:-}" ]]; then
  SCRATCH_BASE="$_CONDOR_SCRATCH_DIR"
elif [[ -n "${TMPDIR:-}" ]]; then
  SCRATCH_BASE="$TMPDIR"
else
  SCRATCH_BASE="/tmp/${USER:-unknown}"
fi

mkdir -p "$SCRATCH_BASE"

if [[ ! -d "$SCRATCH_BASE" ]]; then
  echo "ERROR: scratch base was not created: $SCRATCH_BASE" >&2
  exit 1
fi

if [[ ! -w "$SCRATCH_BASE" ]]; then
  echo "ERROR: scratch base is not writable: $SCRATCH_BASE" >&2
  exit 1
fi

SCRATCH_DIR="$(
  mktemp -d "$SCRATCH_BASE/full6f_${OUTPUT_BASENAME}_XXXXXX"
)"

cleanup() {
  local rc=$?

  if [[ "$ARCHIVE_WORKSPACE" -eq 1 && -d "$SCRATCH_DIR" ]]; then
    rm -rf -- "$RUN_DIR/workspace"
    mkdir -p "$RUN_DIR/workspace"
    cp -a "$SCRATCH_DIR/." "$RUN_DIR/workspace/" || true
  fi

  rm -rf -- "$SCRATCH_DIR"
  exit "$rc"
}

trap cleanup EXIT

START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HOSTNAME_VALUE="$(hostname -f 2>/dev/null || hostname)"

cp -a "$SOURCE_CARD" "$SCRATCH_DIR/process.sin"
cp -a "$SOURCE_COMMON" "$SCRATCH_DIR/common"
cp -a "$SOURCE_CONTEXT" "$SCRATCH_DIR/render_context.json"

LOCAL_PROCESS_CARD="$SCRATCH_DIR/process.sin"
LOCAL_INTEGRATION="$SCRATCH_DIR/common/integration.inc"
LOCAL_EVENT_OUTPUT="$SCRATCH_DIR/common/event_output.inc"

# The generated process card contains absolute include paths into the
# repository-generated card tree. Rewrite every common include to the
# shard-local copy so seed, integration, event-count, and output-name
# overrides are actually consumed by WHIZARD.
python3 - "$LOCAL_PROCESS_CARD" "$SOURCE_COMMON" <<'PY_LOCALIZE'
from __future__ import annotations

import re
import sys
from pathlib import Path

process_card = Path(sys.argv[1])
source_common = Path(sys.argv[2]).resolve()

text = process_card.read_text(encoding="utf-8")

include_pattern = re.compile(
    r'include\("'
    + re.escape(str(source_common))
    + r'/([^"]+)"\)'
)

matches = include_pattern.findall(text)

required_files = {
    "model.inc",
    "beams.inc",
    "isr.inc",
    "integration.inc",
    "event_output.inc",
}

optional_files = {
    "polarization.inc",
}

allowed_files = required_files | optional_files
observed_files = set(matches)

missing = required_files - observed_files
unexpected = observed_files - allowed_files

if missing:
    raise SystemExit(
        "ERROR: process-card localization did not find required includes: "
        + ", ".join(sorted(missing))
    )

if unexpected:
    raise SystemExit(
        "ERROR: process card contains unexpected common includes: "
        + ", ".join(sorted(unexpected))
    )

localized = include_pattern.sub(
    lambda match: f'include("common/{match.group(1)}")',
    text,
)

if str(source_common) in localized:
    raise SystemExit(
        "ERROR: source common path remains in localized process card"
    )

for filename in sorted(observed_files):
    marker = f'include("common/{filename}")'

    if localized.count(marker) != 1:
        raise SystemExit(
            f"ERROR: expected exactly one localized include {marker}, "
            f"found {localized.count(marker)}"
        )

print(
    "LOCALIZED_COMMON_INCLUDES="
    + ",".join(sorted(observed_files))
)
print(
    "POLARIZATION_INCLUDE_PRESENT="
    + str("polarization.inc" in observed_files).lower()
)

process_card.write_text(localized, encoding="utf-8")

print(f"LOCALIZED_PROCESS_CARD={process_card}")
print(f"N_LOCALIZED_INCLUDES={len(matches)}")
PY_LOCALIZE

python3 - \
  "$LOCAL_INTEGRATION" \
  "$WHIZARD_SEED" \
  "$ITERATIONS" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
requested_seed = int(sys.argv[2])
iterations = sys.argv[3]

text = path.read_text(encoding="utf-8")

seed_pattern = re.compile(
    r"(?m)^\s*seed\s*=\s*(\d+)\s*$"
)
seed_matches = list(seed_pattern.finditer(text))

if len(seed_matches) != 1:
    raise SystemExit(
        f"ERROR: expected one rendered seed assignment in {path}, "
        f"found {len(seed_matches)}"
    )

text = seed_pattern.sub(
    f"seed = {requested_seed}",
    text,
    count=1,
)

iterations_pattern = re.compile(
    r"(?m)^\s*iterations\s*=\s*.+$"
)
iteration_matches = list(iterations_pattern.finditer(text))

if len(iteration_matches) != 1:
    raise SystemExit(
        f"ERROR: expected one iterations assignment in {path}, "
        f"found {len(iteration_matches)}"
    )

text = iterations_pattern.sub(
    f"iterations = {iterations}",
    text,
    count=1,
)

if "integrate (" not in text:
    raise SystemExit(f"ERROR: no integrate statement in {path}")

if text.index(f"seed = {requested_seed}") >= text.index("integrate ("):
    raise SystemExit(
        "ERROR: localized WHIZARD seed does not precede integration"
    )

path.write_text(text, encoding="utf-8")
PY

python3 - \
  "$LOCAL_EVENT_OUTPUT" \
  "$EVENTS" \
  "$OUTPUT_BASENAME" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
events = int(sys.argv[2])
sample = sys.argv[3]

text = path.read_text(encoding="utf-8")

text, n_events_count = re.subn(
    r"(?m)^\s*n_events\s*=\s*\d+\s*$",
    f"  n_events = {events}",
    text,
    count=1,
)

text, sample_count = re.subn(
    r'(?m)^\s*\$sample\s*=\s*"[^"]*"\s*$',
    f'  $sample = "{sample}"',
    text,
    count=1,
)

if n_events_count != 1:
    raise SystemExit(
        f"ERROR: expected one n_events assignment in {path}, "
        f"replaced {n_events_count}"
    )

if sample_count != 1:
    raise SystemExit(
        f"ERROR: expected one sample assignment in {path}, "
        f"replaced {sample_count}"
    )

path.write_text(text, encoding="utf-8")
PY

python3 - \
  "$LOCAL_PROCESS_CARD" \
  "$LOCAL_INTEGRATION" \
  "$LOCAL_EVENT_OUTPUT" \
  "$WHIZARD_SEED" \
  "$ITERATIONS" \
  "$EVENTS" \
  "$OUTPUT_BASENAME" <<'PY_VALIDATE_EFFECTIVE'
from __future__ import annotations

import re
import sys
from pathlib import Path

(
    process_path,
    integration_path,
    event_output_path,
    requested_seed,
    requested_iterations,
    requested_events,
    requested_sample,
) = sys.argv[1:]

process = Path(process_path).read_text(encoding="utf-8")
integration = Path(integration_path).read_text(encoding="utf-8")
event_output = Path(event_output_path).read_text(encoding="utf-8")

failures: list[str] = []

required_process_includes = (
    "model.inc",
    "beams.inc",
    "isr.inc",
    "integration.inc",
    "event_output.inc",
)

for filename in required_process_includes:
    marker = f'include("common/{filename}")'

    if process.count(marker) != 1:
        failures.append(
            f"expected one localized include {marker}, "
            f"found {process.count(marker)}"
        )

polarization_marker = 'include("common/polarization.inc")'
polarization_count = process.count(polarization_marker)

if polarization_count not in {0, 1}:
    failures.append(
        "expected zero or one localized polarization include, "
        f"found {polarization_count}"
    )

if "/sindarin/generated/" in process:
    failures.append(
        "absolute generated-tree include remains in process.sin"
    )

seed_pattern = re.compile(
    r"(?m)^\s*seed\s*=\s*(\d+)\s*$"
)
seed_matches = seed_pattern.findall(integration)

if seed_matches != [requested_seed]:
    failures.append(
        f"integration seed mismatch: {seed_matches} != "
        f"[{requested_seed!r}]"
    )

iterations_pattern = re.compile(
    r"(?m)^\s*iterations\s*=\s*(.+?)\s*$"
)
iteration_matches = iterations_pattern.findall(integration)

if iteration_matches != [requested_iterations]:
    failures.append(
        f"integration setting mismatch: {iteration_matches} != "
        f"[{requested_iterations!r}]"
    )

if "integrate (" not in integration:
    failures.append("integration include has no integrate statement")
else:
    seed_position = integration.find(
        f"seed = {requested_seed}"
    )
    integrate_position = integration.find("integrate (")

    if seed_position < 0 or seed_position >= integrate_position:
        failures.append(
            "effective seed does not precede integration"
        )

events_pattern = re.compile(
    r"(?m)^\s*n_events\s*=\s*(\d+)\s*$"
)
event_matches = events_pattern.findall(event_output)

if event_matches != [requested_events]:
    failures.append(
        f"event-count mismatch: {event_matches} != "
        f"[{requested_events!r}]"
    )

sample_pattern = re.compile(
    r'(?m)^\s*\$sample\s*=\s*"([^"]+)"\s*$'
)
sample_matches = sample_pattern.findall(event_output)

if sample_matches != [requested_sample]:
    failures.append(
        f"sample-basename mismatch: {sample_matches} != "
        f"[{requested_sample!r}]"
    )

if failures:
    print("FULL6F_EFFECTIVE_CARD_VALIDATION=FAIL")

    for failure in failures:
        print(f"  {failure}")

    raise SystemExit(1)

print("FULL6F_EFFECTIVE_CARD_VALIDATION=PASS")
print(f"WHIZARD_SEED={requested_seed}")
print(f"ITERATIONS={requested_iterations}")
print(f"EVENTS={requested_events}")
print(f"SAMPLE_BASENAME={requested_sample}")
PY_VALIDATE_EFFECTIVE

cp -a "$SCRATCH_DIR/process.sin" "$RUN_DIR/effective_process.sin"
cp -a "$SCRATCH_DIR/common" "$RUN_DIR/effective_common"
cp -a "$SCRATCH_DIR/render_context.json" "$RUN_DIR/render_context.json"

printf '%s\n' "$WHIZARD_VERSION_LINE" \
  > "$RUN_DIR/whizard_version.txt"

WHIZARD_REALPATH="$(readlink -f "$(command -v whizard)")"
printf '%s\n' "$WHIZARD_REALPATH" \
  > "$RUN_DIR/whizard_binary.txt"

CONSOLE_LOG="$RUN_DIR/console.log"
TIMEOUT_SECONDS=$(( TIMEOUT_MINUTES * 60 ))

set +e
(
  cd "$SCRATCH_DIR" || exit 1

  if command -v timeout >/dev/null 2>&1; then
    timeout --signal=TERM --kill-after=60 \
      "$TIMEOUT_SECONDS" \
      whizard process.sin
  else
    whizard process.sin
  fi
) 2>&1 | tee "$CONSOLE_LOG"

WHIZARD_RC=${PIPESTATUS[0]}
set -e

printf '%s\n' "$WHIZARD_RC" \
  > "$RUN_DIR/whizard_return_code.txt"

LOCAL_LHE="$SCRATCH_DIR/${OUTPUT_BASENAME}.lhe"

if [[ "$WHIZARD_RC" -ne 0 ]]; then
  echo "ERROR: WHIZARD failed with rc=$WHIZARD_RC" >&2
  exit "$WHIZARD_RC"
fi

if [[ ! -s "$LOCAL_LHE" ]]; then
  echo "ERROR: WHIZARD completed but raw LHE is missing: $LOCAL_LHE" >&2
  exit 1
fi

GENERATED_EVENTS="$(
  grep -c '<event>' "$LOCAL_LHE" || true
)"

if [[ "$GENERATED_EVENTS" -ne "$EVENTS" ]]; then
  echo "ERROR: generated event count mismatch" >&2
  echo "Requested: $EVENTS" >&2
  echo "Observed:  $GENERATED_EVENTS" >&2
  exit 1
fi

TEMP_RAW_LHE="${RAW_LHE}.tmp.$$"
cp -a "$LOCAL_LHE" "$TEMP_RAW_LHE"
mv -f "$TEMP_RAW_LHE" "$RAW_LHE"

LHE_SHA256="$(sha256sum "$RAW_LHE" | awk '{print $1}')"
SOURCE_CARD_SHA256="$(sha256sum "$SOURCE_CARD" | awk '{print $1}')"
EFFECTIVE_CARD_SHA256="$(sha256sum "$RUN_DIR/effective_process.sin" | awk '{print $1}')"
EFFECTIVE_INTEGRATION_SHA256="$(
  sha256sum "$RUN_DIR/effective_common/integration.inc" \
    | awk '{print $1}'
)"

END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

python3 - \
  "$METADATA" \
  "$CAMPAIGN_ID" \
  "$SAMPLE_ID" \
  "$SUBPROCESS_ID" \
  "$SHARD_INDEX" \
  "$SHARD_LABEL" \
  "$WHIZARD_SEED" \
  "$EVENTS" \
  "$GENERATED_EVENTS" \
  "$ITERATIONS" \
  "$SOURCE_CARD" \
  "$SOURCE_CARD_SHA256" \
  "$RUN_DIR/effective_process.sin" \
  "$EFFECTIVE_CARD_SHA256" \
  "$RUN_DIR/effective_common/integration.inc" \
  "$EFFECTIVE_INTEGRATION_SHA256" \
  "$RAW_LHE" \
  "$LHE_SHA256" \
  "$WHIZARD_VERSION_LINE" \
  "$WHIZARD_REALPATH" \
  "$START_UTC" \
  "$END_UTC" \
  "$HOSTNAME_VALUE" \
  "$SCRATCH_DIR" \
  "$ARCHIVE_WORKSPACE" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

(
    output,
    campaign_id,
    sample_id,
    subprocess_id,
    shard_index,
    shard_label,
    whizard_seed,
    requested_events,
    generated_events,
    iterations,
    source_card,
    source_card_sha256,
    effective_card,
    effective_card_sha256,
    effective_integration,
    effective_integration_sha256,
    raw_lhe,
    raw_lhe_sha256,
    whizard_version,
    whizard_binary,
    start_utc,
    end_utc,
    hostname,
    scratch_directory,
    archive_workspace,
) = sys.argv[1:]

payload = {
    "schema_version": 1,
    "status": "success",
    "production_mode": "direct_full_six_fermion",
    "campaign_id": campaign_id,
    "sample_id": sample_id,
    "subprocess_id": subprocess_id,
    "shard_index": int(shard_index),
    "shard_label": shard_label,
    "random_streams": {
        "whizard_seed": int(whizard_seed),
        "pythia_seed": None,
    },
    "requested_events": int(requested_events),
    "generated_events": int(generated_events),
    "integration_iterations": iterations,
    "source_card": source_card,
    "source_card_sha256": source_card_sha256,
    "effective_card": effective_card,
    "effective_card_sha256": effective_card_sha256,
    "effective_integration_include": effective_integration,
    "effective_integration_include_sha256": (
        effective_integration_sha256
    ),
    "raw_lhe": raw_lhe,
    "raw_lhe_sha256": raw_lhe_sha256,
    "runtime": {
        "whizard_version": whizard_version,
        "whizard_binary": whizard_binary,
        "required_whizard_version": "3.1.8",
    },
    "start_utc": start_utc,
    "end_utc": end_utc,
    "hostname": hostname,
    "scratch_directory": scratch_directory,
    "archive_workspace": bool(int(archive_workspace)),
}

path = Path(output)
path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

{
  sha256sum \
    "$RUN_DIR/effective_process.sin" \
    "$RUN_DIR/effective_common/integration.inc" \
    "$RUN_DIR/effective_common/event_output.inc" \
    "$RUN_DIR/render_context.json" \
    "$RUN_DIR/whizard_version.txt" \
    "$RUN_DIR/whizard_binary.txt" \
    "$CONSOLE_LOG" \
    "$METADATA" \
    "$RAW_LHE"
} > "$RUN_DIR/SHA256SUMS.txt"

touch "$SUCCESS_MARKER"

echo "Completed $SAMPLE_ID/$SUBPROCESS_ID/$SHARD_LABEL"
echo "events=$GENERATED_EVENTS"
echo "whizard_seed=$WHIZARD_SEED"
echo "Run metadata: $METADATA"
echo "Raw LHE: $RAW_LHE"
