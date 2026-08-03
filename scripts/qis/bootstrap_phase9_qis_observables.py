#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

COMPONENTS = ("r", "n", "k")
DEFAULT_SAMPLES = ("unpol_epmum", "LR100_epmum", "RL100_epmum")


def import_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCRIPT_DIR = Path(__file__).resolve().parent
COMPARE = import_module_from_path(
    "phase9_pair_compare",
    SCRIPT_DIR / "compare_phase9_dilepton_spin_moments.py",
)
QIS = import_module_from_path(
    "phase9_qis",
    SCRIPT_DIR / "build_phase9_density_matrix_qis_observables.py",
)


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


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


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")
    mu = sum(values) / len(values)
    return math.sqrt(sum((x - mu) ** 2 for x in values) / (len(values) - 1))


def summarize_metric(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(sum(values) / len(values)) if values else float("nan"),
        "se": float(stdev(values)),
        "p02p5": float(percentile(values, 0.025)),
        "p16": float(percentile(values, 0.16)),
        "p50": float(percentile(values, 0.50)),
        "p84": float(percentile(values, 0.84)),
        "p97p5": float(percentile(values, 0.975)),
        "min": float(min(values)) if values else float("nan"),
        "max": float(max(values)) if values else float("nan"),
    }


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


KEYS = moment_keys()


def vector_to_blocks(vec: np.ndarray) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    m = {k: float(v) for k, v in zip(KEYS, vec)}

    Bplus = {c: m[f"Bplus_{c}"] for c in COMPONENTS}
    Bminus = {c: m[f"Bminus_{c}"] for c in COMPONENTS}
    C = {f"{i}{j}": m[f"C_{i}{j}"] for i in COMPONENTS for j in COMPONENTS}

    return Bplus, Bminus, C


