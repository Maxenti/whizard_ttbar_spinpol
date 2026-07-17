#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
PROJECT_SETUP=${QIS_PROJECT_SETUP:-$ROOT/setup_lxplus.sh}
if [[ ${WHIZARD_TTBAR_ENV_READY:-0} != 1 ]]; then
  [[ -r $PROJECT_SETUP ]] || {
    echo "ERROR: setup script not readable: $PROJECT_SETUP" >&2
    exit 2
  }
  nounset=0
  errexit=0
  case $- in *u*) nounset=1; set +u;; esac
  case $- in *e*) errexit=1; set +e;; esac
  # shellcheck disable=SC1090
  source "$PROJECT_SETUP"
  setup_rc=$?
  (( errexit == 0 )) || set -e
  (( nounset == 0 )) || set -u
  (( setup_rc == 0 )) || {
    echo "ERROR: environment setup failed rc=$setup_rc" >&2
    exit 3
  }
fi
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
exec "$@"
