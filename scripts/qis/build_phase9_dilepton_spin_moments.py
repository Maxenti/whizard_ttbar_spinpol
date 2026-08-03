#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

COMPONENTS = ("r", "n", "k")
DILEPTON_PARENTS = {"unpol_epmum", "LR100_epmum", "RL100_epmum"}
SQRTS_GEV = 365.0


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


def obj4(obj: dict[str, Any]):
    return (float(obj["e"]), float(obj["px"]), float(obj["py"]), float(obj["pz"]))


def spatial(v):
    return (v[1], v[2], v[3])


def mass4(v):
    e, px, py, pz = v
    m2 = e * e - px * px - py * py - pz * pz
    return math.sqrt(max(m2, 0.0))


def beta_of(v):
    e, px, py, pz = v
    if e == 0:
        return None
    return (px / e, py / e, pz / e)


def boost(v, beta):
    """Lorentz boost four-vector by velocity beta.

    Convention: boost(v, beta) applies

      E' = gamma (E - beta · p)

    With this convention, to transform a lab-frame four-vector into the rest
    frame of an object with four-momentum P, use beta = P_vec / P_E.
    """
    e, px, py, pz = v
    bx, by, bz = beta
    b2 = bx * bx + by * by + bz * bz
    if b2 >= 1.0:
        raise ValueError(f"unphysical beta^2={b2}")

    if b2 <= 0.0:
        return v

    gamma = 1.0 / math.sqrt(1.0 - b2)
    bp = bx * px + by * py + bz * pz
    gamma2 = (gamma - 1.0) / b2

    pxp = px + gamma2 * bp * bx - gamma * bx * e
    pyp = py + gamma2 * bp * by - gamma * by * e
    pzp = pz + gamma2 * bp * bz - gamma * bz * e
    ep = gamma * (e - bp)

    return (ep, pxp, pyp, pzp)


def neg_beta(beta):
    return (-beta[0], -beta[1], -beta[2])


def boost_axis_to_rest(axis_ttbar, parent_p4_ttbar):
    """Boost a spatial spin axis from ttbar rest into a parent rest frame."""
    beta_parent = beta_of(parent_p4_ttbar)
    if beta_parent is None:
        return None

    axis4 = (0.0, axis_ttbar[0], axis_ttbar[1], axis_ttbar[2])
    axis_parent = boost(axis4, beta_parent)
    return unit3(spatial(axis_parent))


def lepton_dir_in_parent_rest(lepton_lab, parent_lab):
    beta_parent_lab = beta_of(parent_lab)
    if beta_parent_lab is None:
        return None
    lep_parent = boost(lepton_lab, beta_parent_lab)
    return unit3(spatial(lep_parent))


def get_required_objects(record):
    objs = record.get("objects", {})
    required = ["b", "bbar", "lplus", "nu_e", "lminus", "anti_nu_mu"]
    missing = [k for k in required if k not in objs]
    if missing:
        return None, missing
    return objs, []


