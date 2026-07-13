#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=${REPO_ROOT:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
EOS_ROOT=${EOS_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
OUTPUT_DIRS=(runs lhe logs metadata validation)

fail=0
for name in "${OUTPUT_DIRS[@]}"; do
  path="$REPO_ROOT/$name"
  expected="$EOS_ROOT/$name"
  if [[ ! -L "$path" ]]; then
    echo "FAIL: $path is not a symlink"
    fail=1
    continue
  fi
  resolved=$(readlink -f "$path")
  if [[ "$resolved" != "$expected" ]]; then
    echo "FAIL: $path -> $resolved; expected $expected"
    fail=1
  else
    echo "PASS: $path -> $resolved"
  fi
done

if [[ $fail -ne 0 ]]; then
  exit 1
fi

echo "All persistent output trees resolve to EOS."
