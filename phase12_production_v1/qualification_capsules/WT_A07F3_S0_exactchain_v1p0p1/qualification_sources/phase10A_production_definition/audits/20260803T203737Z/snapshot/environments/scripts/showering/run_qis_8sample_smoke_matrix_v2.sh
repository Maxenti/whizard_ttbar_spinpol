#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
OUT=${OUT:-/tmp/$USER/qis_8sample_smoke_matrix_v2}
EVENTS=${EVENTS:-200}

INPUT_DIR="$REPO/tests/qis/data/smoke_lhe"
CANONICALIZER="$REPO/scripts/showering/canonicalize_whizard_lhe_for_pythia.py"
EXE="$REPO/build/qis_lhe_to_hepmc3"
SETTINGS="$REPO/configs/pythia/level_a.cmnd"

export PYTHONDONTWRITEBYTECODE=1

die() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -d "$REPO" ]] || die "repository does not exist: $REPO"
[[ -d "$INPUT_DIR" ]] || die "smoke input directory does not exist: $INPUT_DIR"
[[ -x "$CANONICALIZER" ]] || die "canonicalizer is not executable: $CANONICALIZER"
[[ -x "$EXE" ]] || die "shower executable is not executable: $EXE"
[[ -f "$SETTINGS" ]] || die "PYTHIA settings file does not exist: $SETTINGS"

grep -q 'rewired_isr_photons' "$CANONICALIZER" \
  || die "canonicalizer does not appear to be v2"

python3 - <<'PY'
import importlib
importlib.import_module("pyhepmc")
print("Python dependency check: PASS")
PY

rm -rf "$OUT"

for mode in default meextended_off mecorrections_off; do
  mkdir -p \
    "$OUT/hepmc3/$mode" \
    "$OUT/metadata/$mode" \
    "$OUT/logs/$mode"
done

mkdir -p \
  "$OUT/canonical" \
  "$OUT/canonical_summaries" \
  "$OUT/return_codes"

