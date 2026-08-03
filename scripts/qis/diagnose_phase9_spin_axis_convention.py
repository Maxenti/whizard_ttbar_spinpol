#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

COMPONENTS = ("r", "n", "k")
DILEPTON_PARENTS = {"unpol_epmum", "LR100_epmum", "RL100_epmum"}
SQRTS_GEV = 365.0


@dataclass(frozen=True)
class Particle:
    pid: int
    status: int
    px: float
    py: float
    pz: float
    e: float
    m: float


def try_int(x: str) -> int | None:
    try:
        return int(x)
    except Exception:
        return None


def try_float(x: str) -> float | None:
    try:
        return float(x)
    except Exception:
        return None


def parse_particle_line(line: str) -> Particle | None:
    parts = line.split()
    if len(parts) < 10 or parts[0] != "P":
        return None

    pid = try_int(parts[3])
    px = try_float(parts[4])
    py = try_float(parts[5])
    pz = try_float(parts[6])
    e = try_float(parts[7])
    m = try_float(parts[8])
    status = try_int(parts[9])

    if None in (pid, px, py, pz, e, m, status):
        return None

    return Particle(int(pid), int(status), float(px), float(py), float(pz), float(e), float(m))


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def iter_hepmc_events(path: Path):
    event_index = -1
    particles: list[Particle] = []

    with path.open("r", errors="replace") as handle:
        for line in handle:
            if line.startswith("E "):
                if event_index >= 0:
                    yield event_index, particles
                event_index += 1
                particles = []
                continue

            if line.startswith("P "):
                p = parse_particle_line(line)
                if p is not None:
                    particles.append(p)

    if event_index >= 0:
        yield event_index, particles


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross3(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def norm3(a):
    return math.sqrt(dot3(a, a))


def unit3(a):
    n = norm3(a)
    if n <= 0:
        return None
    return (a[0] / n, a[1] / n, a[2] / n)


def add4(*vs):
    return (
        sum(v[0] for v in vs),
        sum(v[1] for v in vs),
        sum(v[2] for v in vs),
        sum(v[3] for v in vs),
    )


def v4(p: Particle):
    return (p.e, p.px, p.py, p.pz)


def spatial(v):
    return (v[1], v[2], v[3])


def beta_of(v):
    e, px, py, pz = v
    if e == 0:
        return None
    return (px / e, py / e, pz / e)


def boost(v, beta):
    e, px, py, pz = v
    bx, by, bz = beta
    b2 = bx * bx + by * by + bz * bz
    if b2 >= 1.0:
        raise ValueError(f"unphysical beta^2={b2}")
    if b2 <= 0:
        return v

    gamma = 1.0 / math.sqrt(1.0 - b2)
    bp = bx * px + by * py + bz * pz
    gamma2 = (gamma - 1.0) / b2

    return (
        gamma * (e - bp),
        px + gamma2 * bp * bx - gamma * bx * e,
        py + gamma2 * bp * by - gamma * by * e,
        pz + gamma2 * bp * bz - gamma * bz * e,
    )


def select_particle(particles: list[Particle], pid: int, preferred_statuses: tuple[int, ...]) -> Particle | None:
    for status in preferred_statuses:
        candidates = [p for p in particles if p.pid == pid and p.status == status]
        if candidates:
            return max(candidates, key=lambda p: p.e)

    candidates = [p for p in particles if p.pid == pid and p.status not in {4, 21}]
    if candidates:
        return max(candidates, key=lambda p: p.e)

    return None


def select_nominal_beam() -> tuple[float, float, float, float]:
    return (SQRTS_GEV / 2.0, 0.0, 0.0, SQRTS_GEV / 2.0)


def select_effective_beam(particles: list[Particle]) -> tuple[float, float, float, float] | None:
    # In these HepMC3 files, status 21 records are the post-ISR incoming
    # leptons. For e- use pid=11 and positive pz, preferring status 21.
    candidates = [p for p in particles if p.pid == 11 and p.status == 21]
    if not candidates:
        return None
    return v4(max(candidates, key=lambda p: p.e))


def boosted_axis(axis_ttbar, parent_ttbar):
    beta_parent = beta_of(parent_ttbar)
    if beta_parent is None:
        return None
    return unit3(spatial(boost((0.0, *axis_ttbar), beta_parent)))


def lepton_dir_parent_rest(lepton_lab, parent_lab):
    beta_parent = beta_of(parent_lab)
    if beta_parent is None:
        return None
    return unit3(spatial(boost(lepton_lab, beta_parent)))


def event_contribs(particles: list[Particle], axis_mode: str) -> dict[str, float] | None:
    b = select_particle(particles, 5, (23, 1))
    bbar = select_particle(particles, -5, (23, 1))
    eplus = select_particle(particles, -11, (1, 23))
    nue = select_particle(particles, 12, (1, 23))
    muminus = select_particle(particles, 13, (1, 23))
    anumu = select_particle(particles, -14, (1, 23))

    if any(x is None for x in [b, bbar, eplus, nue, muminus, anumu]):
        return None

    top_lab = add4(v4(b), v4(eplus), v4(nue))
    antitop_lab = add4(v4(bbar), v4(muminus), v4(anumu))
    ttbar_lab = add4(top_lab, antitop_lab)

    beta_ttbar = beta_of(ttbar_lab)
    if beta_ttbar is None:
        return None

    top_ttbar = boost(top_lab, beta_ttbar)
    antitop_ttbar = boost(antitop_lab, beta_ttbar)

    if axis_mode == "nominal_beam":
        beam_lab = select_nominal_beam()
    elif axis_mode == "effective_status21_beam":
        beam_lab = select_effective_beam(particles)
        if beam_lab is None:
            return None
    else:
        raise ValueError(f"unknown axis_mode={axis_mode}")

    beam_ttbar = boost(beam_lab, beta_ttbar)

    k_hat = unit3(spatial(top_ttbar))
    beam_hat = unit3(spatial(beam_ttbar))
    if k_hat is None or beam_hat is None:
        return None

    n_hat = unit3(cross3(beam_hat, k_hat))
    if n_hat is None:
        return None

    r_hat = unit3(cross3(n_hat, k_hat))
    if r_hat is None:
        return None

    axes_ttbar = {"r": r_hat, "n": n_hat, "k": k_hat}

    lp_dir = lepton_dir_parent_rest(v4(eplus), top_lab)
    lm_dir = lepton_dir_parent_rest(v4(muminus), antitop_lab)
    if lp_dir is None or lm_dir is None:
        return None

    axes_top = {}
    axes_antitop = {}
    for c, axis in axes_ttbar.items():
        axes_top[c] = boosted_axis(axis, top_ttbar)
        axes_antitop[c] = boosted_axis(axis, antitop_ttbar)
        if axes_top[c] is None or axes_antitop[c] is None:
            return None

    uplus = {c: dot3(lp_dir, axes_top[c]) for c in COMPONENTS}
    uminus = {c: dot3(lm_dir, axes_antitop[c]) for c in COMPONENTS}

    out = {}
    for c in COMPONENTS:
        out[f"Bplus_{c}"] = 3.0 * uplus[c]
        out[f"Bminus_{c}"] = -3.0 * uminus[c]
    for i in COMPONENTS:
        for j in COMPONENTS:
            out[f"C_{i}{j}"] = -9.0 * uplus[i] * uminus[j]

    return out


def mean(rows, key):
    return sum(r[key] for r in rows) / len(rows)


def summarize(rows_by_parent_mode):
    keys = []
    for c in COMPONENTS:
        keys.append(f"Bplus_{c}")
    for c in COMPONENTS:
        keys.append(f"Bminus_{c}")
    for i in COMPONENTS:
        for j in COMPONENTS:
            keys.append(f"C_{i}{j}")

    out = {}
    for parent, modes in rows_by_parent_mode.items():
        out[parent] = {}
        for mode, rows in modes.items():
            out[parent][mode] = {
                "n_events": len(rows),
                "moments": {k: mean(rows, k) for k in keys},
            }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--summary-json", required=True)
    args = ap.parse_args()

    inventory = [r for r in load_jsonl(Path(args.inventory)) if r.get("parent_label") in DILEPTON_PARENTS]

    rows = {
        "unpol_epmum": {"nominal_beam": [], "effective_status21_beam": []},
        "LR100_epmum": {"nominal_beam": [], "effective_status21_beam": []},
    }

    failures = []

    for source_i, record in enumerate(inventory, 1):
        parent = record["parent_label"]
        hepmc = Path(record["hepmc"])
        print(f"AXIS_SOURCE={source_i}/{len(inventory)} PARENT={parent} LABEL={record['label']}", flush=True)

        for event_index, particles in iter_hepmc_events(hepmc):
            for mode in ("nominal_beam", "effective_status21_beam"):
                contrib = event_contribs(particles, mode)
                if contrib is None:
                    if len(failures) < 20:
                        failures.append({
                            "parent_label": parent,
                            "label": record["label"],
                            "event_index": event_index,
                            "axis_mode": mode,
                        })
                    continue
                rows[parent][mode].append(contrib)

    results = summarize(rows)

    comparisons = []
    for parent, modes in results.items():
        nominal = modes["nominal_beam"]["moments"]
        effective = modes["effective_status21_beam"]["moments"]
        for key in nominal:
            comparisons.append({
                "parent_label": parent,
                "key": key,
                "nominal_beam": nominal[key],
                "effective_status21_beam": effective[key],
                "delta_effective_minus_nominal": effective[key] - nominal[key],
                "abs_delta": abs(effective[key] - nominal[key]),
            })

    comparisons.sort(key=lambda r: r["abs_delta"], reverse=True)

    payload = {
        "schema_version": 1,
        "status": "PASS" if not failures else "PASS_WITH_FAILURES",
        "inventory": str(Path(args.inventory)),
        "axis_modes": ["nominal_beam", "effective_status21_beam"],
        "basis_component_order": list(COMPONENTS),
        "results": results,
        "comparisons": comparisons,
        "failures": failures,
        "notes": [
            "Compares spin moments using nominal e- beam axis versus status-21 post-ISR/effective e- beam axis.",
            "This is a convention diagnostic, not a final physics claim.",
            "If deltas are negligible relative to statistical errors, nominal-beam convention can be frozen for this Phase 9 truth-candidate product.",
        ],
    }

    out_json = Path(args.output_json)
    out_csv = Path(args.output_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        fields = ["parent_label", "key", "nominal_beam", "effective_status21_beam", "delta_effective_minus_nominal", "abs_delta"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for r in comparisons:
            writer.writerow({k: r[k] for k in fields})

    summary = {
        "schema_version": 1,
        "status": payload["status"],
        "axis_json": str(out_json),
        "axis_csv": str(out_csv),
        "inventory": payload["inventory"],
        "axis_modes": payload["axis_modes"],
        "basis_component_order": payload["basis_component_order"],
        "n_events": {
            parent: {mode: results[parent][mode]["n_events"] for mode in results[parent]}
            for parent in results
        },
        "top_axis_deltas": comparisons[:15],
        "max_abs_delta": comparisons[0]["abs_delta"] if comparisons else None,
        "notes": payload["notes"],
    }

    Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"AXIS_CONVENTION_STATUS={payload['status']}")
    for parent in sorted(results):
        for mode in sorted(results[parent]):
            print(f"AXIS_EVENTS {parent} {mode} {results[parent][mode]['n_events']}")
    print(f"MAX_ABS_AXIS_DELTA={summary['max_abs_delta']}")
    print(f"WROTE_JSON={out_json}")
    print(f"WROTE_CSV={out_csv}")
    print(f"WROTE_SUMMARY={args.summary_json}")

    return 0 if payload["status"] in {"PASS", "PASS_WITH_FAILURES"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
