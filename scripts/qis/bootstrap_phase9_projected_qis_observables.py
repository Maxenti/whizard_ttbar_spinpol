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
        raise RuntimeError(f"could not import module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCRIPT_DIR = Path(__file__).resolve().parent

COMPARE = import_module_from_path(
    "phase9_pair_compare_projected_bootstrap",
    SCRIPT_DIR / "compare_phase9_dilepton_spin_moments.py",
)

RAW_QIS = import_module_from_path(
    "phase9_raw_qis_projected_bootstrap",
    SCRIPT_DIR / "build_phase9_density_matrix_qis_observables.py",
)

PROJECTION = import_module_from_path(
    "phase9_projection_projected_bootstrap",
    SCRIPT_DIR / "project_phase9_density_matrices.py",
)


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def percentile(values: list[float], probability: float) -> float:
    if not values:
        return float("nan")

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = probability * (len(ordered) - 1)
    low = int(math.floor(position))
    high = int(math.ceil(position))

    if low == high:
        return ordered[low]

    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def sample_stdev(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")

    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)

    return math.sqrt(variance)


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(sum(values) / len(values)),
        "se": float(sample_stdev(values)),
        "p02p5": float(percentile(values, 0.025)),
        "p16": float(percentile(values, 0.16)),
        "p50": float(percentile(values, 0.50)),
        "p84": float(percentile(values, 0.84)),
        "p97p5": float(percentile(values, 0.975)),
        "min": float(min(values)),
        "max": float(max(values)),
    }


def moment_keys() -> list[str]:
    keys: list[str] = []

    for component in COMPONENTS:
        keys.append(f"Bplus_{component}")

    for component in COMPONENTS:
        keys.append(f"Bminus_{component}")

    for first in COMPONENTS:
        for second in COMPONENTS:
            keys.append(f"C_{first}{second}")

    return keys


MOMENT_KEYS = moment_keys()


