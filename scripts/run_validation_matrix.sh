#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_validation_matrix.sh [options]

Options:
  --dry-run                  Print selected samples without invoking WHIZARD.
  --force                    Replace existing non-empty sample workspaces.
  --continue-on-error        Run remaining samples after a failure.
  --initial-state ee|mumu    Restrict the initial state.
  --spin sc|iso              Restrict the spin mode.
  --polarization VALUE       Restrict to unpol, LR100, or RL100.
  -h, --help                 Show this help.
EOF
}

DRY_RUN=0
FORCE=0
CONTINUE_ON_ERROR=0
INITIAL_FILTER=''
SPIN_FILTER=''
POL_FILTER=''

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --continue-on-error) CONTINUE_ON_ERROR=1; shift ;;
    --initial-state) INITIAL_FILTER=${2:-}; shift 2 ;;
    --spin) SPIN_FILTER=${2:-}; shift 2 ;;
    --polarization) POL_FILTER=${2:-}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -n "$INITIAL_FILTER" && "$INITIAL_FILTER" != ee && "$INITIAL_FILTER" != mumu ]]; then
  echo "ERROR: --initial-state must be ee or mumu" >&2
  exit 2
fi
if [[ -n "$SPIN_FILTER" && "$SPIN_FILTER" != sc && "$SPIN_FILTER" != iso ]]; then
  echo "ERROR: --spin must be sc or iso" >&2
  exit 2
fi
if [[ -n "$POL_FILTER" && "$POL_FILTER" != unpol && "$POL_FILTER" != LR100 && "$POL_FILTER" != RL100 ]]; then
  echo "ERROR: --polarization must be unpol, LR100, or RL100" >&2
  exit 2
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

mapfile -t ALL_FILES < <(find "$REPO_ROOT/sindarin" -type f -name '*.sin' | sort)
SELECTED=()
for sin in "${ALL_FILES[@]}"; do
  base=$(basename "$sin" .sin)
  initial=$(basename "$(dirname "$sin")")
  [[ -n "$INITIAL_FILTER" && "$initial" != "$INITIAL_FILTER" ]] && continue
  [[ -n "$SPIN_FILTER" && "$base" != *"_${SPIN_FILTER}_500GeV" ]] && continue
  [[ -n "$POL_FILTER" && "$base" != *"_${POL_FILTER}_"* ]] && continue
  SELECTED+=("$sin")
done

if [[ ${#SELECTED[@]} -eq 0 ]]; then
  echo "ERROR: no SINDARIN files match the selected filters." >&2
  exit 3
fi

echo "Selected ${#SELECTED[@]} sample(s)."
FAILURES=0
for sin in "${SELECTED[@]}"; do
  echo
  echo "======================================================================"
  echo "Running: $(basename "$sin")"
  echo "======================================================================"
  args=()
  [[ $DRY_RUN -eq 1 ]] && args+=(--dry-run)
  [[ $FORCE -eq 1 ]] && args+=(--force)

  set +e
  "$SCRIPT_DIR/run_one.sh" "${args[@]}" "$sin"
  rc=$?
  set -e

  if [[ $rc -ne 0 ]]; then
    FAILURES=$((FAILURES + 1))
    echo "FAILED: $(basename "$sin") (exit $rc)" >&2
    if [[ $CONTINUE_ON_ERROR -eq 0 ]]; then
      break
    fi
  fi
done

python3 "$SCRIPT_DIR/make_sample_manifest.py" --repo-root "$REPO_ROOT"
if [[ $DRY_RUN -eq 0 ]]; then
  python3 "$SCRIPT_DIR/validate_cross_sections.py" --repo-root "$REPO_ROOT" || true
fi

if [[ $FAILURES -ne 0 ]]; then
  echo "Validation matrix completed with $FAILURES failure(s)." >&2
  exit 1
fi

echo "Validation matrix completed successfully."