def qis_metrics_from_moment_vector(vec: np.ndarray) -> dict[str, float | bool]:
    Bplus, Bminus, C = vector_to_blocks(vec)

    rho = QIS.build_rho(Bplus, Bminus, C)

    eigvals = sorted(float(x.real) for x in np.linalg.eigvalsh(rho))
    min_eig = min(eigvals)

    trace = np.trace(rho)
    herm = np.max(np.abs(rho - rho.conjugate().T))

    purity = float(np.real(np.trace(rho @ rho)))
    rho_pt = QIS.partial_transpose_second_qubit(rho)
    pt_eigvals = sorted(float(x.real) for x in np.linalg.eigvalsh(rho_pt))

    negativity = float(sum(abs(x) for x in pt_eigvals if x < 0.0))
    concurrence = float(QIS.concurrence_candidate(rho))
    chsh, _ = QIS.horodecki_chsh_max(C)

    return {
        "rho_trace_real": float(trace.real),
        "rho_trace_imag": float(trace.imag),
        "rho_hermiticity_max_abs_residual": float(herm),
        "rho_min_eigenvalue": float(min_eig),
        "purity_tr_rho2": float(purity),
        "linear_entropy_1_minus_purity": float(1.0 - purity),
        "partial_transpose_min_eigenvalue": float(min(pt_eigvals)),
        "negativity_candidate": negativity,
        "concurrence_candidate": concurrence,
        "bell_chsh_horodecki_max": float(chsh),
        "bell_chsh_violation_candidate": bool(chsh > 2.0),
        "rho_positive_semidefinite_candidate": bool(min_eig >= -1.0e-8),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth-jsonl", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--summary-json", required=True)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=36520260803)
    ap.add_argument("--samples", nargs="*", default=list(DEFAULT_SAMPLES))
    args = ap.parse_args()

    truth_path = Path(args.truth_jsonl)
    samples = tuple(args.samples)

    vectors_by_sample: dict[str, list[list[float]]] = {s: [] for s in samples}
    seen_by_parent = defaultdict(int)
    skipped_by_parent = defaultdict(int)

    for record in load_jsonl(truth_path):
        parent = record.get("parent_label", "")
        seen_by_parent[parent] += 1

        if parent not in vectors_by_sample:
            continue

        contrib = COMPARE.spin_contributions_from_truth_record(record)
        if contrib is None:
            skipped_by_parent[parent] += 1
            continue

        vectors_by_sample[parent].append([float(contrib[k]) for k in KEYS])

    rng = np.random.default_rng(args.seed)

    result_samples = []
    csv_rows = []

    metrics_to_summarize = [
        "rho_min_eigenvalue",
        "purity_tr_rho2",
        "linear_entropy_1_minus_purity",
        "partial_transpose_min_eigenvalue",
        "negativity_candidate",
        "concurrence_candidate",
        "bell_chsh_horodecki_max",
    ]

    status = "PASS"

    for parent in samples:
        arr = np.array(vectors_by_sample[parent], dtype=float)

        if arr.size == 0:
            status = "FAIL"
            result_samples.append({
                "parent_label": parent,
                "status": "FAIL",
                "reason": "no usable events",
                "n_events": 0,
            })
            continue

        n = arr.shape[0]
        central_vec = arr.mean(axis=0)
        central_metrics = qis_metrics_from_moment_vector(central_vec)

        boot_metrics: dict[str, list[float]] = {m: [] for m in metrics_to_summarize}
        boot_physical = []
        boot_chsh_violation = []

        for _ in range(args.bootstrap):
            idx = rng.integers(0, n, size=n)
            vec = arr[idx].mean(axis=0)
            m = qis_metrics_from_moment_vector(vec)

            for key in metrics_to_summarize:
                boot_metrics[key].append(float(m[key]))

            boot_physical.append(bool(m["rho_positive_semidefinite_candidate"]))
            boot_chsh_violation.append(bool(m["bell_chsh_violation_candidate"]))

        metric_summaries = {
            key: summarize_metric(vals)
            for key, vals in boot_metrics.items()
        }

        physical_fraction = sum(boot_physical) / len(boot_physical)
        chsh_violation_fraction = sum(boot_chsh_violation) / len(boot_chsh_violation)

        sample_payload = {
            "parent_label": parent,
            "status": "PASS",
            "n_events": n,
            "central_metrics": central_metrics,
            "bootstrap": {
                "n_bootstrap": args.bootstrap,
                "seed": args.seed,
                "metrics": metric_summaries,
                "rho_positive_semidefinite_fraction": physical_fraction,
                "bell_chsh_violation_fraction": chsh_violation_fraction,
            },
        }

        result_samples.append(sample_payload)

        for metric, summary in metric_summaries.items():
            csv_rows.append({
                "parent_label": parent,
                "n_events": n,
                "metric": metric,
                "central": central_metrics[metric],
                "bootstrap_mean": summary["mean"],
                "bootstrap_se": summary["se"],
                "bootstrap_p02p5": summary["p02p5"],
                "bootstrap_p16": summary["p16"],
                "bootstrap_p50": summary["p50"],
                "bootstrap_p84": summary["p84"],
                "bootstrap_p97p5": summary["p97p5"],
                "bootstrap_min": summary["min"],
                "bootstrap_max": summary["max"],
                "rho_positive_semidefinite_fraction": physical_fraction,
                "bell_chsh_violation_fraction": chsh_violation_fraction,
            })

    payload = {
        "schema_version": 1,
        "status": status,
        "truth_jsonl": str(truth_path),
        "basis": "rnk_common_v1_nominal_beam_phase9",
        "component_order": list(COMPONENTS),
        "samples_requested": list(samples),
        "truth_events_seen_by_parent_label": dict(sorted(seen_by_parent.items())),
        "skipped_events_by_parent_label": dict(sorted(skipped_by_parent.items())),
        "bootstrap": {
            "n_bootstrap": args.bootstrap,
            "seed": args.seed,
            "method": "event-level resampling within each parent_label, recomputing Bplus/Bminus/C and QIS metrics",
        },
        "samples": result_samples,
        "notes": [
            "Bootstrap propagates event-level spin-moment fluctuations into raw density-matrix/QIS candidate observables.",
            "QIS quantities remain diagnostic candidates for the Phase 9 parton-only truth-candidate product.",
            "rho_positive_semidefinite_fraction estimates how often finite-statistics resamples yield a positive semidefinite raw rho.",
        ],
    }

    out_json = Path(args.output_json)
    out_csv = Path(args.output_csv)
    out_summary = Path(args.summary_json)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fields = [
        "parent_label",
        "n_events",
        "metric",
        "central",
        "bootstrap_mean",
        "bootstrap_se",
        "bootstrap_p02p5",
        "bootstrap_p16",
        "bootstrap_p50",
        "bootstrap_p84",
        "bootstrap_p97p5",
        "bootstrap_min",
        "bootstrap_max",
        "rho_positive_semidefinite_fraction",
        "bell_chsh_violation_fraction",
    ]

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)

    summary = {
        "schema_version": 1,
        "status": status,
        "truth_jsonl": str(truth_path),
        "bootstrap_json": str(out_json),
        "bootstrap_csv": str(out_csv),
        "basis": payload["basis"],
        "component_order": payload["component_order"],
        "bootstrap": payload["bootstrap"],
        "samples": [
            {
                "parent_label": s["parent_label"],
                "status": s["status"],
                "n_events": s.get("n_events", 0),
                "central_rho_min_eigenvalue": s.get("central_metrics", {}).get("rho_min_eigenvalue"),
                "rho_min_eigenvalue_p16": s.get("bootstrap", {}).get("metrics", {}).get("rho_min_eigenvalue", {}).get("p16"),
                "rho_min_eigenvalue_p50": s.get("bootstrap", {}).get("metrics", {}).get("rho_min_eigenvalue", {}).get("p50"),
                "rho_min_eigenvalue_p84": s.get("bootstrap", {}).get("metrics", {}).get("rho_min_eigenvalue", {}).get("p84"),
                "rho_positive_semidefinite_fraction": s.get("bootstrap", {}).get("rho_positive_semidefinite_fraction"),
                "central_purity": s.get("central_metrics", {}).get("purity_tr_rho2"),
                "purity_se": s.get("bootstrap", {}).get("metrics", {}).get("purity_tr_rho2", {}).get("se"),
                "central_chsh": s.get("central_metrics", {}).get("bell_chsh_horodecki_max"),
                "chsh_se": s.get("bootstrap", {}).get("metrics", {}).get("bell_chsh_horodecki_max", {}).get("se"),
                "bell_chsh_violation_fraction": s.get("bootstrap", {}).get("bell_chsh_violation_fraction"),
                "central_concurrence": s.get("central_metrics", {}).get("concurrence_candidate"),
                "central_negativity": s.get("central_metrics", {}).get("negativity_candidate"),
            }
            for s in result_samples
        ],
        "notes": payload["notes"],
    }

    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"PHASE9_QIS_BOOTSTRAP_STATUS={status}")
    print(f"N_BOOTSTRAP={args.bootstrap}")
    for s in summary["samples"]:
        print(
            f"{s['parent_label']:20s} "
            f"minEig={s['central_rho_min_eigenvalue']:+.6f} "
            f"p16={s['rho_min_eigenvalue_p16']:+.6f} "
            f"p50={s['rho_min_eigenvalue_p50']:+.6f} "
            f"p84={s['rho_min_eigenvalue_p84']:+.6f} "
            f"psdFrac={s['rho_positive_semidefinite_fraction']:.3f} "
            f"CHSH={s['central_chsh']:.6f}±{s['chsh_se']:.6f}"
        )

    print(f"WROTE_JSON={out_json}")
    print(f"WROTE_CSV={out_csv}")
    print(f"WROTE_SUMMARY={out_summary}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
