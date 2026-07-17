#!/usr/bin/env bash
# Build the C++ shower executable in the active Key4HEP environment and run a
# compact PYTHIA8 -> HepMC3 -> Python-analysis acceptance test.
set -euo pipefail

REPO=$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." >/dev/null 2>&1
  pwd -P
)
SETUP=${QIS_PROJECT_SETUP:-$REPO/setup_lxplus.sh}
EVENTS=${QIS_LXPLUS_SMOKE_EVENTS:-10}
WORK=${QIS_LXPLUS_SMOKE_DIR:-/tmp/${USER:-unknown}/whizard_qis_lxplus_smoke}
INPUT=${QIS_LXPLUS_SMOKE_LHE:-$REPO/tests/qis/data/smoke_lhe/ee_ttbar_epmum_LR100_sc_ISR_500GeV.lhe}

[[ -r $SETUP ]] || { echo "ERROR: setup script not readable: $SETUP" >&2; exit 2; }
[[ -r $INPUT ]] || { echo "ERROR: smoke LHE not readable: $INPUT" >&2; exit 3; }

nounset_was_on=0
errexit_was_on=0
case $- in *u*) nounset_was_on=1; set +u;; esac
case $- in *e*) errexit_was_on=1; set +e;; esac
# shellcheck disable=SC1090
source "$SETUP"
setup_rc=$?
(( errexit_was_on == 0 )) || set -e
(( nounset_was_on == 0 )) || set -u
(( setup_rc == 0 )) || { echo "ERROR: environment setup failed rc=$setup_rc" >&2; exit 4; }

rm -rf "$WORK"
mkdir -p "$WORK"

QIS_SKIP_ENV_SETUP=1 "$REPO/scripts/qis/build_qis.sh"

"$REPO/build/qis_lhe_to_hepmc3" \
  --input "$INPUT" \
  --output "$WORK/smoke.hepmc3" \
  --metadata "$WORK/smoke.metadata.json" \
  --settings "$REPO/configs/pythia/level_a.cmnd" \
  --campaign-id lxplus_acceptance \
  --sample-id ee_ttbar_epmum_LR100_sc_ISR_500GeV \
  --shard-id smoke \
  --seed 880001 \
  --max-events "$EVENTS"

PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}" python3 - "$WORK" "$EVENTS" <<'PY'
import json
import sys
from pathlib import Path

import pyhepmc

work = Path(sys.argv[1])
expected = int(sys.argv[2])
metadata = json.loads((work / "smoke.metadata.json").read_text())
if metadata.get("status") != "success":
    raise SystemExit(f"metadata status is not success: {metadata}")
if int(metadata.get("accepted_events", -1)) != expected:
    raise SystemExit(f"accepted_events mismatch: {metadata.get('accepted_events')} != {expected}")
count = 0
with pyhepmc.open(work / "smoke.hepmc3") as stream:
    for _ in stream:
        count += 1
if count != expected:
    raise SystemExit(f"HepMC3 event count mismatch: {count} != {expected}")
print(f"LXPLUS C++ ACCEPTANCE PASS events={count}")
PY

PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}" python3 "$REPO/scripts/qis/validate_qis_framework.py" \
  --output "$WORK/qis_framework_validation"

echo "Acceptance products: $WORK"