shopt -s nullglob
inputs=("$INPUT_DIR"/*.lhe)
shopt -u nullglob

(( ${#inputs[@]} == 8 )) \
  || die "expected exactly 8 smoke LHE files, found ${#inputs[@]}"

modes=(default meextended_off mecorrections_off)
sample_index=0

for input in "${inputs[@]}"; do
  sample=$(basename "$input" .lhe)
  canonical="$OUT/canonical/${sample}.canonical_v2.lhe"
  canonical_summary="$OUT/canonical_summaries/${sample}.json"

  echo
  echo "======================================================================"
  echo "CANONICALIZE: $sample"
  echo "======================================================================"

  python3 "$CANONICALIZER" \
    --input "$input" \
    --output "$canonical" \
    --summary "$canonical_summary"

  python3 - "$canonical" "$canonical_summary" "$EVENTS" "$sample" <<'PY'
import json
import sys
from pathlib import Path

canonical = Path(sys.argv[1])
summary = json.loads(Path(sys.argv[2]).read_text())
expected_events = int(sys.argv[3])
sample_id = sys.argv[4]

assert summary["total_events"] == expected_events, summary
assert summary["canonicalized_events"] == expected_events, summary
assert summary["removed_bridge_particles"] == 2 * expected_events, summary
assert summary["promoted_beam_particles"] == 2 * expected_events, summary
assert summary["rewired_isr_photons"] == 2 * expected_events, summary
assert summary["removed_sqme_prc_tags"] == expected_events, summary
assert summary["max_rel_closure"] <= 1.0e-7, summary

if sample_id.startswith("ee_"):
    incoming_pid = 11
elif sample_id.startswith("mumu_"):
    incoming_pid = 13
else:
    raise AssertionError(
        f"unsupported sample prefix for beam validation: {sample_id}"
    )

lines = canonical.read_text().splitlines()
start = lines.index("<event>")
nup = int(lines[start + 1].split()[0])
particles = [line.split() for line in lines[start + 2:start + 2 + nup]]

expected = [
    [str(incoming_pid),  "-1", "0", "0"],
    [str(-incoming_pid), "-1", "0", "0"],
    ["6",                 "2", "1", "2"],
    ["-6",                "2", "1", "2"],
    ["22",                "1", "1", "2"],
    ["22",                "1", "1", "2"],
]
for index, wanted in enumerate(expected):
    actual = particles[index][0:4]
    assert actual == wanted, (
        f"{sample_id}: particle {index + 1}: "
        f"expected {wanted}, found {actual}"
    )

print(
    "Canonical v2 contract: PASS "
    f"sample={sample_id} incoming_pid={incoming_pid}"
)
PY

  mode_index=0
  for mode in "${modes[@]}"; do
    output="$OUT/hepmc3/$mode/${sample}.hepmc3"
    metadata="$OUT/metadata/$mode/${sample}.metadata.json"
    log="$OUT/logs/$mode/${sample}.log"
    rc_file="$OUT/return_codes/${sample}.${mode}.rc"

    seed=$((880001 + 10 * sample_index + mode_index))
    overrides=()

    case "$mode" in
      default)
        ;;
      meextended_off)
        overrides+=(--set "TimeShower:MEextended = off")
        ;;
      mecorrections_off)
        overrides+=(--set "TimeShower:MEcorrections = off")
        ;;
      *)
        die "unknown mode: $mode"
        ;;
    esac

    echo
    echo "----------------------------------------------------------------------"
    echo "SHOWER: sample=$sample mode=$mode seed=$seed events=$EVENTS"
    echo "----------------------------------------------------------------------"

    set +e
    "$EXE" \
      --input "$canonical" \
      --output "$output" \
      --metadata "$metadata" \
      --settings "$SETTINGS" \
      --campaign-id qis_8sample_smoke_matrix_v2 \
      --sample-id "$sample" \
      --shard-id "$mode" \
      --seed "$seed" \
      --max-events "$EVENTS" \
      "${overrides[@]}" \
      >"$log" 2>&1
    rc=$?
    set -e

    printf '%s\n' "$rc" > "$rc_file"
    echo "return code: $rc"

    if (( rc != 0 )); then
      tail -80 "$log" || true
    fi

    mode_index=$((mode_index + 1))
  done

  sample_index=$((sample_index + 1))
done

export QIS_SMOKE_MATRIX_OUT="$OUT"
export QIS_SMOKE_MATRIX_EVENTS="$EVENTS"

python3 - <<'PY'
from __future__ import annotations

import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path

import pyhepmc

root = Path(os.environ["QIS_SMOKE_MATRIX_OUT"])
expected_events = int(os.environ["QIS_SMOKE_MATRIX_EVENTS"])
modes = ("default", "meextended_off", "mecorrections_off")

samples = sorted(
    path.name.removesuffix(".canonical_v2.lhe")
    for path in (root / "canonical").glob("*.canonical_v2.lhe")
)

if len(samples) != 8:
    raise SystemExit(f"ERROR: expected 8 canonical samples, found {len(samples)}")


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

for sample in samples:
    canonical_summary = json.loads(
        (root / "canonical_summaries" / f"{sample}.json").read_text()
    )

    for mode in modes:
        metadata_path = root / "metadata" / mode / f"{sample}.metadata.json"
        output_path = root / "hepmc3" / mode / f"{sample}.hepmc3"
        log_path = root / "logs" / mode / f"{sample}.log"
        rc_path = root / "return_codes" / f"{sample}.{mode}.rc"

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
        neg_warnings = warning_count(
            log_text,
            "SimpleTimeShower::pTnext: negative dipole mass",
        )

        row = {
            "sample_id": sample,
            "mode": mode,
            "return_code": rc,
            "status": metadata.get("status", "missing"),
            "attempted_events": metadata.get("attempted_events", -1),
            "accepted_events": metadata.get("accepted_events", -1),
            "failed_events": metadata.get("failed_events", -1),
            "hepmc_events": hepmc_events,
            "sigma_gen_mb": metadata.get("sigma_gen_mb", ""),
            "weight_sum": metadata.get("weight_sum", ""),
            "weight_sum2": metadata.get("weight_sum2", ""),
            "last_pythia_event_size": metadata.get("last_pythia_event_size", ""),
            "me_weight_warning_count": me_warnings,
            "negative_dipole_warning_count": neg_warnings,
            "me_weight_warnings_per_event": me_warnings / expected_events,
            "negative_dipole_warnings_per_event": neg_warnings / expected_events,
            "canonicalized_events": canonical_summary.get(
                "canonicalized_events", -1
            ),
            "rewired_isr_photons": canonical_summary.get(
                "rewired_isr_photons", -1
            ),
            "max_abs_closure_gev": canonical_summary.get(
                "max_abs_closure_gev", ""
            ),
            "max_rel_closure": canonical_summary.get("max_rel_closure", ""),
            "output_size_bytes": (
                output_path.stat().st_size if output_path.exists() else -1
            ),
        }
        rows.append(row)

        label = f"{sample}/{mode}"
        if rc != 0:
            problems.append(f"{label}: return code {rc}")
        if metadata.get("status") != "success":
            problems.append(f"{label}: status={metadata.get('status')!r}")
        if metadata.get("accepted_events") != expected_events:
            problems.append(
                f"{label}: accepted_events={metadata.get('accepted_events')}"
            )
        if hepmc_events != expected_events:
            problems.append(f"{label}: HepMC events={hepmc_events}")

csv_path = root / "smoke_matrix_summary.csv"
with csv_path.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

totals = defaultdict(
    lambda: {
        "runs": 0,
        "accepted": 0,
        "hepmc": 0,
        "me_warnings": 0,
        "negative_dipole_warnings": 0,
    }
)

for row in rows:
    mode_totals = totals[row["mode"]]
    mode_totals["runs"] += 1
    mode_totals["accepted"] += int(row["accepted_events"])
    mode_totals["hepmc"] += int(row["hepmc_events"])
    mode_totals["me_warnings"] += int(row["me_weight_warning_count"])
    mode_totals["negative_dipole_warnings"] += int(
        row["negative_dipole_warning_count"]
    )

md_path = root / "smoke_matrix_summary.md"
with md_path.open("w") as stream:
    stream.write("# QIS eight-sample PYTHIA smoke matrix\n\n")
    stream.write(
        f"- Samples: 8\n"
        f"- Events per sample and mode: {expected_events}\n"
        f"- Modes: 3\n"
        f"- Runs: {len(rows)}\n\n"
    )
    stream.write(
        "| Mode | Runs | Accepted | HepMC | ME-weight warnings | "
        "Negative-dipole warnings |\n"
    )
    stream.write("|---|---:|---:|---:|---:|---:|\n")
    for mode in modes:
        t = totals[mode]
        stream.write(
            f"| {mode} | {t['runs']} | {t['accepted']} | "
            f"{t['hepmc']} | {t['me_warnings']} | "
            f"{t['negative_dipole_warnings']} |\n"
        )

print()
print("=" * 166)
header = (
    f"{'sample':55s} "
    f"{'mode':19s} "
    f"{'acc':>5s} "
    f"{'HepMC':>5s} "
    f"{'MEwarn':>7s} "
    f"{'negDip':>7s} "
    f"{'status':>9s}"
)
print(header)
print("-" * len(header))
for row in rows:
    print(
        f"{row['sample_id']:55s} "
        f"{row['mode']:19s} "
        f"{int(row['accepted_events']):5d} "
        f"{int(row['hepmc_events']):5d} "
        f"{int(row['me_weight_warning_count']):7d} "
        f"{int(row['negative_dipole_warning_count']):7d} "
        f"{row['status']:>9s}"
    )
print("=" * 166)

print()
print("MODE TOTALS")
print("-" * 90)
for mode in modes:
    t = totals[mode]
    print(
        f"{mode:19s} "
        f"runs={t['runs']:2d} "
        f"accepted={t['accepted']:5d} "
        f"HepMC={t['hepmc']:5d} "
        f"MEwarn={t['me_warnings']:6d} "
        f"negDip={t['negative_dipole_warnings']:6d}"
    )

print()
print(f"Wrote {csv_path}")
print(f"Wrote {md_path}")

if problems:
    print()
    print("STRUCTURAL FAILURES:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print()
print(
    f"STRUCTURAL SMOKE MATRIX PASS: {len(rows)}/{len(rows)} runs "
    f"accepted {expected_events} events."
)
PY

echo
echo "Smoke matrix complete: $OUT"
echo "Summary CSV: $OUT/smoke_matrix_summary.csv"
echo "Summary Markdown: $OUT/smoke_matrix_summary.md"