def moment_vector_to_blocks(
    vector: np.ndarray,
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    moments = {
        key: float(value)
        for key, value in zip(MOMENT_KEYS, vector)
    }

    bplus = {
        component: moments[f"Bplus_{component}"]
        for component in COMPONENTS
    }

    bminus = {
        component: moments[f"Bminus_{component}"]
        for component in COMPONENTS
    }

    correlations = {
        f"{first}{second}": moments[f"C_{first}{second}"]
        for first in COMPONENTS
        for second in COMPONENTS
    }

    return bplus, bminus, correlations


def raw_and_projected_metrics(moment_vector: np.ndarray) -> dict[str, Any]:
    bplus, bminus, correlations = moment_vector_to_blocks(moment_vector)

    raw_rho = RAW_QIS.build_rho(
        bplus,
        bminus,
        correlations,
    )

    raw_eigenvalues = np.linalg.eigvalsh(raw_rho)
    raw_minimum_eigenvalue = float(np.min(raw_eigenvalues).real)
    raw_purity = float(np.trace(raw_rho @ raw_rho).real)

    raw_partial_transpose = RAW_QIS.partial_transpose_second_qubit(raw_rho)
    raw_partial_transpose_eigenvalues = np.linalg.eigvalsh(
        raw_partial_transpose
    )
    raw_partial_transpose_minimum = float(
        np.min(raw_partial_transpose_eigenvalues).real
    )

    raw_negativity = float(
        sum(
            abs(float(value.real))
            for value in raw_partial_transpose_eigenvalues
            if float(value.real) < 0.0
        )
    )

    raw_concurrence = float(
        RAW_QIS.concurrence_candidate(raw_rho)
    )

    raw_chsh, _ = RAW_QIS.horodecki_chsh_max(correlations)

    projected_rho, projection = PROJECTION.project_density_matrix(raw_rho)
    projected = PROJECTION.projected_qis_metrics(projected_rho)

    projection_required = bool(
        projection["frobenius_distance"] > 1.0e-10
    )

    return {
        "raw_rho_min_eigenvalue": raw_minimum_eigenvalue,
        "raw_purity": raw_purity,
        "raw_partial_transpose_min_eigenvalue": (
            raw_partial_transpose_minimum
        ),
        "raw_negativity": raw_negativity,
        "raw_concurrence": raw_concurrence,
        "raw_chsh": float(raw_chsh),
        "raw_is_psd": bool(raw_minimum_eigenvalue >= -1.0e-8),
        "projection_required": projection_required,
        "projection_frobenius_distance": float(
            projection["frobenius_distance"]
        ),
        "projected_rho_min_eigenvalue": float(
            projected["rho_min_eigenvalue"]
        ),
        "projected_purity": float(
            projected["purity_tr_rho2"]
        ),
        "projected_partial_transpose_min_eigenvalue": float(
            projected["partial_transpose_min_eigenvalue"]
        ),
        "projected_negativity": float(
            projected["negativity_candidate"]
        ),
        "projected_concurrence": float(
            projected["concurrence_candidate"]
        ),
        "projected_is_psd": bool(
            projected["rho_min_eigenvalue"] >= -1.0e-10
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--truth-jsonl", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--bootstrap", type=int, default=500)
    parser.add_argument("--seed", type=int, default=36520260803)
    parser.add_argument(
        "--samples",
        nargs="*",
        default=list(DEFAULT_SAMPLES),
    )

    args = parser.parse_args()

    truth_path = Path(args.truth_jsonl)
    requested_samples = tuple(args.samples)

    vectors_by_sample: dict[str, list[list[float]]] = {
        sample: []
        for sample in requested_samples
    }

    events_seen_by_parent: dict[str, int] = defaultdict(int)
    skipped_events_by_parent: dict[str, int] = defaultdict(int)

    for record in load_jsonl(truth_path):
        parent = str(record.get("parent_label", ""))
        events_seen_by_parent[parent] += 1

        if parent not in vectors_by_sample:
            continue

        contributions = COMPARE.spin_contributions_from_truth_record(record)

        if contributions is None:
            skipped_events_by_parent[parent] += 1
            continue

        vectors_by_sample[parent].append(
            [
                float(contributions[key])
                for key in MOMENT_KEYS
            ]
        )

    generator = np.random.default_rng(args.seed)

    scalar_metrics = [
        "raw_rho_min_eigenvalue",
        "raw_purity",
        "raw_partial_transpose_min_eigenvalue",
        "raw_negativity",
        "raw_concurrence",
        "raw_chsh",
        "projection_frobenius_distance",
        "projected_rho_min_eigenvalue",
        "projected_purity",
        "projected_partial_transpose_min_eigenvalue",
        "projected_negativity",
        "projected_concurrence",
    ]

    result_samples = []
    csv_rows = []
    status = "PASS"

    for parent in requested_samples:
        event_vectors = np.array(
            vectors_by_sample[parent],
            dtype=float,
        )

        if event_vectors.size == 0:
            status = "FAIL"
            result_samples.append({
                "parent_label": parent,
                "status": "FAIL",
                "reason": "no usable events",
                "n_events": 0,
            })
            continue

        n_events = event_vectors.shape[0]

        central_vector = event_vectors.mean(axis=0)
        central_metrics = raw_and_projected_metrics(central_vector)

        bootstrap_values: dict[str, list[float]] = {
            metric: []
            for metric in scalar_metrics
        }

        bootstrap_projection_required: list[bool] = []
        bootstrap_raw_psd: list[bool] = []
        bootstrap_projected_psd: list[bool] = []
        bootstrap_chsh_violation: list[bool] = []

        for _ in range(args.bootstrap):
            indices = generator.integers(
                0,
                n_events,
                size=n_events,
            )

            bootstrap_vector = event_vectors[indices].mean(axis=0)
            metrics = raw_and_projected_metrics(bootstrap_vector)

            for metric in scalar_metrics:
                bootstrap_values[metric].append(
                    float(metrics[metric])
                )

            bootstrap_projection_required.append(
                bool(metrics["projection_required"])
            )

            bootstrap_raw_psd.append(
                bool(metrics["raw_is_psd"])
            )

            bootstrap_projected_psd.append(
                bool(metrics["projected_is_psd"])
            )

            bootstrap_chsh_violation.append(
                bool(float(metrics["raw_chsh"]) > 2.0)
            )

        summaries = {
            metric: summarize(values)
            for metric, values in bootstrap_values.items()
        }

        projection_required_fraction = (
            sum(bootstrap_projection_required)
            / len(bootstrap_projection_required)
        )

        raw_psd_fraction = (
            sum(bootstrap_raw_psd)
            / len(bootstrap_raw_psd)
        )

        projected_psd_fraction = (
            sum(bootstrap_projected_psd)
            / len(bootstrap_projected_psd)
        )

        chsh_violation_fraction = (
            sum(bootstrap_chsh_violation)
            / len(bootstrap_chsh_violation)
        )

        sample_result = {
            "parent_label": parent,
            "status": "PASS",
            "n_events": n_events,
            "central_metrics": central_metrics,
            "bootstrap": {
                "n_bootstrap": args.bootstrap,
                "seed": args.seed,
                "metrics": summaries,
                "projection_required_fraction": (
                    projection_required_fraction
                ),
                "raw_psd_fraction": raw_psd_fraction,
                "projected_psd_fraction": projected_psd_fraction,
                "raw_chsh_violation_fraction": (
                    chsh_violation_fraction
                ),
            },
        }

        result_samples.append(sample_result)

        for metric in scalar_metrics:
            metric_summary = summaries[metric]

            csv_rows.append({
                "parent_label": parent,
                "n_events": n_events,
                "metric": metric,
                "central": central_metrics[metric],
                "bootstrap_mean": metric_summary["mean"],
                "bootstrap_se": metric_summary["se"],
                "bootstrap_p02p5": metric_summary["p02p5"],
                "bootstrap_p16": metric_summary["p16"],
                "bootstrap_p50": metric_summary["p50"],
                "bootstrap_p84": metric_summary["p84"],
                "bootstrap_p97p5": metric_summary["p97p5"],
                "bootstrap_min": metric_summary["min"],
                "bootstrap_max": metric_summary["max"],
                "projection_required_fraction": (
                    projection_required_fraction
                ),
                "raw_psd_fraction": raw_psd_fraction,
                "projected_psd_fraction": projected_psd_fraction,
                "raw_chsh_violation_fraction": (
                    chsh_violation_fraction
                ),
            })

    output = {
        "schema_version": 1,
        "status": status,
        "truth_jsonl": str(truth_path),
        "basis": "rnk_common_v1_nominal_beam_phase9",
        "component_order": list(COMPONENTS),
        "samples_requested": list(requested_samples),
        "events_seen_by_parent_label": dict(
            sorted(events_seen_by_parent.items())
        ),
        "skipped_events_by_parent_label": dict(
            sorted(skipped_events_by_parent.items())
        ),
        "bootstrap": {
            "n_bootstrap": args.bootstrap,
            "seed": args.seed,
            "method": (
                "event-level resampling within each parent_label; "
                "recompute Bplus/Bminus/C, raw rho, PSD trace-one "
                "projection, and raw/projected diagnostics"
            ),
        },
        "samples": result_samples,
        "notes": [
            "Raw and projected observables are retained for each bootstrap replica.",
            "Projection uses nearest PSD trace-one Frobenius projection.",
            "CHSH remains the raw correlation-tensor Horodecki observable.",
            "Projected concurrence and negativity are calculated from the projected density matrix.",
            "Projection-required fraction measures how often the unconstrained raw estimator lies outside the PSD state space.",
        ],
    }

    output_json = Path(args.output_json)
    output_csv = Path(args.output_csv)
    summary_json = Path(args.summary_json)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

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
        "projection_required_fraction",
        "raw_psd_fraction",
        "projected_psd_fraction",
        "raw_chsh_violation_fraction",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()

        for row in csv_rows:
            writer.writerow(row)

    summary = {
        "schema_version": 1,
        "status": status,
        "truth_jsonl": str(truth_path),
        "projected_bootstrap_json": str(output_json),
        "projected_bootstrap_csv": str(output_csv),
        "basis": output["basis"],
        "component_order": output["component_order"],
        "bootstrap": output["bootstrap"],
        "samples": [
            {
                "parent_label": sample["parent_label"],
                "status": sample["status"],
                "n_events": sample.get("n_events", 0),
                "central_raw_min_eigenvalue": (
                    sample.get("central_metrics", {}).get(
                        "raw_rho_min_eigenvalue"
                    )
                ),
                "central_projected_min_eigenvalue": (
                    sample.get("central_metrics", {}).get(
                        "projected_rho_min_eigenvalue"
                    )
                ),
                "central_projection_distance": (
                    sample.get("central_metrics", {}).get(
                        "projection_frobenius_distance"
                    )
                ),
                "projection_required_fraction": (
                    sample.get("bootstrap", {}).get(
                        "projection_required_fraction"
                    )
                ),
                "raw_psd_fraction": (
                    sample.get("bootstrap", {}).get(
                        "raw_psd_fraction"
                    )
                ),
                "projected_psd_fraction": (
                    sample.get("bootstrap", {}).get(
                        "projected_psd_fraction"
                    )
                ),
                "central_projected_purity": (
                    sample.get("central_metrics", {}).get(
                        "projected_purity"
                    )
                ),
                "projected_purity_se": (
                    sample.get("bootstrap", {})
                    .get("metrics", {})
                    .get("projected_purity", {})
                    .get("se")
                ),
                "central_projected_negativity": (
                    sample.get("central_metrics", {}).get(
                        "projected_negativity"
                    )
                ),
                "projected_negativity_p50": (
                    sample.get("bootstrap", {})
                    .get("metrics", {})
                    .get("projected_negativity", {})
                    .get("p50")
                ),
                "projected_negativity_p84": (
                    sample.get("bootstrap", {})
                    .get("metrics", {})
                    .get("projected_negativity", {})
                    .get("p84")
                ),
                "central_projected_concurrence": (
                    sample.get("central_metrics", {}).get(
                        "projected_concurrence"
                    )
                ),
                "projected_concurrence_p50": (
                    sample.get("bootstrap", {})
                    .get("metrics", {})
                    .get("projected_concurrence", {})
                    .get("p50")
                ),
                "projected_concurrence_p84": (
                    sample.get("bootstrap", {})
                    .get("metrics", {})
                    .get("projected_concurrence", {})
                    .get("p84")
                ),
                "central_raw_chsh": (
                    sample.get("central_metrics", {}).get(
                        "raw_chsh"
                    )
                ),
                "raw_chsh_se": (
                    sample.get("bootstrap", {})
                    .get("metrics", {})
                    .get("raw_chsh", {})
                    .get("se")
                ),
                "raw_chsh_violation_fraction": (
                    sample.get("bootstrap", {}).get(
                        "raw_chsh_violation_fraction"
                    )
                ),
            }
            for sample in result_samples
        ],
        "notes": output["notes"],
    }

    summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"PHASE9_PROJECTED_QIS_BOOTSTRAP_STATUS={status}")
    print(f"N_BOOTSTRAP={args.bootstrap}")

    for sample in summary["samples"]:
        print(
            f"{sample['parent_label']:20s} "
            f"rawMin={sample['central_raw_min_eigenvalue']:+.6f} "
            f"projMin={sample['central_projected_min_eigenvalue']:+.3e} "
            f"projFrac={sample['projection_required_fraction']:.3f} "
            f"rawPSDFrac={sample['raw_psd_fraction']:.3f} "
            f"projPSDFrac={sample['projected_psd_fraction']:.3f} "
            f"projPurity={sample['central_projected_purity']:.6f}"
            f"±{sample['projected_purity_se']:.6f} "
            f"projConcP50={sample['projected_concurrence_p50']:.6f} "
            f"projNegP50={sample['projected_negativity_p50']:.6f} "
            f"CHSH={sample['central_raw_chsh']:.6f}"
            f"±{sample['raw_chsh_se']:.6f}"
        )

    print(f"WROTE_JSON={output_json}")
    print(f"WROTE_CSV={output_csv}")
    print(f"WROTE_SUMMARY={summary_json}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
