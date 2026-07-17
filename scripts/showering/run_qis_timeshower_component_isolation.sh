#!/usr/bin/env bash
#
# Isolate which PYTHIA timelike-shower component produces
# "SimpleTimeShower::pTnext: negative dipole mass".
#
# This is a diagnostic matrix, not a production configuration.
#
# Usage:
#   source setup_lxplus.sh
#   ./scripts/showering/run_qis_timeshower_component_isolation.sh
#
# Optional:
#   REPO=/path/to/repo
#   SAMPLE=ee_ttbar_epmum_LR100_sc_ISR_500GeV
#   EVENTS=200
#   SEED=882001
#   OUT=/tmp/$USER/qis_timeshower_component_isolation
#

set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
SAMPLE=${SAMPLE:-ee_ttbar_epmum_LR100_sc_ISR_500GeV}
EVENTS=${EVENTS:-200}
SEED=${SEED:-882001}
OUT=${OUT:-/tmp/$USER/qis_timeshower_component_isolation}

INPUT="$REPO/tests/qis/data/smoke_lhe/${SAMPLE}.lhe"
CANONICALIZER="$REPO/scripts/showering/canonicalize_whizard_lhe_for_pythia.py"
EXE="$REPO/build/qis_lhe_to_hepmc3"
SETTINGS="$REPO/configs/pythia/level_a.cmnd"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -f "$INPUT" ]] || die "missing input: $INPUT"
[[ -x "$CANONICALIZER" ]] || die "missing canonicalizer: $CANONICALIZER"
[[ -x "$EXE" ]] || die "missing shower executable: $EXE"
[[ -f "$SETTINGS" ]] || die "missing settings file: $SETTINGS"
grep -q 'rewired_isr_photons' "$CANONICALIZER" \
  || die "installed canonicalizer is not canonical-v2"

python3 - <<'PY'
import importlib
importlib.import_module("pyhepmc")
print("Python dependency check: PASS")
PY

rm -rf "$OUT"
mkdir -p "$OUT"/{lhe,summaries,hepmc3,metadata,logs,return_codes}

CANONICAL="$OUT/lhe/${SAMPLE}.canonical_v2.lhe"

python3 "$CANONICALIZER" \
  --input "$INPUT" \
  --output "$CANONICAL" \
  --summary "$OUT/summaries/canonical_v2.json"

python3 - "$OUT/summaries/canonical_v2.json" "$EVENTS" <<'PY'
import json
import sys
from pathlib import Path

summary = json.loads(Path(sys.argv[1]).read_text())
events = int(sys.argv[2])

assert summary["total_events"] == events, summary
assert summary["canonicalized_events"] == events, summary
assert summary["removed_bridge_particles"] == 2 * events, summary
assert summary["promoted_beam_particles"] == 2 * events, summary
assert summary["rewired_isr_photons"] == 2 * events, summary
assert summary["removed_sqme_prc_tags"] == events, summary
assert summary["max_rel_closure"] <= 1.0e-7, summary

print("Canonical-v2 contract: PASS")
PY