def compute_event_components(record):
    objs, missing = get_required_objects(record)
    if missing:
        return None, [f"missing objects: {missing}"]

    b = obj4(objs["b"])
    bbar = obj4(objs["bbar"])
    lp = obj4(objs["lplus"])
    nu = obj4(objs["nu_e"])
    lm = obj4(objs["lminus"])
    nubar = obj4(objs["anti_nu_mu"])

    top_lab = add4(b, lp, nu)
    antitop_lab = add4(bbar, lm, nubar)
    ttbar_lab = add4(top_lab, antitop_lab)

    beta_ttbar = beta_of(ttbar_lab)
    if beta_ttbar is None:
        return None, ["bad ttbar beta"]

    to_ttbar_rest = beta_ttbar

    top_ttbar = boost(top_lab, to_ttbar_rest)
    antitop_ttbar = boost(antitop_lab, to_ttbar_rest)

    # Nominal incoming e- beam four-vector. This is adequate for the first
    # truth-candidate table; later precision work should decide whether to use
    # nominal beam or post-ISR effective beam directions event-by-event.
    beam_e_minus_lab = (SQRTS_GEV / 2.0, 0.0, 0.0, SQRTS_GEV / 2.0)
    beam_ttbar = boost(beam_e_minus_lab, to_ttbar_rest)

    k_hat = unit3(spatial(top_ttbar))
    if k_hat is None:
        return None, ["bad k axis"]

    beam_hat = unit3(spatial(beam_ttbar))
    if beam_hat is None:
        return None, ["bad beam axis"]

    n_hat = unit3(cross3(beam_hat, k_hat))
    if n_hat is None:
        return None, ["beam parallel to top direction; undefined n axis"]

    r_hat = unit3(cross3(n_hat, k_hat))
    if r_hat is None:
        return None, ["bad r axis"]

    axes_ttbar = {
        "r": r_hat,
        "n": n_hat,
        "k": k_hat,
    }

    lp_dir_top = lepton_dir_in_parent_rest(lp, top_lab)
    lm_dir_antitop = lepton_dir_in_parent_rest(lm, antitop_lab)
    if lp_dir_top is None:
        return None, ["bad lplus direction in top rest"]
    if lm_dir_antitop is None:
        return None, ["bad lminus direction in antitop rest"]

    # Express spin axes in the corresponding parent rest frames.
    top_beta_ttbar = beta_of(top_ttbar)
    antitop_beta_ttbar = beta_of(antitop_ttbar)
    if top_beta_ttbar is None or antitop_beta_ttbar is None:
        return None, ["bad parent beta in ttbar rest"]

    axes_top = {}
    axes_antitop = {}
    for comp, axis in axes_ttbar.items():
        axis_top = boost_axis_to_rest(axis, top_ttbar)
        axis_antitop = boost_axis_to_rest(axis, antitop_ttbar)
        if axis_top is None or axis_antitop is None:
            return None, [f"bad boosted axis {comp}"]
        axes_top[comp] = axis_top
        axes_antitop[comp] = axis_antitop

    uplus = {comp: dot3(lp_dir_top, axes_top[comp]) for comp in COMPONENTS}
    uminus = {comp: dot3(lm_dir_antitop, axes_antitop[comp]) for comp in COMPONENTS}

    return {
        "uplus": uplus,
        "uminus": uminus,
        "m_top": mass4(top_lab),
        "m_antitop": mass4(antitop_lab),
        "m_ttbar": mass4(ttbar_lab),
    }, []


