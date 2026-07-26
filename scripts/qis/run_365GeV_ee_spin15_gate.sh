#!/usr/bin/env bash
#
# Run the complete truth-level Spin-15 qualification gate for the validated
# 365 GeV e+e- -> ttbar SC and isotropic-control sample matrix.
#
# Execute this script. Do not source it.
#
# Optional overrides:
#
#   MAX_EVENTS=100
#   STRICT_PHYSICS=0
#   PLOT_FORMATS="png"
#   OUT=/tmp/<user>/spin15_smoke
#   FORCE=1
#
# The underlying generic gate remains:
#
#   scripts/qis/run_spin15_qualification_gate.sh
#

if [[ ${BASH_SOURCE[0]} != "$0" ]]; then
  echo "ERROR: execute this script; do not source it." >&2
  echo "Use:" >&2
  echo "  ./scripts/qis/run_365GeV_ee_spin15_gate.sh" >&2
  return 2
fi

set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}

SC_CONFIG=${SC_CONFIG:-$REPO/configs/qis/qualification_365GeV_ee_sc_v1.yaml}
ISO_CONFIG=${ISO_CONFIG:-$REPO/configs/qis/qualification_365GeV_ee_iso_v1.yaml}

SC_PRODUCTION_CONFIG=${SC_PRODUCTION_CONFIG:-$REPO/configs/production/production_365GeV_ee_sc_v1.csv}
ISO_PRODUCTION_CONFIG=${ISO_PRODUCTION_CONFIG:-$REPO/configs/production/production_365GeV_ee_iso_v1.csv}

MAX_EVENTS=${MAX_EVENTS:-10000}
STRICT_PHYSICS=${STRICT_PHYSICS:-1}
FORCE=${FORCE:-0}
PLOT_FORMATS=${PLOT_FORMATS:-"png pdf"}

OUT=${OUT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/paper_spin_365GeV_ee_spin15_10k_v1}

GENERIC_GATE=$REPO/scripts/qis/run_spin15_qualification_gate.sh
SETUP=$REPO/setup_lxplus.sh

die() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -d $REPO ]] || die "missing repository: $REPO"
[[ -r $SETUP ]] || die "missing setup script: $SETUP"
[[ -x $GENERIC_GATE ]] || die "missing executable generic gate: $GENERIC_GATE"

[[ -f $SC_CONFIG ]] || die "missing SC qualification config: $SC_CONFIG"
[[ -f $ISO_CONFIG ]] || die "missing ISO qualification config: $ISO_CONFIG"

[[ -f $SC_PRODUCTION_CONFIG ]] \
  || die "missing SC production config: $SC_PRODUCTION_CONFIG"

[[ -f $ISO_PRODUCTION_CONFIG ]] \
  || die "missing ISO production config: $ISO_PRODUCTION_CONFIG"

[[ $MAX_EVENTS =~ ^[0-9]+$ ]] \
  || die "MAX_EVENTS must be a positive integer"

(( MAX_EVENTS > 0 )) \
  || die "MAX_EVENTS must be positive"

[[ $STRICT_PHYSICS == 0 || $STRICT_PHYSICS == 1 ]] \
  || die "STRICT_PHYSICS must be 0 or 1"

[[ $FORCE == 0 || $FORCE == 1 ]] \
  || die "FORCE must be 0 or 1"

[[ $OUT == /eos/* || $OUT == /tmp/* ]] \
  || die "OUT must be on EOS or under /tmp"

cd "$REPO"

# External Key4HEP/Spack setup code is not guaranteed to be compatible with
# nounset or errexit. Temporarily suspend both options while sourcing it.
set +e
set +u

# shellcheck disable=SC1090
source "$SETUP"
setup_rc=$?

set -u
set -e

(( setup_rc == 0 )) \
  || die "setup_lxplus.sh failed with rc=$setup_rc"

[[ ${WHIZARD_TTBAR_ENV_READY:-0} == 1 ]] \
  || die "project runtime environment was not established"

command -v python3 >/dev/null 2>&1 \
  || die "python3 is unavailable after environment setup"

python3 - <<'PY'
import pyhepmc
import yaml

print(f"Python YAML: available")
print(f"pyhepmc:    {getattr(pyhepmc, '__version__', 'available')}")
PY

export REPO
export SC_CONFIG
export ISO_CONFIG
export SC_PRODUCTION_CONFIG
export ISO_PRODUCTION_CONFIG
export MAX_EVENTS
export STRICT_PHYSICS
export FORCE
export PLOT_FORMATS
export OUT

cat <<EOF

======================================================================
365 GEV EE SPIN-15 GATE
======================================================================
Repository:
  $REPO

SC qualification:
  $SC_CONFIG

ISO qualification:
  $ISO_CONFIG

SC beam-production audit:
  $SC_PRODUCTION_CONFIG

ISO beam-production audit:
  $ISO_PRODUCTION_CONFIG

Events per sample:
  $MAX_EVENTS

Strict physics:
  $STRICT_PHYSICS

Plot formats:
  $PLOT_FORMATS

Output:
  $OUT
======================================================================

EOF

"$GENERIC_GATE"
