#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
SAMPLE=${SAMPLE:-ee_ttbar_epmum_LR100_sc_ISR_500GeV}
EVENTS=${EVENTS:-200}
SEED=${SEED:-881001}
OUT=${OUT:-/tmp/$USER/qis_explicit_w_ab_test}

INPUT="$REPO/tests/qis/data/smoke_lhe/${SAMPLE}.lhe"
CANONICALIZER="$REPO/scripts/showering/canonicalize_whizard_lhe_for_pythia.py"
W_ADAPTER="$REPO/scripts/showering/insert_explicit_w_resonances.py"
EXE="$REPO/build/qis_lhe_to_hepmc3"
SETTINGS="$REPO/configs/pythia/level_a.cmnd"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -f "$INPUT" ]] || die "missing input: $INPUT"
[[ -x "$CANONICALIZER" ]] || die "missing canonicalizer: $CANONICALIZER"
[[ -x "$W_ADAPTER" ]] || die "missing explicit-W adapter: $W_ADAPTER"
[[ -x "$EXE" ]] || die "missing shower executable: $EXE"
[[ -f "$SETTINGS" ]] || die "missing settings: $SETTINGS"

export PYTHONDONTWRITEBYTECODE=1

rm -rf "$OUT"
mkdir -p "$OUT"/{lhe,summaries,hepmc3,metadata,logs}

DIRECT="$OUT/lhe/${SAMPLE}.canonical_v2.lhe"
EXPLICIT_W="$OUT/lhe/${SAMPLE}.canonical_v3_explicit_w.lhe"

python3 "$CANONICALIZER" \
  --input "$INPUT" \
  --output "$DIRECT" \
  --summary "$OUT/summaries/canonical_v2.json"

python3 "$W_ADAPTER" \
  --input "$DIRECT" \
  --output "$EXPLICIT_W" \
  --summary "$OUT/summaries/explicit_w_v3.json"

python3 - "$OUT/summaries/canonical_v2.json" \
  "$OUT/summaries/explicit_w_v3.json" "$EVENTS" <<'PY'
import json
import sys
from pathlib import Path

v2 = json.loads(Path(sys.argv[1]).read_text())
v3 = json.loads(Path(sys.argv[2]).read_text())
events = int(sys.argv[3])

assert v2["total_events"] == events, v2
assert v2["canonicalized_events"] == events, v2
assert v2["rewired_isr_photons"] == 2 * events, v2

assert v3["total_events"] == events, v3
assert v3["explicit_w_events"] == events, v3
assert v3["inserted_w_resonances"] == 2 * events, v3
assert v3["max_vertex_rel_closure"] <= 1.0e-7, v3

print("V2 and explicit-W v3 contracts: PASS")
PY

run_case() {
  local case_name=$1
  local input=$2
  shift 2

  local output="$OUT/hepmc3/${case_name}.hepmc3"
  local metadata="$OUT/metadata/${case_name}.json"
  local log="$OUT/logs/${case_name}.log"

  echo
  echo "======================================================================"
  echo "CASE: $case_name"
  echo "INPUT: $input"
  echo "OVERRIDES: $*"
  echo "======================================================================"

  set +e
  "$EXE" \
    --input "$input" \
    --output "$output" \
    --metadata "$metadata" \
    --settings "$SETTINGS" \
    --campaign-id explicit_w_ab_test \
    --sample-id "$SAMPLE" \
    --shard-id "$case_name" \
    --seed "$SEED" \
    --max-events "$EVENTS" \
    "$@" \
    >"$log" 2>&1
  rc=$?
  set -e

  printf '%s\n' "$rc" > "$OUT/metadata/${case_name}.rc"

  if (( rc != 0 )); then
    tail -100 "$log" || true
  fi
}

run_case direct_default "$DIRECT"
run_case direct_mecorrections_off "$DIRECT" \
  --set "TimeShower:MEcorrections = off"
run_case explicit_w_default "$EXPLICIT_W"
run_case explicit_w_mecorrections_off "$EXPLICIT_W" \
  --set "TimeShower:MEcorrections = off"

export QIS_EXPLICIT_W_AB_OUT="$OUT"
export QIS_EXPLICIT_W_AB_EVENTS="$EVENTS"

python3 - <<'PY'
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

import pyhepmc

root = Path(os.environ["QIS_EXPLICIT_W_AB_OUT"])
expected = int(os.environ["QIS_EXPLICIT_W_AB_EVENTS"])

cases = (
    "direct_default",
    "direct_mecorrections_off",
    "explicit_w_default",
    "explicit_w_mecorrections_off",
)


def warnings(text: str, message: str) -> int:
    pattern = re.compile(
        rf"^\s*\|\s*(\d+)\s+Warning in {re.escape(message)}",
        re.MULTILINE,
    )
    found = pattern.findall(text)
    return int(found[-1]) if found else text.count(f"Warning in {message}")


def count_events(path: Path) -> int:
    count = 0
    with pyhepmc.open(path) as stream:
        for _ in stream:
            count += 1
    return count


rows = []
problems = []

for case in cases:
    metadata = json.loads((root / "metadata" / f"{case}.json").read_text())
    rc = int((root / "metadata" / f"{case}.rc").read_text())
    log = (root / "logs" / f"{case}.log").read_text(errors="replace")
    hepmc_path = root / "hepmc3" / f"{case}.hepmc3"
    hepmc_events = count_events(hepmc_path) if hepmc_path.exists() else -1

    row = {
        "case": case,
        "return_code": rc,
        "status": metadata.get("status"),
        "accepted_events": metadata.get("accepted_events"),
        "hepmc_events": hepmc_events,
        "last_pythia_event_size": metadata.get("last_pythia_event_size"),
        "me_weight_warning_count": warnings(
            log,
            "SimpleTimeShower::findMEcorr: ME weight above PS one",
        ),
        "negative_dipole_warning_count": warnings(
            log,
            "SimpleTimeShower::pTnext: negative dipole mass",
        ),
        "output_size_bytes": hepmc_path.stat().st_size if hepmc_path.exists() else -1,
    }
    rows.append(row)

    if rc != 0:
        problems.append(f"{case}: return code {rc}")
    if metadata.get("status") != "success":
        problems.append(f"{case}: status={metadata.get('status')!r}")
    if metadata.get("accepted_events") != expected:
        problems.append(
            f"{case}: accepted={metadata.get('accepted_events')}"
        )
    if hepmc_events != expected:
        problems.append(f"{case}: HepMC={hepmc_events}")

csv_path = root / "explicit_w_ab_summary.csv"
with csv_path.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print()
print(
    f"{'case':32s} {'acc':>5s} {'HepMC':>5s} "
    f"{'MEwarn':>7s} {'negDip':>7s} {'status':>9s}"
)
print("-" * 78)
for row in rows:
    print(
        f"{row['case']:32s} "
        f"{int(row['accepted_events']):5d} "
        f"{int(row['hepmc_events']):5d} "
        f"{int(row['me_weight_warning_count']):7d} "
        f"{int(row['negative_dipole_warning_count']):7d} "
        f"{str(row['status']):>9s}"
    )

print()
print(f"Wrote {csv_path}")

if problems:
    print("FAILURES:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print("EXPLICIT-W A/B STRUCTURAL PASS")
PY
