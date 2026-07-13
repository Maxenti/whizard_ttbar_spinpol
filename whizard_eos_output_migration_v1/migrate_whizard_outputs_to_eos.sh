#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  migrate_whizard_outputs_to_eos.sh [--apply]

Without --apply, print the resolved plan and perform no changes.
With --apply:
  1. Copy runs/lhe/logs/metadata/validation from AFS to EOS.
  2. Verify each copy with checksum-aware rsync dry runs.
  3. Rename the original AFS directories to timestamped backups.
  4. Replace them with symlinks to EOS.

The timestamped AFS backups are NOT deleted automatically.
USAGE
}

APPLY=0
case "${1:-}" in
  "") ;;
  --apply) APPLY=1 ;;
  -h|--help) usage; exit 0 ;;
  *) echo "ERROR: unknown option: $1" >&2; usage >&2; exit 2 ;;
esac

AFS_ROOT=${AFS_ROOT:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
EOS_ROOT=${EOS_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
STAMP=${STAMP:-$(date +%Y%m%d_%H%M%S)}
OUTPUT_DIRS=(runs lhe logs metadata validation)

if [[ ! -d "$AFS_ROOT" ]]; then
  echo "ERROR: AFS repository does not exist: $AFS_ROOT" >&2
  exit 3
fi

case "$EOS_ROOT" in
  /eos/*) ;;
  *) echo "ERROR: EOS_ROOT must be below /eos: $EOS_ROOT" >&2; exit 4 ;;
esac

cat <<PLAN
AFS repository:  $AFS_ROOT
EOS output root: $EOS_ROOT
Timestamp:       $STAMP
Output trees:    ${OUTPUT_DIRS[*]}
Apply changes:   $APPLY
PLAN

RUNNING_PROCESSES=""
if pgrep -x -u "$USER" whizard >/dev/null 2>&1; then
  RUNNING_PROCESSES+="$(pgrep -a -x -u "$USER" whizard || true)"$'\n'
fi
ANALYSIS_PROCESSES=$(pgrep -afu "$USER" 'python(3)? .*scripts/analysis/(parse_lhe_ttbar|make_spin_observables|compare_spin_samples|validate_spin_shapes)\.py' || true)
if [[ -n "$ANALYSIS_PROCESSES" ]]; then
  RUNNING_PROCESSES+="$ANALYSIS_PROCESSES"$'\n'
fi
if [[ -n "${RUNNING_PROCESSES//$'\n'/}" ]]; then
  echo
  echo "WARNING: potentially relevant processes are running:" >&2
  printf '%s' "$RUNNING_PROCESSES" >&2
  echo "Stop them before using --apply." >&2
  if [[ $APPLY -eq 1 ]]; then
    exit 5
  fi
fi

if [[ $APPLY -eq 0 ]]; then
  echo
  echo "Dry plan only. Re-run with --apply after stopping all project jobs."
  exit 0
fi

mkdir -p "$EOS_ROOT"

for name in "${OUTPUT_DIRS[@]}"; do
  src="$AFS_ROOT/$name"
  dst="$EOS_ROOT/$name"

  if [[ -L "$src" ]]; then
    resolved=$(readlink -f "$src")
    if [[ "$resolved" == "$dst" ]]; then
      echo "Already migrated: $src -> $dst"
      continue
    fi
    echo "ERROR: $src is already a symlink to an unexpected target: $resolved" >&2
    exit 6
  fi

  if [[ ! -d "$src" ]]; then
    echo "ERROR: expected source directory is missing: $src" >&2
    exit 7
  fi

  echo
  echo "=== Copying $name ==="
  mkdir -p "$dst"
  rsync -rlt --safe-links --omit-dir-times --info=progress2 "$src/" "$dst/"

  echo "=== Verifying $name with checksums ==="
  verify_output=$(mktemp)
  rsync -rltcn --delete --safe-links --omit-dir-times --itemize-changes \
    "$src/" "$dst/" > "$verify_output"
  if [[ -s "$verify_output" ]]; then
    echo "ERROR: verification differences remain for $name:" >&2
    cat "$verify_output" >&2
    rm -f "$verify_output"
    exit 8
  fi
  rm -f "$verify_output"
  echo "Verified: $name"
done

for name in "${OUTPUT_DIRS[@]}"; do
  src="$AFS_ROOT/$name"
  dst="$EOS_ROOT/$name"

  if [[ -L "$src" ]]; then
    continue
  fi

  backup="$AFS_ROOT/${name}.afs_backup_${STAMP}"
  if [[ -e "$backup" ]]; then
    echo "ERROR: backup path already exists: $backup" >&2
    exit 9
  fi

  mv "$src" "$backup"
  ln -s "$dst" "$src"
  echo "Linked: $src -> $dst"
done

record="$EOS_ROOT/MIGRATION_FROM_AFS_${STAMP}.txt"
{
  echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "afs_root=$AFS_ROOT"
  echo "eos_root=$EOS_ROOT"
  echo "output_dirs=${OUTPUT_DIRS[*]}"
  echo "afs_backups_suffix=.afs_backup_${STAMP}"
} > "$record"

cat <<DONE

Migration and checksum verification completed.

AFS backups remain in place with suffix:
  .afs_backup_${STAMP}

Test the project before deleting them. After successful tests, reclaim AFS space with:
  rm -rf \\
    "$AFS_ROOT/runs.afs_backup_${STAMP}" \\
    "$AFS_ROOT/lhe.afs_backup_${STAMP}" \\
    "$AFS_ROOT/logs.afs_backup_${STAMP}" \\
    "$AFS_ROOT/metadata.afs_backup_${STAMP}" \\
    "$AFS_ROOT/validation.afs_backup_${STAMP}"

Migration record:
  $record
DONE
