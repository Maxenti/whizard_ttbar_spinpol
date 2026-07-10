#!/usr/bin/env bash

# This file must be sourced:
#
#   source setup_lxplus.sh
#
# It configures the stable Key4HEP environment and applies conservative
# thread limits for WHIZARD validation and production jobs.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "ERROR: this script must be sourced, not executed." >&2
  echo "Use:" >&2
  echo "  source setup_lxplus.sh" >&2
  exit 2
fi

_SETUP_DIR=$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &&
  pwd
)

export WHIZARD_TTBAR_ROOT="$_SETUP_DIR"

KEY4HEP_SETUP=${KEY4HEP_SETUP:-/cvmfs/sw.hsf.org/key4hep/setup.sh}

if [[ ! -r "$KEY4HEP_SETUP" ]]; then
  echo "ERROR: Key4HEP setup script is not readable:" >&2
  echo "  $KEY4HEP_SETUP" >&2
  return 3
fi

# Warn about an already-loaded WHIZARD environment. Sourcing several
# independent CVMFS stacks into one shell is not supported.
if command -v whizard >/dev/null 2>&1; then
  echo "WARNING: whizard was already present before Key4HEP setup:"
  command -v whizard
  echo
  echo "For the cleanest environment, start a fresh lxplus shell and source"
  echo "only this setup script."
  echo
fi

source "$KEY4HEP_SETUP" || {
  echo "ERROR: Key4HEP setup failed." >&2
  return 4
}

export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-1}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-1}
export NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS:-1}
export MALLOC_ARENA_MAX=${MALLOC_ARENA_MAX:-2}

_required_commands=(
  whizard
  gcc
  gfortran
  python3
)

_missing=0
for _cmd in "${_required_commands[@]}"; do
  if ! command -v "$_cmd" >/dev/null 2>&1; then
    echo "ERROR: required command is missing: $_cmd" >&2
    _missing=1
  fi
done

if [[ "$_missing" -ne 0 ]]; then
  return 5
fi

export WHIZARD_EXE
WHIZARD_EXE=$(readlink -f "$(command -v whizard)")

echo "============================================================"
echo "WHIZARD ttbar spin/polarization environment"
echo "============================================================"
echo "Project:          $WHIZARD_TTBAR_ROOT"
echo "Key4HEP setup:    $KEY4HEP_SETUP"
echo "WHIZARD command:  $(command -v whizard)"
echo "WHIZARD realpath: $WHIZARD_EXE"
echo "Python:           $(command -v python3)"
echo "GCC:              $(command -v gcc)"
echo "GFortran:         $(command -v gfortran)"
echo
whizard --version
echo
echo "Thread limits:"
echo "  OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "  OPENBLAS_NUM_THREADS=$OPENBLAS_NUM_THREADS"
echo "  MKL_NUM_THREADS=$MKL_NUM_THREADS"
echo "  NUMEXPR_NUM_THREADS=$NUMEXPR_NUM_THREADS"
echo "  MALLOC_ARENA_MAX=$MALLOC_ARENA_MAX"
echo "============================================================"

unset _SETUP_DIR
unset _required_commands
unset _missing
unset _cmd
