#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
BUILD=${1:-$ROOT/build}
PROJECT_SETUP=${QIS_PROJECT_SETUP:-$ROOT/setup_lxplus.sh}

if [[ ${QIS_SKIP_ENV_SETUP:-0} != 1 && ${WHIZARD_TTBAR_ENV_READY:-0} != 1 ]]; then
  [[ -r $PROJECT_SETUP ]] || { echo "ERROR: setup script not readable: $PROJECT_SETUP" >&2; exit 2; }
  nounset_was_on=0
  errexit_was_on=0
  case $- in *u*) nounset_was_on=1; set +u;; esac
  case $- in *e*) errexit_was_on=1; set +e;; esac
  # shellcheck disable=SC1090
  source "$PROJECT_SETUP"
  setup_rc=$?
  (( errexit_was_on == 0 )) || set -e
  (( nounset_was_on == 0 )) || set -u
  (( setup_rc == 0 )) || { echo "ERROR: environment setup failed rc=$setup_rc" >&2; exit 3; }
fi

command -v cmake >/dev/null || { echo "ERROR: cmake unavailable" >&2; exit 4; }
command -v python3 >/dev/null || { echo "ERROR: python3 unavailable" >&2; exit 5; }

cmake -S "$ROOT" -B "$BUILD" \
  -DCMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE:-RelWithDebInfo}" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build "$BUILD" --parallel "${QIS_BUILD_JOBS:-2}"

pip_args=(--no-deps -e "$ROOT")
if [[ -z ${VIRTUAL_ENV:-} && ${QIS_PIP_USER:-1} == 1 ]]; then
  pip_args=(--user "${pip_args[@]}")
fi
python3 -m pip install "${pip_args[@]}"

echo "Built: $BUILD/qis_lhe_to_hepmc3"
echo "Python package: whizard-ttbar-qis"
