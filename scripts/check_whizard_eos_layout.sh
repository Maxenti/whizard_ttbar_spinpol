#!/usr/bin/env bash
#
# Validate that all persistent WHIZARD output trees resolve to the intended
# EOS project area.
#
# CERN EOS home directories can appear through equivalent mount aliases:
#
#   /eos/user/c/<user>/...
#   /eos/home-c/<user>/...
#
# Therefore this checker compares canonical filesystem destinations rather
# than literal path strings.

set -euo pipefail

SCRIPT_DIR="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1
  pwd -P
)"

PROJECT_ROOT="$(
  cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1
  pwd -P
)"

EXPECTED_OUTPUT_ROOT="${WHIZARD_TTBAR_OUTPUT_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"

OUTPUT_DIRS=(
  runs
  lhe
  logs
  metadata
  validation
)

canonical_path() {
  local path="$1"

  if [[ -e "$path" || -L "$path" ]]; then
    readlink -f -- "$path"
  else
    realpath -m -- "$path"
  fi
}

EXPECTED_CANONICAL="$(canonical_path "$EXPECTED_OUTPUT_ROOT")"

echo "Project root:"
echo "  $PROJECT_ROOT"
echo
echo "Configured EOS output root:"
echo "  $EXPECTED_OUTPUT_ROOT"
echo
echo "Canonical EOS output root:"
echo "  $EXPECTED_CANONICAL"
echo

failures=0

for directory in "${OUTPUT_DIRS[@]}"; do
  logical_path="${PROJECT_ROOT}/${directory}"
  expected_path="${EXPECTED_OUTPUT_ROOT}/${directory}"
  expected_canonical="$(canonical_path "$expected_path")"

  if [[ ! -L "$logical_path" ]]; then
    echo "FAIL: $logical_path is not a symbolic link"
    failures=$((failures + 1))
    continue
  fi

  if [[ ! -e "$logical_path" ]]; then
    echo "FAIL: $logical_path is a broken symbolic link"
    failures=$((failures + 1))
    continue
  fi

  actual_canonical="$(canonical_path "$logical_path")"

  if [[ "$actual_canonical" != "$expected_canonical" ]]; then
    echo "FAIL: $logical_path"
    echo "      actual:   $actual_canonical"
    echo "      expected: $expected_canonical"
    failures=$((failures + 1))
    continue
  fi

  if [[ ! -d "$actual_canonical" ]]; then
    echo "FAIL: resolved path is not a directory: $actual_canonical"
    failures=$((failures + 1))
    continue
  fi

  if [[ ! -w "$actual_canonical" ]]; then
    echo "FAIL: resolved directory is not writable: $actual_canonical"
    failures=$((failures + 1))
    continue
  fi

  echo "PASS: $logical_path"
  echo "      -> $actual_canonical"
done

echo

if (( failures > 0 )); then
  echo "EOS layout validation failed: ${failures} problem(s)"
  exit 1
fi

echo "All persistent output trees resolve to the configured EOS project."
echo "Literal /eos/user/... and /eos/home-c/... aliases are treated equivalently."
