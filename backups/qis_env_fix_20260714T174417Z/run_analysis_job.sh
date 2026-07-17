#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
KEY4HEP_SETUP=${KEY4HEP_SETUP:-$ROOT/setup_lxplus.sh}
nounset=0; case $- in *u*) nounset=1; set +u;; esac
# shellcheck disable=SC1090
source "$KEY4HEP_SETUP"
(( nounset == 0 )) || set -u
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
exec "$@"
