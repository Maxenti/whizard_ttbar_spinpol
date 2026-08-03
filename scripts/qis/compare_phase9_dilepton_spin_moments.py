#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

COMPONENTS = ("r", "n", "k")
SQRTS_GEV = 365.0


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def dot3(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross3(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def norm3(a) -> float:
    return math.sqrt(dot3(a, a))


def unit3(a):
    n = norm3(a)
    if n <= 0.0:
        return None
    return (a[0] / n, a[1] / n, a[2] / n)


def add4(*vs):
    return (
        sum(v[0] for v in vs),
        sum(v[1] for v in vs),
        sum(v[2] for v in vs),
        sum(v[3] for v in vs),
    )


def spatial(v):
    return (v[1], v[2], v[3])


def beta_of(v):
    e, px, py, pz = v
    if e == 0.0:
        return None
    return (px / e, py / e, pz / e)


def boost(v, beta):
    # Convention:
    #   E' = gamma (E - beta . p)
    # Therefore beta = P_vec/P_E boosts into the rest frame of P.
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

    return (
        gamma * (e - bp),
        px + gamma2 * bp * bx - gamma * bx * e,
        py + gamma2 * bp * by - gamma * by * e,
        pz + gamma2 * bp * bz - gamma * bz * e,
    )


def p4_from_obj(obj: dict[str, Any]):
    return (
        float(obj["e"]),
        float(obj["px"]),
        float(obj["py"]),
        float(obj["pz"]),
    )


def get_obj(objects: dict[str, Any], names: list[str]) -> dict[str, Any] | None:
    for name in names:
        obj = objects.get(name)
        if isinstance(obj, dict):
            return obj
    return None


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


def spin_contributions_from_truth_record(record: dict[str, Any]) -> dict[str, float] | None:
    if record.get("status") != "PASS":
        return None

    parent = record.get("parent_label", "")
    if parent not in {"unpol_epmum", "LR100_epmum", "RL100_epmum"}:
        return None

    objects = record.get("objects", {})
    if not isinstance(objects, dict):
        return None

    b = get_obj(objects, ["b"])
    bbar = get_obj(objects, ["bbar"])
    lplus = get_obj(objects, ["lplus", "eplus", "positron"])
    nue = get_obj(objects, ["nu_e", "nue"])
    lminus = get_obj(objects, ["lminus", "muminus", "mu_minus"])
    anumu = get_obj(objects, ["anti_nu_mu", "anti_numu", "numubar", "nubar_mu"])

    if any(x is None for x in [b, bbar, lplus, nue, lminus, anumu]):
        return None

    b4 = p4_from_obj(b)
    bbar4 = p4_from_obj(bbar)
    lp4 = p4_from_obj(lplus)
    nue4 = p4_from_obj(nue)
    lm4 = p4_from_obj(lminus)
    anumu4 = p4_from_obj(anumu)

    top_lab = add4(b4, lp4, nue4)
    antitop_lab = add4(bbar4, lm4, anumu4)
    ttbar_lab = add4(top_lab, antitop_lab)

    beta_ttbar = beta_of(ttbar_lab)
    if beta_ttbar is None:
        return None

    top_ttbar = boost(top_lab, beta_ttbar)
    antitop_ttbar = boost(antitop_lab, beta_ttbar)

    # Phase 9 axis convention is frozen to the nominal e- beam; the
    # status-21 effective-beam diagnostic agreed to roundoff for this product.
    beam_lab = (SQRTS_GEV / 2.0, 0.0, 0.0, SQRTS_GEV / 2.0)
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

    lp_dir = lepton_dir_parent_rest(lp4, top_lab)
    lm_dir = lepton_dir_parent_rest(lm4, antitop_lab)
    if lp_dir is None or lm_dir is None:
        return None

    axes_top = {}
    axes_antitop = {}
    for comp, axis in axes_ttbar.items():
        axes_top[comp] = boosted_axis(axis, top_ttbar)
        axes_antitop[comp] = boosted_axis(axis, antitop_ttbar)

        if axes_top[comp] is None or axes_antitop[comp] is None:
            return None

    uplus = {c: dot3(lp_dir, axes_top[c]) for c in COMPONENTS}
    uminus = {c: dot3(lm_dir, axes_antitop[c]) for c in COMPONENTS}

    out: dict[str, float] = {}

    for c in COMPONENTS:
        out[f"Bplus_{c}"] = 3.0 * uplus[c]
        out[f"Bminus_{c}"] = -3.0 * uminus[c]

    for i in COMPONENTS:
        for j in COMPONENTS:
            out[f"C_{i}{j}"] = -9.0 * uplus[i] * uminus[j]

    return out


def moment_keys() -> list[str]:
    keys = []
    for c in COMPONENTS:
        keys.append(f"Bplus_{c}")
    for c in COMPONENTS:
        keys.append(f"Bminus_{c}")
    for i in COMPONENTS:
        for j in COMPONENTS:
            keys.append(f"C_{i}{j}")
    return keys


def key_family_component(key: str):
    if key.startswith("Bplus_"):
        return "Bplus", key.split("_", 1)[1]
    if key.startswith("Bminus_"):
        return "Bminus", key.split("_", 1)[1]
    if key.startswith("C_"):
        return "C", key.split("_", 1)[1]
    return "unknown", ""


def mean_value(rows: list[dict[str, float]], key: str) -> float:
    return sum(r[key] for r in rows) / len(rows)


def bootstrap_indices(rng: random.Random, n: int) -> list[int]:
    return [rng.randrange(n) for _ in range(n)]


def mean_from_indices(rows: list[dict[str, float]], key: str, indices: list[int]) -> float:
    return sum(rows[i][key] for i in indices) / len(indices)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")

    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]

    pos = p * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))

    if lo == hi:
        return xs[lo]

    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def sample_stdev(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")

    mu = sum(values) / len(values)
    var = sum((x - mu) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(var)


def classify(delta: float, se: float) -> tuple[str, float]:
    if not math.isfinite(se) or se <= 0.0:
        return "unknown", float("nan")

    z = delta / se
    az = abs(z)

    if az >= 5.0:
        return "large_resolved_shift", z
    if az >= 3.0:
        return "moderate_resolved_shift", z
    if az >= 2.5:
        return "small_but_resolved_shift", z
    return "not_resolved", z


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth-jsonl", required=True)
    ap.add_argument("--reference", default="unpol_epmum")
    ap.add_argument("--comparison", default="LR100_epmum")
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--summary-json", required=True)
    ap.add_argument("--bootstrap", type=int, default=500)
    ap.add_argument("--seed", type=int, default=36520260803)
    args = ap.parse_args()

    truth_path = Path(args.truth_jsonl)
    keys = moment_keys()

    rows_by_parent: dict[str, list[dict[str, float]]] = {
        args.reference: [],
        args.comparison: [],
    }

    total_truth_events_seen = 0
    total_dilepton_events_seen = 0
    skipped = Counter()

    for record in load_jsonl(truth_path):
        total_truth_events_seen += 1
        parent = record.get("parent_label", "")

        if parent not in rows_by_parent:
            continue

        total_dilepton_events_seen += 1
        contrib = spin_contributions_from_truth_record(record)

        if contrib is None:
            skipped[parent] += 1
            continue

        rows_by_parent[parent].append(contrib)

    n_ref = len(rows_by_parent[args.reference])
    n_cmp = len(rows_by_parent[args.comparison])

    if n_ref == 0 or n_cmp == 0:
        summary = {
            "schema_version": 2,
            "status": "FAIL",
            "reason": "missing usable events for reference or comparison",
            "truth_jsonl": str(truth_path),
            "reference": args.reference,
            "comparison": args.comparison,
            "usable_events_by_sample": {
                args.reference: n_ref,
                args.comparison: n_cmp,
            },
            "skipped_events_by_sample": dict(skipped),
        }
        Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print("SPIN_COMPARISON_STATUS=FAIL")
        return 1

    ref_rows = rows_by_parent[args.reference]
    cmp_rows = rows_by_parent[args.comparison]

    rng = random.Random(args.seed)
    boot_deltas_by_key = {key: [] for key in keys}

    for _ in range(args.bootstrap):
        ref_idx = bootstrap_indices(rng, n_ref)
        cmp_idx = bootstrap_indices(rng, n_cmp)

        for key in keys:
            d = mean_from_indices(cmp_rows, key, cmp_idx) - mean_from_indices(ref_rows, key, ref_idx)
            boot_deltas_by_key[key].append(d)

    comparisons = []

    for key in keys:
        ref_mean = mean_value(ref_rows, key)
        cmp_mean = mean_value(cmp_rows, key)
        delta = cmp_mean - ref_mean

        boot = boot_deltas_by_key[key]
        se = sample_stdev(boot)
        classification, z = classify(delta, se)
        family, component = key_family_component(key)

        comparisons.append({
            "key": key,
            "family": family,
            "component": component,
            args.reference: ref_mean,
            args.comparison: cmp_mean,
            f"delta_{args.comparison}_minus_{args.reference}": delta,
            "delta_bootstrap_se": se,
            "delta_z": z,
            "delta_bootstrap_p16": percentile(boot, 0.16),
            "delta_bootstrap_p50": percentile(boot, 0.50),
            "delta_bootstrap_p84": percentile(boot, 0.84),
            "classification": classification,
        })

    comparisons.sort(
        key=lambda r: (
            0.0 if not math.isfinite(float(r["delta_z"])) else abs(float(r["delta_z"])),
            abs(float(r[f"delta_{args.comparison}_minus_{args.reference}"])),
        ),
        reverse=True,
    )

    class_counts = Counter(r["classification"] for r in comparisons)

    payload = {
        "schema_version": 2,
        "status": "PASS",
        "basis": "rnk_common_v1_nominal_beam_phase9",
        "component_order": list(COMPONENTS),
        "truth_jsonl": str(truth_path),
        "sample_pair": {
            "reference": args.reference,
            "comparison": args.comparison,
            "delta_definition": f"{args.comparison} - {args.reference}",
        },
        "bootstrap": {
            "n_bootstrap": args.bootstrap,
            "seed": args.seed,
        },
        "total_truth_events_seen": total_truth_events_seen,
        "total_dilepton_events_seen_for_pair": total_dilepton_events_seen,
        "usable_events_by_sample": {
            args.reference: n_ref,
            args.comparison: n_cmp,
        },
        "skipped_events_by_sample": dict(skipped),
        "classification_counts": dict(sorted(class_counts.items())),
        "comparisons": comparisons,
        "notes": [
            "Pair-configurable Phase 9 spin-moment comparison.",
            "Moment contributions are computed from truth JSONL objects using the frozen nominal-beam r,n,k convention.",
            "This remains a parton-only truth-candidate comparison.",
        ],
    }

    out_json = Path(args.output_json)
    out_csv = Path(args.output_csv)
    out_summary = Path(args.summary_json)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "key",
            "family",
            "component",
            args.reference,
            args.comparison,
            f"delta_{args.comparison}_minus_{args.reference}",
            "delta_bootstrap_se",
            "delta_z",
            "delta_bootstrap_p16",
            "delta_bootstrap_p50",
            "delta_bootstrap_p84",
            "classification",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in comparisons:
            writer.writerow({k: row[k] for k in fields})

    summary = {
        "schema_version": payload["schema_version"],
        "status": payload["status"],
        "basis": payload["basis"],
        "component_order": payload["component_order"],
        "truth_jsonl": payload["truth_jsonl"],
        "comparison_json": str(out_json),
        "comparison_csv": str(out_csv),
        "sample_pair": payload["sample_pair"],
        "bootstrap": payload["bootstrap"],
        "total_truth_events_seen": payload["total_truth_events_seen"],
        "total_dilepton_events_seen_for_pair": payload["total_dilepton_events_seen_for_pair"],
        "usable_events_by_sample": payload["usable_events_by_sample"],
        "skipped_events_by_sample": payload["skipped_events_by_sample"],
        "classification_counts": payload["classification_counts"],
        "top_resolved_shifts": comparisons[:10],
        "notes": payload["notes"],
    }

    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("SPIN_COMPARISON_STATUS=PASS")
    print(f"REFERENCE={args.reference}")
    print(f"COMPARISON={args.comparison}")
    print(f"TOTAL_TRUTH_EVENTS_SEEN={total_truth_events_seen}")
    print(f"TOTAL_DILEPTON_EVENTS_SEEN_FOR_PAIR={total_dilepton_events_seen}")
    print(f"USABLE_REFERENCE={n_ref}")
    print(f"USABLE_COMPARISON={n_cmp}")
    print(f"N_BOOTSTRAP={args.bootstrap}")
    print(f"WROTE_JSON={out_json}")
    print(f"WROTE_CSV={out_csv}")
    print(f"WROTE_SUMMARY={out_summary}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
