#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/qis/submit_365GeV_lhe_matrix.sh --campaign-root PATH [options]

Options:
  --repo-root PATH         Repository root (default: inferred)
  --campaign-root PATH     Prepared campaign root, preferably through the AFS-visible runs path
  --config PATH            Matrix YAML
  --job-flavour NAME       Override configured CERN JobFlavour
  --submit-only            Write descriptor but do not call condor_submit
  --rerun                  Pass --rerun to every point job
  -h, --help               Show this help
USAGE
}

SCRIPT_DIR=$(cd -L "$(dirname "${BASH_SOURCE[0]}")" && pwd -L)
REPO=$(cd -L "$SCRIPT_DIR/../.." && pwd -L)
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

# Preserve logical AFS-visible paths.  In this repository, runs/ may be a
# symlink into EOS.  CERN standard schedds accept the /afs path in a submit
# file but reject the resolved /eos path.  Therefore do not use cd -P,
# realpath, or readlink -f for any path written into the descriptor.
REPO=$(cd -L "$REPO" && pwd -L)
if [[ $CAMPAIGN_ROOT != /* ]]; then
  CAMPAIGN_ROOT="$REPO/$CAMPAIGN_ROOT"
fi
if [[ ! -d $CAMPAIGN_ROOT ]]; then
  echo "ERROR: campaign root does not exist: $CAMPAIGN_ROOT" >&2
  exit 1
fi
CAMPAIGN_ROOT=$(cd -L "$CAMPAIGN_ROOT" && pwd -L)

if [[ $CONFIG != /* ]]; then
  CONFIG="$REPO/$CONFIG"
fi
if [[ ! -f $CONFIG ]]; then
  echo "ERROR: matrix config does not exist: $CONFIG" >&2
  exit 1
fi

# Standard CERN schedds reject literal /eos paths in submit descriptors.
# Users should pass the AFS-visible repository path, whose runs symlink can
# still point to EOS.  This guard catches accidental direct-EOS invocation.
for submit_visible_path in "$REPO" "$CAMPAIGN_ROOT" "$CONFIG"; do
  if [[ $submit_visible_path == /eos/* ]]; then
    cat >&2 <<EOF_ERROR
ERROR: standard CERN batch schedds cannot use a literal /eos path in this submit file:
  $submit_visible_path
Use the AFS-visible repository path instead, for example:
  $REPO/runs/<campaign>
The runs symlink may still resolve physically to EOS.
EOF_ERROR
    exit 1
  fi
done

MANIFEST="$CAMPAIGN_ROOT/campaign_manifest.json"
SAMPLE_LIST="$CAMPAIGN_ROOT/sample_ids.txt"
if [[ ! -f $MANIFEST ]]; then
  echo "ERROR: missing campaign manifest: $MANIFEST" >&2
  exit 1
fi
if [[ ! -f $SAMPLE_LIST ]]; then
  echo "ERROR: missing sample list: $SAMPLE_LIST" >&2
  exit 1
fi

mapfile -t SETTINGS < <(
  python3 - "$CONFIG" "$MANIFEST" <<'PY'
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
STDOUT_DIR="$CONDOR_DIR/stdout"
STDERR_DIR="$CONDOR_DIR/stderr"
mkdir -p "$CONDOR_DIR" "$STDOUT_DIR" "$STDERR_DIR"

# Fail before submission if the access point cannot create files through the
# exact logical paths named by output/error/log.
for directory in "$CONDOR_DIR" "$STDOUT_DIR" "$STDERR_DIR"; do
  probe="$directory/.write_probe_$$"
  if ! : > "$probe"; then
    echo "ERROR: Condor output directory is not writable: $directory" >&2
    exit 1
  fi
  rm -f "$probe"
done

SUBMIT_FILE="$CONDOR_DIR/lhe_matrix.sub"
EXTRA_ARGS=
if ((RERUN)); then
  EXTRA_ARGS=' --rerun'
fi

cat > "$SUBMIT_FILE" <<EOF_SUBMIT
universe = vanilla
executable = $REPO/scripts/qis/run_365GeV_lhe_point.sh
arguments = --repo-root $REPO --campaign-root $CAMPAIGN_ROOT --sample-id \$(sample_id)$EXTRA_ARGS

initialdir = $REPO
getenv = $GETENV
should_transfer_files = $TRANSFER

request_cpus = $REQUEST_CPUS
request_memory = $REQUEST_MEMORY
request_disk = $REQUEST_DISK

output = $STDOUT_DIR/\$(sample_id).out
error = $STDERR_DIR/\$(sample_id).err
log = $CONDOR_DIR/cluster.log

+JobFlavour = "$JOB_FLAVOUR"

queue sample_id from $SAMPLE_LIST
EOF_SUBMIT

# Assert that the generated descriptor has no literal EOS path before asking
# condor_submit to parse it.
if grep -nE '(^|[[:space:]="])\/eos\/' "$SUBMIT_FILE"; then
  echo "ERROR: generated submit descriptor contains a literal /eos path" >&2
  exit 1
fi

PHYSICAL_CAMPAIGN_ROOT=$(cd -P "$CAMPAIGN_ROOT" && pwd -P)
SAMPLE_COUNT=$(grep -cve '^[[:space:]]*$' "$SAMPLE_LIST")

printf '%s\n' \
  "Prepared Condor descriptor:" \
  "  $SUBMIT_FILE" \
  "Samples: $SAMPLE_COUNT" \
  "JobFlavour: $JOB_FLAVOUR" \
  "Submit-visible campaign root: $CAMPAIGN_ROOT" \
  "Physical campaign root (diagnostic only): $PHYSICAL_CAMPAIGN_ROOT" \
  "Stdout directory: $STDOUT_DIR" \
  "Stderr directory: $STDERR_DIR"

if ((SUBMIT_ONLY)); then
  exit 0
fi

if ! command -v condor_submit >/dev/null 2>&1; then
  echo "ERROR: condor_submit is not available" >&2
  exit 1
fi

condor_submit "$SUBMIT_FILE" | tee "$CONDOR_DIR/submit_output.txt"
