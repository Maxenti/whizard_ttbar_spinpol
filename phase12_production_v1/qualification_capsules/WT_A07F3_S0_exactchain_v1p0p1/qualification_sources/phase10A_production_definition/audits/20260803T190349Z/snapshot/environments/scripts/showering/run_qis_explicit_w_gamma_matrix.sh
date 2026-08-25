#!/usr/bin/env bash
#
# Eight-sample closure test for the preferred QIS shower candidate:
#
#   canonical LHA v2
#   + explicit W resonances v3
#   + default PYTHIA MECs
#   + TimeShower:QEDshowerByGamma = off
#
# The control keeps photon conversions enabled.  Both modes use the same
# per-sample random seed, but their random streams will diverge after the first
# setting-dependent branching decision; comparisons are therefore
# distribution-level rather than strict event-paired shower comparisons.
#
# Outputs:
#   lhe/v2/
#   lhe/v3/
#   summaries/v2/
#   summaries/v3/
#   hepmc3/{gamma_on,gamma_off}/
#   metadata/{gamma_on,gamma_off}/
#   logs/{gamma_on,gamma_off}/
#   explicit_w_gamma_matrix.csv
#   explicit_w_gamma_matrix.md
#
# Usage:
#   source setup_lxplus.sh
#   ./scripts/showering/run_qis_explicit_w_gamma_matrix.sh
#
# Optional:
#   REPO=/path/to/repo
#   OUT=/tmp/$USER/qis_explicit_w_gamma_matrix
#   EVENTS=200
#   SEED_BASE=883001
#

set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
OUT=${OUT:-/tmp/$USER/qis_explicit_w_gamma_matrix}
EVENTS=${EVENTS:-200}
SEED_BASE=${SEED_BASE:-883001}

INPUT_DIR="$REPO/tests/qis/data/smoke_lhe"
CANONICALIZER="$REPO/scripts/showering/canonicalize_whizard_lhe_for_pythia.py"
W_ADAPTER="$REPO/scripts/showering/insert_explicit_w_resonances.py"
EXE="$REPO/build/qis_lhe_to_hepmc3"
SETTINGS="$REPO/configs/pythia/level_a.cmnd"

export PYTHONDONTWRITEBYTECODE=1

die() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -d "$INPUT_DIR" ]] || die "missing input directory: $INPUT_DIR"
[[ -x "$CANONICALIZER" ]] || die "missing canonicalizer: $CANONICALIZER"
[[ -x "$W_ADAPTER" ]] || die "missing explicit-W adapter: $W_ADAPTER"
[[ -x "$EXE" ]] || die "missing shower executable: $EXE"
[[ -f "$SETTINGS" ]] || die "missing PYTHIA settings: $SETTINGS"

grep -q 'rewired_isr_photons' "$CANONICALIZER" \
  || die "canonicalizer is not v2"

python3 - <<'PY'
import importlib
importlib.import_module("pyhepmc")
print("Python dependency check: PASS")
PY

rm -rf "$OUT"

for mode in gamma_on gamma_off; do
  mkdir -p \
    "$OUT/hepmc3/$mode" \
    "$OUT/metadata/$mode" \
    "$OUT/logs/$mode" \
    "$OUT/return_codes/$mode"
done

mkdir -p \
  "$OUT/lhe/v2" \
  "$OUT/lhe/v3" \
  "$OUT/summaries/v2" \
  "$OUT/summaries/v3"

