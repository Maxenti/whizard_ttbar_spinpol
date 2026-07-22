#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/qis/run_365GeV_lhe_matrix_local.sh --campaign-root PATH [options]

Options:
  --repo-root PATH       Repository root (default: inferred)
  --campaign-root PATH   Prepared campaign root
  --rerun                Regenerate already completed samples
  --continue-on-error    Continue after a failed point and report failures
  -h, --help             Show this help
EOF
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$SCRIPT_DIR/../.." && pwd)
CAMPAIGN_ROOT=
RERUN=0
CONTINUE_ON_ERROR=0

while (($#)); do
  case "$1" in
    --repo-root) REPO=$2; shift 2 ;;
    --campaign-root) CAMPAIGN_ROOT=$2; shift 2 ;;
    --rerun) RERUN=1; shift ;;
    --continue-on-error) CONTINUE_ON_ERROR=1; shift ;;
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

mapfile -t SAMPLE_IDS < "$CAMPAIGN_ROOT/sample_ids.txt"
failures=()
for sample_id in "${SAMPLE_IDS[@]}"; do
  args=(
    --repo-root "$REPO"
    --campaign-root "$CAMPAIGN_ROOT"
    --sample-id "$sample_id"
  )
  if ((RERUN)); then
    args+=(--rerun)
  fi
  if ! bash "$REPO/scripts/qis/run_365GeV_lhe_point.sh" "${args[@]}"; then
    failures+=("$sample_id")
    if ((CONTINUE_ON_ERROR == 0)); then
      exit 1
    fi
  fi
done

if ((${#failures[@]})); then
  printf 'FAILED: %s\n' "${failures[@]}" >&2
  exit 1
fi

echo "All ${#SAMPLE_IDS[@]} LHE matrix points passed."
