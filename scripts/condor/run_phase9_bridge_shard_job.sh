#!/usr/bin/env bash
set -uo pipefail

REPO="${1:?missing REPO}"
MANIFEST="${2:?missing MANIFEST}"
PROC_ID="${3:?missing PROC_ID}"
OUT_ARG="${4:?missing OUT_DIR_OR_TAG}"
TIMEOUT_MINUTES="${5:-45}"

# Standard CERN batch schedds must not use /eos paths directly in the submit
# description.  For Condor production, pass a short output tag and reconstruct
# the EOS output path inside the job.  Direct absolute paths remain supported
# for manual/local tests.
if [[ "$OUT_ARG" == /* ]]; then
  OUT_DIR="$OUT_ARG"
else
  OUT_DIR="/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/$OUT_ARG"
fi

export REPO MANIFEST PROC_ID OUT_ARG OUT_DIR TIMEOUT_MINUTES

mkdir -p \
  "$OUT_DIR/logs" \
  "$OUT_DIR/status" \
  "$OUT_DIR/records" \
  "$OUT_DIR/summaries"

source "$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh"

cd "$REPO" || exit 2

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export BLAS_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

RECORD_JSON="$OUT_DIR/records/record_${PROC_ID}.json"
ENV_FILE="$OUT_DIR/records/record_${PROC_ID}.env"

python3 - "$MANIFEST" "$PROC_ID" "$RECORD_JSON" > "$ENV_FILE" <<'PY'
import json
import shlex
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
proc_id = int(sys.argv[2])
record_json = Path(sys.argv[3])

records = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]

if proc_id < 0 or proc_id >= len(records):
    raise SystemExit(f"ERROR: ProcId {proc_id} outside manifest length {len(records)}")

record = records[proc_id]
record_json.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

required = [
    "card",
    "label",
    "sample_id",
    "campaign_id",
    "shard_id",
    "events",
    "iterations",
    "seed",
    "pythia_profile",
]
missing = [key for key in required if key not in record]
if missing:
    raise SystemExit(f"ERROR: manifest record missing required keys: {missing}")

mapping = {
    "CARD": record["card"],
    "LABEL": record["label"],
    "SAMPLE_ID": record["sample_id"],
    "CAMPAIGN_ID": record["campaign_id"],
    "SHARD_ID": record["shard_id"],
    "EVENTS": record["events"],
    "ITERATIONS": record["iterations"],
    "SEED": record["seed"],
    "PYTHIA_PROFILE": record["pythia_profile"],
    "PARENT_LABEL": record.get("parent_label", record["label"]),
    "SHARD_INDEX": record.get("shard_index", proc_id),
}

for key, value in mapping.items():
    print(f"export {key}={shlex.quote(str(value))}")
PY

EXTRACT_RC=$?
if [[ "$EXTRACT_RC" -ne 0 ]]; then
  STATUS_JSON="$OUT_DIR/status/job_${PROC_ID}_extract_failed.status.json"
  export STATUS_JSON EXTRACT_RC

  python3 - <<'PY'
import json
import os
from pathlib import Path

Path(os.environ["STATUS_JSON"]).write_text(
    json.dumps(
        {
            "proc_id": int(os.environ.get("PROC_ID", "-1")),
            "stage": "record_extract",
            "return_code": int(os.environ.get("EXTRACT_RC", "1")),
            "status": "FAIL",
        },
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)
PY

  exit "$EXTRACT_RC"
fi

source "$ENV_FILE"

export CARD LABEL SAMPLE_ID CAMPAIGN_ID SHARD_ID EVENTS ITERATIONS SEED PYTHIA_PROFILE PARENT_LABEL SHARD_INDEX

SAFE_LABEL="$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9_.-' '_')"
JOB_LOG="$OUT_DIR/logs/job_${PROC_ID}_${SAFE_LABEL}.log"
STATUS_JSON="$OUT_DIR/status/job_${PROC_ID}_${SAFE_LABEL}.status.json"

export JOB_LOG STATUS_JSON

{
  echo "===================================================================================================="
  echo "PHASE9_CONDOR_SHARD_JOB"
  echo "HOST=$(hostname)"
  echo "DATE_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "REPO=$REPO"
  echo "MANIFEST=$MANIFEST"
  echo "PROC_ID=$PROC_ID"
  echo "LABEL=$LABEL"
  echo "PARENT_LABEL=$PARENT_LABEL"
  echo "SHARD_INDEX=$SHARD_INDEX"
  echo "EVENTS=$EVENTS"
  echo "ITERATIONS=$ITERATIONS"
  echo "SEED=$SEED"
  echo "PYTHIA_PROFILE=$PYTHIA_PROFILE"
  echo "TIMEOUT_MINUTES=$TIMEOUT_MINUTES"
  echo "OUT_DIR=$OUT_DIR"
  echo "===================================================================================================="

  python3 "$REPO/scripts/showering/run_phase7_canonical_bridge.py" \
    --repo "$REPO" \
    --card "$CARD" \
    --label "$LABEL" \
    --sample-id "$SAMPLE_ID" \
    --campaign-id "$CAMPAIGN_ID" \
    --shard-id "$SHARD_ID" \
    --events "$EVENTS" \
    --iterations "$ITERATIONS" \
    --seed "$SEED" \
    --pythia-profile "$PYTHIA_PROFILE" \
    --timeout-whizard-minutes "$TIMEOUT_MINUTES"
} 2>&1 | tee "$JOB_LOG"

RUN_RC=${PIPESTATUS[0]}
export RUN_RC

RUN_DIR="$(
  grep -h 'PHASE7_BRIDGE_RUNNER_RUN_DIR=' "$JOB_LOG" 2>/dev/null \
    | tail -1 \
    | sed 's/^PHASE7_BRIDGE_RUNNER_RUN_DIR=//'
)"
export RUN_DIR

SUMMARY_COPY=""
if [[ -n "$RUN_DIR" && -f "$RUN_DIR/phase7_bridge_summary.json" ]]; then
  SUMMARY_COPY="$OUT_DIR/summaries/job_${PROC_ID}_${SAFE_LABEL}.phase7_bridge_summary.json"
  cp "$RUN_DIR/phase7_bridge_summary.json" "$SUMMARY_COPY"
fi
export SUMMARY_COPY

python3 - <<'PY'
import json
import os
from pathlib import Path

status = {
    "proc_id": int(os.environ["PROC_ID"]),
    "label": os.environ.get("LABEL"),
    "parent_label": os.environ.get("PARENT_LABEL"),
    "shard_index": int(os.environ.get("SHARD_INDEX", "-1")),
    "events": int(os.environ.get("EVENTS", "-1")),
    "iterations": os.environ.get("ITERATIONS"),
    "seed": int(os.environ.get("SEED", "-1")),
    "pythia_profile": os.environ.get("PYTHIA_PROFILE"),
    "timeout_minutes": int(os.environ.get("TIMEOUT_MINUTES", "-1")),
    "return_code": int(os.environ["RUN_RC"]),
    "run_dir": os.environ.get("RUN_DIR"),
    "job_log": os.environ.get("JOB_LOG"),
    "summary_copy": os.environ.get("SUMMARY_COPY"),
}

summary_path = os.environ.get("SUMMARY_COPY")
if summary_path and Path(summary_path).is_file():
    try:
        child = json.loads(Path(summary_path).read_text(encoding="utf-8"))
        status["runner_status"] = child.get("status")
        status["event_counts"] = child.get("event_counts")
        status["warning_counts"] = child.get("warning_counts")
        status["errors"] = child.get("errors", [])
        status["warnings"] = child.get("warnings", [])
    except Exception as exc:
        status["summary_parse_error"] = str(exc)

if status["return_code"] == 0 and status.get("runner_status") in {"PASS", "PASS_WITH_RUNTIME_WARNINGS"}:
    status["status"] = "PASS"
else:
    status["status"] = "FAIL"

Path(os.environ["STATUS_JSON"]).write_text(
    json.dumps(status, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

echo "PHASE9_CONDOR_SHARD_STATUS_JSON=$STATUS_JSON"
echo "PHASE9_CONDOR_SHARD_RUN_RC=$RUN_RC"

exit "$RUN_RC"