shopt -s nullglob
inputs=("$INPUT_DIR"/*.lhe)
shopt -u nullglob

(( ${#inputs[@]} == 8 )) \
  || die "expected exactly 8 smoke LHE files, found ${#inputs[@]}"

sample_index=0

for input in "${inputs[@]}"; do
  sample=$(basename "$input" .lhe)
  seed=$((SEED_BASE + sample_index))

  v2="$OUT/lhe/v2/${sample}.canonical_v2.lhe"
  v3="$OUT/lhe/v3/${sample}.explicit_w_v3.lhe"
  v2_summary="$OUT/summaries/v2/${sample}.json"
  v3_summary="$OUT/summaries/v3/${sample}.json"

  echo
  echo "======================================================================"
  echo "PREPARE: $sample"
  echo "======================================================================"

  python3 "$CANONICALIZER" \
    --input "$input" \
    --output "$v2" \
    --summary "$v2_summary"

  python3 "$W_ADAPTER" \
    --input "$v2" \
    --output "$v3" \
    --summary "$v3_summary"

  python3 - "$v2_summary" "$v3_summary" "$EVENTS" <<'PY'
import json
import sys
from pathlib import Path

v2 = json.loads(Path(sys.argv[1]).read_text())
v3 = json.loads(Path(sys.argv[2]).read_text())
events = int(sys.argv[3])

assert v2["total_events"] == events, v2
assert v2["canonicalized_events"] == events, v2
assert v2["removed_bridge_particles"] == 2 * events, v2
assert v2["promoted_beam_particles"] == 2 * events, v2
assert v2["rewired_isr_photons"] == 2 * events, v2
assert v2["removed_sqme_prc_tags"] == events, v2
assert v2["max_rel_closure"] <= 1.0e-7, v2

assert v3["total_events"] == events, v3
assert v3["explicit_w_events"] == events, v3
assert v3["inserted_w_resonances"] == 2 * events, v3
assert v3["max_vertex_rel_closure"] <= 1.0e-7, v3

print("V2 + explicit-W v3 contracts: PASS")
PY

  for mode in gamma_on gamma_off; do
    output="$OUT/hepmc3/$mode/${sample}.hepmc3"
    metadata="$OUT/metadata/$mode/${sample}.json"
    log="$OUT/logs/$mode/${sample}.log"
    rc_file="$OUT/return_codes/$mode/${sample}.rc"

    overrides=()
    if [[ "$mode" == gamma_off ]]; then
      overrides+=(--set "TimeShower:QEDshowerByGamma = off")
    fi

    echo
    echo "----------------------------------------------------------------------"
    echo "SHOWER: sample=$sample mode=$mode seed=$seed events=$EVENTS"
    echo "----------------------------------------------------------------------"

    set +e
    "$EXE" \
      --input "$v3" \
      --output "$output" \
      --metadata "$metadata" \
      --settings "$SETTINGS" \
      --campaign-id explicit_w_gamma_matrix \
      --sample-id "$sample" \
      --shard-id "$mode" \
      --seed "$seed" \
      --max-events "$EVENTS" \
      "${overrides[@]}" \
      >"$log" 2>&1
    rc=$?
    set -e

    printf '%s\n' "$rc" >"$rc_file"
    echo "return code: $rc"

    if (( rc != 0 )); then
      tail -100 "$log" || true
    fi
  done

  sample_index=$((sample_index + 1))
done

export QIS_GAMMA_MATRIX_OUT="$OUT"
export QIS_GAMMA_MATRIX_EVENTS="$EVENTS"

python3 - <<'PY'
from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import pyhepmc

root = Path(os.environ["QIS_GAMMA_MATRIX_OUT"])
expected_events = int(os.environ["QIS_GAMMA_MATRIX_EVENTS"])
modes = ("gamma_on", "gamma_off")

samples = sorted(
    path.name.removesuffix(".explicit_w_v3.lhe")
    for path in (root / "lhe" / "v3").glob("*.explicit_w_v3.lhe")
)

if len(samples) != 8:
    raise SystemExit(f"ERROR: expected 8 v3 samples, found {len(samples)}")

fermions = {1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16}
charged_abs_pids = {
    1, 2, 3, 4, 5, 6,
    11, 13, 15,
    24,
    211, 321, 2212,
}


def warning_count(text: str, message: str) -> int:
    pattern = re.compile(
        rf"^\s*\|\s*(\d+)\s+Warning in {re.escape(message)}",
        re.MULTILINE,
    )
    found = pattern.findall(text)
    if found:
        return int(found[-1])
    return text.count(f"Warning in {message}")


def analyze_hepmc(path: Path) -> dict[str, object]:
    events = 0
    conversion_vertices = 0
    events_with_conversion = 0
    conversion_species = Counter()

    stable_particles = 0
    stable_charged = 0
    stable_photons = 0
    stable_photons_gt_1mev = 0
    stable_photons_gt_100mev = 0
    stable_photons_gt_1gev = 0
    stable_photon_energy_gev = 0.0

    with pyhepmc.open(path) as stream:
        for event in stream:
            events += 1
            event_conversions = 0

            for particle in event.particles:
                if particle.pid == 22 and particle.end_vertex is not None:
                    daughters = list(particle.end_vertex.particles_out)
                    if (
                        len(daughters) == 2
                        and daughters[0].pid == -daughters[1].pid
                        and abs(daughters[0].pid) in fermions
                    ):
                        conversion_vertices += 1
                        event_conversions += 1
                        conversion_species[abs(daughters[0].pid)] += 1

                is_stable = particle.status == 1 and particle.end_vertex is None
                if not is_stable:
                    continue

                stable_particles += 1

                if abs(particle.pid) in charged_abs_pids:
                    stable_charged += 1

                if particle.pid != 22:
                    continue

                energy = float(particle.momentum.e)
                stable_photons += 1
                stable_photon_energy_gev += energy

                if energy > 1.0e-3:
                    stable_photons_gt_1mev += 1
                if energy > 1.0e-1:
                    stable_photons_gt_100mev += 1
                if energy > 1.0:
                    stable_photons_gt_1gev += 1

            if event_conversions:
                events_with_conversion += 1

    return {
        "hepmc_events": events,
        "conversion_vertices": conversion_vertices,
        "events_with_conversion": events_with_conversion,
        "conversion_species_json": json.dumps(
            dict(sorted(conversion_species.items())),
            sort_keys=True,
        ),
        "stable_particles": stable_particles,
        "stable_charged": stable_charged,
        "stable_photons": stable_photons,
        "stable_photons_gt_1mev": stable_photons_gt_1mev,
        "stable_photons_gt_100mev": stable_photons_gt_100mev,
        "stable_photons_gt_1gev": stable_photons_gt_1gev,
        "stable_photon_energy_gev": stable_photon_energy_gev,
    }


rows: list[dict[str, object]] = []
problems: list[str] = []

for sample in samples:
    for mode in modes:
        output = root / "hepmc3" / mode / f"{sample}.hepmc3"
        metadata_path = root / "metadata" / mode / f"{sample}.json"
        log_path = root / "logs" / mode / f"{sample}.log"
        rc_path = root / "return_codes" / mode / f"{sample}.rc"

        rc = int(rc_path.read_text().strip())
        metadata = json.loads(metadata_path.read_text())
        log_text = log_path.read_text(errors="replace")
        analysis = analyze_hepmc(output)

        me_warnings = warning_count(
            log_text,
            "SimpleTimeShower::findMEcorr: ME weight above PS one",
        )
        negative_warnings = warning_count(
            log_text,
            "SimpleTimeShower::pTnext: negative dipole mass",
        )

        row = {
            "sample_id": sample,
            "mode": mode,
            "return_code": rc,
            "status": metadata.get("status"),
            "accepted_events": metadata.get("accepted_events"),
            **analysis,
            "me_weight_warning_count": me_warnings,
            "negative_dipole_warning_count": negative_warnings,
            "mean_stable_particles_per_event": (
                int(analysis["stable_particles"]) / expected_events
            ),
            "mean_stable_charged_per_event": (
                int(analysis["stable_charged"]) / expected_events
            ),
            "mean_stable_photons_per_event": (
                int(analysis["stable_photons"]) / expected_events
            ),
            "mean_stable_photons_gt_100mev_per_event": (
                int(analysis["stable_photons_gt_100mev"]) / expected_events
            ),
            "mean_stable_photon_energy_gev_per_event": (
                float(analysis["stable_photon_energy_gev"]) / expected_events
            ),
            "output_size_bytes": output.stat().st_size,
        }
        rows.append(row)

        label = f"{sample}/{mode}"
        if rc != 0:
            problems.append(f"{label}: return code {rc}")
        if metadata.get("status") != "success":
            problems.append(f"{label}: status={metadata.get('status')!r}")
        if metadata.get("accepted_events") != expected_events:
            problems.append(
                f"{label}: accepted={metadata.get('accepted_events')}"
            )
        if analysis["hepmc_events"] != expected_events:
            problems.append(
                f"{label}: HepMC={analysis['hepmc_events']}"
            )
        if mode == "gamma_off":
            if me_warnings != 0:
                problems.append(f"{label}: ME warnings={me_warnings}")
            if negative_warnings != 0:
                problems.append(
                    f"{label}: negative-dipole warnings={negative_warnings}"
                )
            if analysis["conversion_vertices"] != 0:
                problems.append(
                    f"{label}: conversions={analysis['conversion_vertices']}"
                )

csv_path = root / "explicit_w_gamma_matrix.csv"
with csv_path.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

totals: dict[str, dict[str, float]] = defaultdict(
    lambda: defaultdict(float)
)
for row in rows:
    mode = str(row["mode"])
    for key in (
        "accepted_events",
        "hepmc_events",
        "conversion_vertices",
        "events_with_conversion",
        "stable_particles",
        "stable_charged",
        "stable_photons",
        "stable_photons_gt_1mev",
        "stable_photons_gt_100mev",
        "stable_photons_gt_1gev",
        "stable_photon_energy_gev",
        "me_weight_warning_count",
        "negative_dipole_warning_count",
    ):
        totals[mode][key] += float(row[key])
    totals[mode]["runs"] += 1

md_path = root / "explicit_w_gamma_matrix.md"
with md_path.open("w") as stream:
    stream.write("# Explicit-W photon-conversion closure matrix\n\n")
    stream.write(
        f"- Samples: 8\n"
        f"- Events per sample and mode: {expected_events}\n"
        f"- Modes: gamma_on, gamma_off\n\n"
    )
    stream.write(
        "| Mode | Accepted | HepMC | Conversion vertices | "
        "Events with conversion | Stable photons | "
        "ME warnings | Negative-dipole warnings |\n"
    )
    stream.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
    for mode in modes:
        t = totals[mode]
        stream.write(
            f"| {mode} | {int(t['accepted_events'])} | "
            f"{int(t['hepmc_events'])} | "
            f"{int(t['conversion_vertices'])} | "
            f"{int(t['events_with_conversion'])} | "
            f"{int(t['stable_photons'])} | "
            f"{int(t['me_weight_warning_count'])} | "
            f"{int(t['negative_dipole_warning_count'])} |\n"
        )

print()
print(
    f"{'sample':55s} {'mode':10s} {'acc':>5s} {'conv':>5s} "
    f"{'evtconv':>7s} {'photons':>8s} {'>100MeV':>8s} "
    f"{'MEwarn':>7s} {'negDip':>7s}"
)
print("-" * 126)
for row in rows:
    print(
        f"{str(row['sample_id']):55s} "
        f"{str(row['mode']):10s} "
        f"{int(row['accepted_events']):5d} "
        f"{int(row['conversion_vertices']):5d} "
        f"{int(row['events_with_conversion']):7d} "
        f"{int(row['stable_photons']):8d} "
        f"{int(row['stable_photons_gt_100mev']):8d} "
        f"{int(row['me_weight_warning_count']):7d} "
        f"{int(row['negative_dipole_warning_count']):7d}"
    )

print()
print("MODE TOTALS")
print("-" * 100)
for mode in modes:
    t = totals[mode]
    print(
        f"{mode:10s} "
        f"accepted={int(t['accepted_events']):5d} "
        f"HepMC={int(t['hepmc_events']):5d} "
        f"conversions={int(t['conversion_vertices']):4d} "
        f"events_with_conversion={int(t['events_with_conversion']):4d} "
        f"stable_photons={int(t['stable_photons']):7d} "
        f"MEwarn={int(t['me_weight_warning_count']):5d} "
        f"negDip={int(t['negative_dipole_warning_count']):5d}"
    )

print()
print(f"Wrote {csv_path}")
print(f"Wrote {md_path}")

if problems:
    print()
    print("FAILURES:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print()
print("EXPLICIT-W GAMMA MATRIX STRUCTURAL PASS")
PY