def load_truth(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield lineno, json.loads(line)
            except Exception as exc:
                raise SystemExit(f"ERROR: bad truth JSONL line {lineno}: {exc}") from exc


def summarize_sample(parent, rows):
    n = len(rows)

    means_plus = {c: sum(r["uplus"][c] for r in rows) / n for c in COMPONENTS}
    means_minus = {c: sum(r["uminus"][c] for r in rows) / n for c in COMPONENTS}

    corr = {}
    for i in COMPONENTS:
        for j in COMPONENTS:
            corr[f"{i}{j}"] = sum(r["uplus"][i] * r["uminus"][j] for r in rows) / n

    bplus = {c: 3.0 * means_plus[c] for c in COMPONENTS}
    bminus = {c: -3.0 * means_minus[c] for c in COMPONENTS}
    cmat = {ij: -9.0 * val for ij, val in corr.items()}

    masses = {
        "top_mean": sum(r["m_top"] for r in rows) / n,
        "antitop_mean": sum(r["m_antitop"] for r in rows) / n,
        "ttbar_mean": sum(r["m_ttbar"] for r in rows) / n,
    }

    return {
        "parent_label": parent,
        "n_events": n,
        "component_order": list(COMPONENTS),
        "basis": "rnk_common_v1_truth_candidate",
        "moment_convention": {
            "Bplus_i": "3 * <uplus_i>",
            "Bminus_j": "-3 * <uminus_j>",
            "C_ij": "-9 * <uplus_i * uminus_j>",
            "subsystem_order": ["top", "antitop"],
            "lepton_analyzer_signs": {
                "top_lplus": +1,
                "antitop_lminus": -1,
            },
        },
        "mean_uplus": means_plus,
        "mean_uminus": means_minus,
        "mean_uplus_uminus": corr,
        "Bplus": bplus,
        "Bminus": bminus,
        "C": cmat,
        "mass_sanity_GeV": masses,
    }


def write_csv(path: Path, summaries):
    fields = ["parent_label", "n_events"]

    for c in COMPONENTS:
        fields.append(f"Bplus_{c}")
    for c in COMPONENTS:
        fields.append(f"Bminus_{c}")
    for i in COMPONENTS:
        for j in COMPONENTS:
            fields.append(f"C_{i}{j}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for s in summaries:
            row = {
                "parent_label": s["parent_label"],
                "n_events": s["n_events"],
            }
            for c in COMPONENTS:
                row[f"Bplus_{c}"] = s["Bplus"][c]
            for c in COMPONENTS:
                row[f"Bminus_{c}"] = s["Bminus"][c]
            for i in COMPONENTS:
                for j in COMPONENTS:
                    row[f"C_{i}{j}"] = s["C"][f"{i}{j}"]
            writer.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth-jsonl", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--summary-json", required=True)
    args = ap.parse_args()

    by_parent = defaultdict(list)
    skipped_by_parent = defaultdict(int)
    failed_examples = []

    total_seen = 0
    total_used = 0

    for lineno, record in load_truth(Path(args.truth_jsonl)):
        total_seen += 1
        parent = record.get("parent_label")

        if parent not in DILEPTON_PARENTS:
            skipped_by_parent[parent] += 1
            continue

        if record.get("status") != "PASS":
            skipped_by_parent[parent] += 1
            continue

        comps, errors = compute_event_components(record)
        if errors:
            skipped_by_parent[parent] += 1
            if len(failed_examples) < 20:
                failed_examples.append(
                    {
                        "line": lineno,
                        "parent_label": parent,
                        "source_label": record.get("source_label"),
                        "event_index_in_parent": record.get("event_index_in_parent"),
                        "errors": errors,
                    }
                )
            continue

        by_parent[parent].append(comps)
        total_used += 1

    summaries = []
    for parent in sorted(by_parent):
        rows = by_parent[parent]
        if not rows:
            continue
        summaries.append(summarize_sample(parent, rows))

    output_json = Path(args.output_json)
    output_csv = Path(args.output_csv)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": 1,
        "status": "PASS" if not failed_examples else "PASS_WITH_SKIPS",
        "truth_jsonl": str(Path(args.truth_jsonl)),
        "total_truth_events_seen": total_seen,
        "total_dilepton_events_used": total_used,
        "skipped_by_parent_label": dict(sorted(skipped_by_parent.items())),
        "failed_examples": failed_examples,
        "samples": summaries,
    }

    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(output_csv, summaries)

    summary = {
        "schema_version": 1,
        "status": payload["status"],
        "truth_jsonl": payload["truth_jsonl"],
        "spin_moments_json": str(output_json),
        "spin_moments_csv": str(output_csv),
        "total_truth_events_seen": total_seen,
        "total_dilepton_events_used": total_used,
        "skipped_by_parent_label": dict(sorted(skipped_by_parent.items())),
        "sample_labels": [s["parent_label"] for s in summaries],
        "n_events_by_sample": {s["parent_label"]: s["n_events"] for s in summaries},
        "component_order": list(COMPONENTS),
        "basis": "rnk_common_v1_truth_candidate",
        "notes": [
            "First-pass truth-candidate spin moments from parton-only HepMC3-derived truth table.",
            "Uses nominal e- beam axis boosted to reconstructed ttbar rest frame.",
            "Precision interpretation should freeze ISR/effective-beam convention before publication use.",
        ],
    }

    Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"SPIN_MOMENT_STATUS={payload['status']}")
    print(f"TOTAL_TRUTH_EVENTS_SEEN={total_seen}")
    print(f"TOTAL_DILEPTON_EVENTS_USED={total_used}")
    print(f"WROTE_JSON={output_json}")
    print(f"WROTE_CSV={output_csv}")
    print(f"WROTE_SUMMARY={args.summary_json}")

    return 0 if payload["status"] in {"PASS", "PASS_WITH_SKIPS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
