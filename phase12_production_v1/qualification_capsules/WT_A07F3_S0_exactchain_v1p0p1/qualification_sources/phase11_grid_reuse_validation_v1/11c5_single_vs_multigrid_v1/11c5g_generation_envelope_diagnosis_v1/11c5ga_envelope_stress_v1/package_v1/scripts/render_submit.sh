#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  render_submit.sh \
    --subdir DIR \
    --output-root DIR \
    --repo DIR \
    --worker FILE \
    --source-card FILE \
    --itemdata FILE
EOF
}

SUBDIR=""
OUTPUT_ROOT=""
REPO=""
WORKER=""
SOURCE_CARD=""
ITEMDATA=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --subdir) SUBDIR=$2; shift 2 ;;
    --output-root) OUTPUT_ROOT=$2; shift 2 ;;
    --repo) REPO=$2; shift 2 ;;
    --worker) WORKER=$2; shift 2 ;;
    --source-card) SOURCE_CARD=$2; shift 2 ;;
    --itemdata) ITEMDATA=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg $1" >&2; usage >&2; exit 2 ;;
  esac
done

for V in SUBDIR OUTPUT_ROOT REPO WORKER SOURCE_CARD ITEMDATA; do
  [[ -n "${!V}" ]] || { echo "ERROR: missing $V" >&2; exit 2; }
done

mkdir -p "$SUBDIR/logs" "$SUBDIR/dryruns"

cat > "$SUBDIR/c5ga_stress.sub" <<EOF
universe = vanilla

executable = $WORKER

arguments = \
  --repo $REPO \
  --mode \$(mode) \
  --checkpoint-kind \$(checkpoint_kind) \
  --workspace-tar \$(workspace_tar) \
  --expected-vg2-sha \$(vg2_sha) \
  --expected-phs-sha \$(phs_sha) \
  --source-card $SOURCE_CARD \
  --output-root $OUTPUT_ROOT \
  --grid-seed \$(grid_seed) \
  --pre-integration-seed \$(shard_seed) \
  --generation-seed \$(metadata_seed) \
  --events \$(events)

initialdir = $SUBDIR

should_transfer_files = NO
getenv = False

request_cpus = 1
request_memory = 3000MB
request_disk = 3000MB

+JobFlavour = "workday"

output = logs/\$(mode).\$(ClusterId).\$(ProcId).out
error  = logs/\$(mode).\$(ClusterId).\$(ProcId).err
log    = condor.log

notification = Never

queue mode, grid_label, checkpoint_kind, workspace_tar, vg2_sha, phs_sha, grid_seed, shard_seed, metadata_seed, events from $ITEMDATA
EOF

printf 'C5GA_SUBMIT_FILE=%s\n' "$SUBDIR/c5ga_stress.sub"
echo "C5GA_RENDER_SUBMIT=PASS"
