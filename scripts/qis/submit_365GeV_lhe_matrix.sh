#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/qis/submit_365GeV_lhe_matrix.sh --campaign-root PATH [options]

Options:
  --repo-root PATH         Repository root (default: inferred)
  --campaign-root PATH     Prepared campaign root
  --config PATH            Matrix YAML
  --job-flavour NAME       Override configured CERN JobFlavour
  --submit-only            Write descriptor but do not call condor_submit
  --rerun                  Pass --rerun to every point job
  -h, --help               Show this help
EOF
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$SCRIPT_DIR/../.." && pwd)
CAMPAIGN_ROOT=
CONFIG=configs/qis/paper_spin_365GeV_lhe_matrix.yaml
JOB_FLAVOUR=
SUBMIT_ONLY=0
RERUN=0

while (($#)); do
  case "$1" in
    --repo-root) REPO=$2; shift 2 ;;
    --campaign-root) CAMPAIGN_ROOT=$2; shift 2 ;;
    --config) CONFIG=$2; shift 2 ;;
    --job-flavour) JOB_FLAVOUR=$2; shift 2 ;;
    --submit-only) SUBMIT_ONLY=1; shift ;;
    --rerun) RERUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z $CAMPAIGN_ROOT ]]; then
  echo "ERROR: --campaign-root is required" >&2
  exit 2
fi

REPO=$(cd "$REPO" && pwd)
if [[ $CAMPAIGN_ROOT != /* ]]; then
  CAMPAIGN_ROOT="$REPO/$CAMPAIGN_ROOT"
fi
CAMPAIGN_ROOT=$(cd "$CAMPAIGN_ROOT" && pwd)
if [[ $CONFIG != /* ]]; then
  CONFIG="$REPO/$CONFIG"
fi

mapfile -t SETTINGS < <(
  python3 - "$CONFIG" "$CAMPAIGN_ROOT/campaign_manifest.json" <<'PY'
import json
import sys
from pathlib import Path
import yaml

config = yaml.safe_load(Path(sys.argv[1]).read_text())
manifest = json.loads(Path(sys.argv[2]).read_text())
profile = config["profiles"][manifest["profile"]]
condor = config["condor"]
print(profile["condor_job_flavour"])
print(condor["request_cpus"])
print(condor["request_memory"])
print(condor["request_disk"])
print(str(condor.get("getenv", True)).lower())
print(condor.get("should_transfer_files", "NO"))
PY
)

if [[ -z $JOB_FLAVOUR ]]; then
  JOB_FLAVOUR=${SETTINGS[0]}
fi
REQUEST_CPUS=${SETTINGS[1]}
REQUEST_MEMORY=${SETTINGS[2]}
REQUEST_DISK=${SETTINGS[3]}
GETENV=${SETTINGS[4]}
TRANSFER=${SETTINGS[5]}

CONDOR_DIR="$CAMPAIGN_ROOT/condor"
mkdir -p "$CONDOR_DIR" "$CAMPAIGN_ROOT/logs"
SUBMIT_FILE="$CONDOR_DIR/lhe_matrix.sub"
EXTRA_ARGS=
if ((RERUN)); then
  EXTRA_ARGS=' --rerun'
fi

cat > "$SUBMIT_FILE" <<EOF
universe = vanilla
executable = $REPO/scripts/qis/run_365GeV_lhe_point.sh
arguments = --repo-root $REPO --campaign-root $CAMPAIGN_ROOT --sample-id \$(sample_id)$EXTRA_ARGS

initialdir = $REPO
getenv = $GETENV
should_transfer_files = $TRANSFER

request_cpus = $REQUEST_CPUS
request_memory = $REQUEST_MEMORY
request_disk = $REQUEST_DISK

output = $CAMPAIGN_ROOT/logs/\$(sample_id).out
error = $CAMPAIGN_ROOT/logs/\$(sample_id).err
log = $CONDOR_DIR/cluster.log

+JobFlavour = "$JOB_FLAVOUR"

queue sample_id from $CAMPAIGN_ROOT/sample_ids.txt
EOF

printf '%s\n' \
  "Prepared Condor descriptor:" \
  "  $SUBMIT_FILE" \
  "Samples: 16" \
  "JobFlavour: $JOB_FLAVOUR"

if ((SUBMIT_ONLY)); then
  exit 0
fi

if ! command -v condor_submit >/dev/null 2>&1; then
  echo "ERROR: condor_submit is not available" >&2
  exit 1
fi

condor_submit "$SUBMIT_FILE" | tee "$CONDOR_DIR/submit_output.txt"
