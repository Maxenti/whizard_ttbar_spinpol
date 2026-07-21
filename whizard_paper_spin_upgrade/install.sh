#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
PATCH_GATE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO=$2; shift 2 ;;
    --patch-gate) PATCH_GATE=1; shift ;;
    -h|--help)
      cat <<EOF
Usage: $0 [--repo PATH] [--patch-gate]

Installs the additive overlay. Existing colliding files are backed up.
The validated output tree is never modified. --patch-gate optionally adds an
early 'paper-spin' dispatch to run_next_production_gate.sh.
EOF
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

REPO=$(readlink -f "$REPO")
[[ -d "$REPO" ]] || { echo "Missing repository: $REPO" >&2; exit 1; }

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP="$REPO/backups/paper_spin_upgrade_$STAMP"
OVERLAY="$BUNDLE_DIR/repo_overlay"
mkdir -p "$BACKUP"

while IFS= read -r -d '' source; do
  relative=${source#"$OVERLAY"/}
  destination="$REPO/$relative"
  if [[ -e "$destination" ]]; then
    mkdir -p "$BACKUP/$(dirname "$relative")"
    cp -a "$destination" "$BACKUP/$relative"
  fi
  mkdir -p "$(dirname "$destination")"
  cp -a "$source" "$destination"
done < <(find "$OVERLAY" -type f -print0)

find "$REPO/scripts/qis" -maxdepth 2 -type f \( -name '*.py' -o -name '*.sh' \) -exec chmod +x {} +

if [[ "$PATCH_GATE" == "1" ]]; then
  python3 "$REPO/scripts/qis/patch_run_next_gate.py" --repo "$REPO"
fi

cat > "$REPO/PAPER_SPIN_UPGRADE_INSTALLED.txt" <<EOF
Installed UTC: $STAMP
Bundle: $BUNDLE_DIR
Backup: $BACKUP
Baseline output trees modified: no
Optional run_next gate patch: $PATCH_GATE
EOF

echo "Installed additive paper-spin upgrade"
echo "Repository: $REPO"
echo "Backup:     $BACKUP"
echo
echo "Validate syntax and tests with:"
echo "  cd $REPO"
echo "  source setup_lxplus.sh"
echo "  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/qis/test_paper_spin_*.py"
