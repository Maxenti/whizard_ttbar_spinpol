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

# Make project setup idempotent.  The raw Key4HEP setup script deliberately
# rejects repeated setup in one shell, while project wrappers may be nested
# (validation -> build, interactive shell -> validation, etc.).
_key4hep_active=0
_whizard_before_setup=""

if [[ ${WHIZARD_TTBAR_ENV_READY:-0} == 1 ]]; then
  _key4hep_active=1
elif command -v whizard >/dev/null 2>&1; then
  _whizard_before_setup=$(readlink -f "$(command -v whizard)")
  if [[ $_whizard_before_setup == /cvmfs/sw.hsf.org/key4hep/releases/* ]]; then
    _key4hep_active=1
  fi
fi

if (( _key4hep_active == 0 )); then
  if [[ -n $_whizard_before_setup ]]; then
    echo "WARNING: a non-Key4HEP WHIZARD environment is already active:"
    echo "  $_whizard_before_setup"
    echo
    echo "For the cleanest environment, start a fresh lxplus shell and source"
    echo "only this setup script."
    echo
  fi

  nounset_was_on=0
  errexit_was_on=0
  case $- in *u*) nounset_was_on=1; set +u;; esac
  case $- in *e*) errexit_was_on=1; set +e;; esac

  # shellcheck disable=SC1090
  source "$KEY4HEP_SETUP"
  _setup_rc=$?

  (( errexit_was_on == 0 )) || set -e
  (( nounset_was_on == 0 )) || set -u

  if (( _setup_rc != 0 )); then
    echo "ERROR: Key4HEP setup failed with return code $_setup_rc." >&2
    return 4
  fi
else
  echo "Key4HEP environment already active; reusing current environment."
fi

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
unset _key4hep_active
unset _whizard_before_setup
unset _setup_rc
unset nounset_was_on
unset errexit_was_on

# Mark the project environment as initialized so nested wrappers do not source
# the raw Key4HEP setup script again.
export WHIZARD_TTBAR_ENV_READY=1

# Canonical persistent output location.
export WHIZARD_TTBAR_OUTPUT_ROOT=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

# Do not create Python bytecode caches inside the AFS source tree.
export PYTHONDONTWRITEBYTECODE=1