run_case() {
  local case_name=$1
  shift

  local output="$OUT/hepmc3/${case_name}.hepmc3"
  local metadata="$OUT/metadata/${case_name}.json"
  local log="$OUT/logs/${case_name}.log"
  local rc_file="$OUT/return_codes/${case_name}.rc"

  echo
  echo "======================================================================"
  echo "CASE: $case_name"
  printf 'OVERRIDES:'
  if (( $# == 0 )); then
    printf ' (none)'
  else
    printf ' %q' "$@"
  fi
  echo
  echo "======================================================================"

  set +e
  "$EXE" \
    --input "$CANONICAL" \
    --output "$output" \
    --metadata "$metadata" \
    --settings "$SETTINGS" \
    --campaign-id qis_timeshower_component_isolation \
    --sample-id "$SAMPLE" \
    --shard-id "$case_name" \
    --seed "$SEED" \
    --max-events "$EVENTS" \
    "$@" \
    >"$log" 2>&1
  rc=$?
  set -e

  printf '%s\n' "$rc" > "$rc_file"
  echo "return code: $rc"

  if (( rc != 0 )); then
    echo "--- final 100 log lines ---"
    tail -100 "$log" || true
    echo "---------------------------"
  fi
}

# Controls.
run_case default
run_case mecorrections_off \
  --set "TimeShower:MEcorrections = off"
run_case fsr_off \
  --set "PartonLevel:FSR = off"
run_case resonance_fsr_off \
  --set "PartonLevel:FSRinResonances = off"

# QCD versus all timelike QED.
run_case qcd_off \
  --set "TimeShower:QCDshower = off"

run_case all_qed_off \
  --set "TimeShower:QEDshowerByQ = off" \
  --set "TimeShower:QEDshowerByL = off" \
  --set "TimeShower:QEDshowerByOther = off" \
  --set "TimeShower:QEDshowerByGamma = off"

# Individual QED sources.
run_case qed_by_quark_off \
  --set "TimeShower:QEDshowerByQ = off"

run_case qed_by_lepton_off \
  --set "TimeShower:QEDshowerByL = off"

run_case qed_by_resonance_off \
  --set "TimeShower:QEDshowerByOther = off"

run_case qed_by_gamma_off \
  --set "TimeShower:QEDshowerByGamma = off"

# No standard QCD or QED timelike branching.
run_case qcd_and_qed_off \
  --set "TimeShower:QCDshower = off" \
  --set "TimeShower:QEDshowerByQ = off" \
  --set "TimeShower:QEDshowerByL = off" \
  --set "TimeShower:QEDshowerByOther = off" \
  --set "TimeShower:QEDshowerByGamma = off"

export QIS_COMPONENT_OUT="$OUT"
export QIS_COMPONENT_EVENTS="$EVENTS"

python3 - <<'PY'
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

import pyhepmc

root = Path(os.environ["QIS_COMPONENT_OUT"])
expected_events = int(os.environ["QIS_COMPONENT_EVENTS"])

cases = (
    "default",
    "mecorrections_off",
    "fsr_off",
    "resonance_fsr_off",
    "qcd_off",
    "all_qed_off",
    "qed_by_quark_off",
    "qed_by_lepton_off",
    "qed_by_resonance_off",
    "qed_by_gamma_off",
    "qcd_and_qed_off",
)


def warning_count(text: str, message: str) -> int:
    pattern = re.compile(
        rf"^\s*\|\s*(\d+)\s+Warning in {re.escape(message)}",
        re.MULTILINE,
    )
    matches = pattern.findall(text)
    if matches:
        return int(matches[-1])
    return text.count(f"Warning in {message}")


def count_hepmc_events(path: Path) -> int:
    if not path.exists():
        return -1
    count = 0
    with pyhepmc.open(path) as stream:
        for _ in stream:
            count += 1
    return count


rows = []
problems = []

for case in cases:
    metadata_path = root / "metadata" / f"{case}.json"
    output_path = root / "hepmc3" / f"{case}.hepmc3"
    log_path = root / "logs" / f"{case}.log"
    rc_path = root / "return_codes" / f"{case}.rc"

    rc = int(rc_path.read_text().strip())
    metadata = (
        json.loads(metadata_path.read_text())
        if metadata_path.exists()
        else {}
    )
    log_text = (
        log_path.read_text(errors="replace")
        if log_path.exists()
        else ""
    )
    hepmc_events = count_hepmc_events(output_path)

    me_warnings = warning_count(
        log_text,
        "SimpleTimeShower::findMEcorr: ME weight above PS one",
    )
    negative_dipole_warnings = warning_count(
        log_text,
        "SimpleTimeShower::pTnext: negative dipole mass",
    )

    row = {
        "case": case,
        "return_code": rc,
        "status": metadata.get("status", "missing"),
        "accepted_events": metadata.get("accepted_events", -1),
        "hepmc_events": hepmc_events,
        "me_weight_warning_count": me_warnings,
        "negative_dipole_warning_count": negative_dipole_warnings,
        "me_weight_warnings_per_event": me_warnings / expected_events,
        "negative_dipole_warnings_per_event": (
            negative_dipole_warnings / expected_events
        ),
        "last_pythia_event_size": metadata.get(
            "last_pythia_event_size", ""
        ),
        "output_size_bytes": (
            output_path.stat().st_size if output_path.exists() else -1
        ),
    }
    rows.append(row)

    label = case
    if rc != 0:
        problems.append(f"{label}: return code {rc}")
    if metadata.get("status") != "success":
        problems.append(f"{label}: status={metadata.get('status')!r}")
    if metadata.get("accepted_events") != expected_events:
        problems.append(
            f"{label}: accepted={metadata.get('accepted_events')}"
        )
    if hepmc_events != expected_events:
        problems.append(f"{label}: HepMC={hepmc_events}")

csv_path = root / "timeshower_component_summary.csv"
with csv_path.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print()
print(
    f"{'case':28s} {'acc':>5s} {'HepMC':>5s} "
    f"{'MEwarn':>7s} {'negDip':>7s} {'neg/event':>10s} "
    f"{'status':>9s}"
)
print("-" * 88)
for row in rows:
    print(
        f"{row['case']:28s} "
        f"{int(row['accepted_events']):5d} "
        f"{int(row['hepmc_events']):5d} "
        f"{int(row['me_weight_warning_count']):7d} "
        f"{int(row['negative_dipole_warning_count']):7d} "
        f"{float(row['negative_dipole_warnings_per_event']):10.4f} "
        f"{str(row['status']):>9s}"
    )

print()
print(f"Wrote {csv_path}")

if problems:
    print()
    print("STRUCTURAL FAILURES:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print()
print("TIMESHOWER COMPONENT ISOLATION STRUCTURAL PASS")
PY
