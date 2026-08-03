#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
from pathlib import Path
from typing import Any


def load_spin_module():
    path = Path(__file__).with_name("build_phase9_dilepton_spin_moments.py")
    spec = importlib.util.spec_from_file_location("phase9_spin_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import spin builder from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return float("nan")
    xs = sorted(vals)
    if len(xs) == 1:
        return xs[0]
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def sample_std(vals: list[float]) -> float:
    if len(vals) < 2:
        return float("nan")
    mean = sum(vals) / len(vals)
    var = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
    return math.sqrt(max(var, 0.0))


def event_moment_contributions(comps: dict[str, Any], components: tuple[str, ...]) -> dict[str, float]:
    out: dict[str, float] = {}

    uplus = comps["uplus"]
    uminus = comps["uminus"]

    for c in components:
        out[f"Bplus_{c}"] = 3.0 * float(uplus[c])
        out[f"Bminus_{c}"] = -3.0 * float(uminus[c])

    for i in components:
        for j in components:
            out[f"C_{i}{j}"] = -9.0 * float(uplus[i]) * float(uminus[j])

    return out


def mean_contributions(rows: list[dict[str, float]], keys: list[str]) -> dict[str, float]:
    n = len(rows)
    if n <= 0:
        raise ValueError("cannot average empty row list")
    return {k: sum(r[k] for r in rows) / n for k in keys}


def bootstrap_means(
    rows: list[dict[str, float]],
    keys: list[str],
    n_bootstrap: int,
    rng: random.Random,
) -> dict[str, list[float]]:
    n = len(rows)
    boot: dict[str, list[float]] = {k: [] for k in keys}

    for _ in range(n_bootstrap):
        sums = {k: 0.0 for k in keys}
        for _i in range(n):
            r = rows[rng.randrange(n)]
            for k in keys:
                sums[k] += r[k]
        for k in keys:
            boot[k].append(sums[k] / n)

    return boot


def classify(delta: float, se_delta: float) -> str:
    if not math.isfinite(se_delta) or se_delta <= 0:
        return "uncertain_no_error_estimate"

    z = abs(delta / se_delta)

    if abs(delta) >= 0.10 and z >= 5.0:
        return "large_resolved_shift"
    if abs(delta) >= 0.03 and z >= 3.0:
        return "moderate_resolved_shift"
    if z >= 3.0:
        return "small_but_resolved_shift"
    return "not_resolved"


def component_family(key: str) -> tuple[str, str]:
    if key.startswith("Bplus_"):
        return "Bplus", key.replace("Bplus_", "")
    if key.startswith("Bminus_"):
        return "Bminus", key.replace("Bminus_", "")
    if key.startswith("C_"):
        return "C", key.replace("C_", "")
    return "unknown", key


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth-jsonl", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--summary-json", required=True)
    ap.add_argument("--bootstrap", type=int, default=500)
    ap.add_argument("--seed", type=int, default=36520260803)
    args = ap.parse_args()

    spin = load_spin_module()
    components = tuple(spin.COMPONENTS)

    keys = []
    for c in components:
        keys.append(f"Bplus_{c}")
    for c in components:
        keys.append(f"Bminus_{c}")
    for i in components:
        for j in components:
            keys.append(f"C_{i}{j}")

    wanted = {"unpol_epmum", "LR100_epmum"}
    rows_by_parent: dict[str, list[dict[str, float]]] = {p: [] for p in wanted}

    total_seen = 0
    total_dilepton_seen = 0
    failed_examples = []

    for lineno, record in spin.load_truth(Path(args.truth_jsonl)):
        total_seen += 1
        parent = record.get("parent_label")
        if parent not in wanted:
            continue

        total_dilepton_seen += 1
        comps, errors = spin.compute_event_components(record)
        if errors:
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

        rows_by_parent[parent].append(event_moment_contributions(comps, components))

    for parent in wanted:
        if len(rows_by_parent[parent]) != 10000:
            raise SystemExit(f"ERROR: expected 10000 usable events for {parent}, got {len(rows_by_parent[parent])}")

    means = {parent: mean_contributions(rows, keys) for parent, rows in rows_by_parent.items()}

    rng = random.Random(args.seed)
    boot = {
        parent: bootstrap_means(rows, keys, args.bootstrap, rng)
        for parent, rows in rows_by_parent.items()
    }

    comparisons = []

    for key in keys:
        unpol = means["unpol_epmum"][key]
        lr100 = means["LR100_epmum"][key]
        delta = lr100 - unpol

        unpol_boot = boot["unpol_epmum"][key]
        lr100_boot = boot["LR100_epmum"][key]
        unpol_se = sample_std(unpol_boot)
        lr100_se = sample_std(lr100_boot)
        se_delta = math.sqrt(unpol_se * unpol_se + lr100_se * lr100_se)

        z = delta / se_delta if se_delta > 0 else float("nan")
        fam, comp = component_family(key)

        delta_boot = [a - b for a, b in zip(lr100_boot, unpol_boot)]

        comparisons.append(
            {
                "key": key,
                "family": fam,
                "component": comp,
                "unpol_epmum": unpol,
                "LR100_epmum": lr100,
                "delta_LR100_minus_unpol": delta,
                "unpol_bootstrap_se": unpol_se,
                "LR100_bootstrap_se": lr100_se,
                "delta_bootstrap_se": se_delta,
                "delta_z": z,
                "delta_bootstrap_p16": percentile(delta_boot, 0.16),
                "delta_bootstrap_p50": percentile(delta_boot, 0.50),
                "delta_bootstrap_p84": percentile(delta_boot, 0.84),
                "classification": classify(delta, se_delta),
            }
        )

    comparisons.sort(key=lambda r: abs(r["delta_z"]), reverse=True)

    output_json = Path(args.output_json)
    output_csv = Path(args.output_csv)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": 1,
        "status": "PASS" if not failed_examples else "PASS_WITH_SKIPS",
        "truth_jsonl": str(Path(args.truth_jsonl)),
        "bootstrap": {
            "n_bootstrap": args.bootstrap,
            "seed": args.seed,
        },
        "basis": "rnk_common_v1_truth_candidate",
        "component_order": list(components),
        "sample_pair": {
            "reference": "unpol_epmum",
            "comparison": "LR100_epmum",
            "delta_definition": "LR100_epmum - unpol_epmum",
        },
        "total_truth_events_seen": total_seen,
        "total_dilepton_events_seen": total_dilepton_seen,
        "usable_events_by_sample": {k: len(v) for k, v in rows_by_parent.items()},
        "failed_examples": failed_examples,
        "comparisons": comparisons,
        "notes": [
            "Bootstrap uncertainties are computed from per-event truth-candidate moment contributions.",
            "This is still a truth-candidate product because the ISR/effective-beam axis convention is not yet frozen for precision interpretation.",
            "Large resolved shifts show which components respond to LR100 beam polarization in the current convention.",
        ],
    }

    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fields = [
        "key",
        "family",
        "component",
        "unpol_epmum",
        "LR100_epmum",
        "delta_LR100_minus_unpol",
        "delta_bootstrap_se",
        "delta_z",
        "delta_bootstrap_p16",
        "delta_bootstrap_p50",
        "delta_bootstrap_p84",
        "classification",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for r in comparisons:
            writer.writerow({k: r[k] for k in fields})

    summary = {
        "schema_version": 1,
        "status": payload["status"],
        "truth_jsonl": payload["truth_jsonl"],
        "comparison_json": str(output_json),
        "comparison_csv": str(output_csv),
        "bootstrap": payload["bootstrap"],
        "basis": payload["basis"],
        "component_order": payload["component_order"],
        "sample_pair": payload["sample_pair"],
        "usable_events_by_sample": payload["usable_events_by_sample"],
        "top_resolved_shifts": comparisons[:10],
        "n_large_resolved_shift": sum(1 for r in comparisons if r["classification"] == "large_resolved_shift"),
        "n_moderate_resolved_shift": sum(1 for r in comparisons if r["classification"] == "moderate_resolved_shift"),
        "n_small_but_resolved_shift": sum(1 for r in comparisons if r["classification"] == "small_but_resolved_shift"),
        "n_not_resolved": sum(1 for r in comparisons if r["classification"] == "not_resolved"),
        "notes": payload["notes"],
    }

    Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"SPIN_COMPARISON_STATUS={payload['status']}")
    print(f"TOTAL_TRUTH_EVENTS_SEEN={total_seen}")
    print(f"TOTAL_DILEPTON_EVENTS_SEEN={total_dilepton_seen}")
    print(f"USABLE_UNPOL={len(rows_by_parent['unpol_epmum'])}")
    print(f"USABLE_LR100={len(rows_by_parent['LR100_epmum'])}")
    print(f"N_BOOTSTRAP={args.bootstrap}")
    print(f"WROTE_JSON={output_json}")
    print(f"WROTE_CSV={output_csv}")
    print(f"WROTE_SUMMARY={args.summary_json}")

    return 0 if payload["status"] in {"PASS", "PASS_WITH_SKIPS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
