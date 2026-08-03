#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


def import_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCRIPT_DIR = Path(__file__).resolve().parent
QIS = import_module_from_path(
    "phase9_qis_builder",
    SCRIPT_DIR / "build_phase9_density_matrix_qis_observables.py",
)


def project_vector_to_simplex(values: np.ndarray) -> np.ndarray:
    """
    Euclidean projection of a real vector onto:
        x_i >= 0
        sum_i x_i = 1
    """
    v = np.asarray(values, dtype=float)

    if v.ndim != 1:
        raise ValueError("simplex projection expects a one-dimensional vector")

    u = np.sort(v)[::-1]
    cssv = np.cumsum(u)

    rho_candidates = np.nonzero(
        u - (cssv - 1.0) / np.arange(1, len(u) + 1) > 0
    )[0]

    if len(rho_candidates) == 0:
        return np.full_like(v, 1.0 / len(v))

    rho = rho_candidates[-1]
    theta = (cssv[rho] - 1.0) / float(rho + 1)

    return np.maximum(v - theta, 0.0)


def project_density_matrix(rho: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    hermitian = 0.5 * (rho + rho.conjugate().T)

    eigvals, eigvecs = np.linalg.eigh(hermitian)
    projected_eigvals = project_vector_to_simplex(eigvals.real)

    projected = (
        eigvecs
        @ np.diag(projected_eigvals.astype(complex))
        @ eigvecs.conjugate().T
    )

    projected = 0.5 * (projected + projected.conjugate().T)
    projected /= np.trace(projected).real

    diagnostics = {
        "raw_eigenvalues": [float(x) for x in eigvals.real],
        "projected_eigenvalues": [float(x) for x in projected_eigvals],
        "frobenius_distance": float(np.linalg.norm(projected - rho, ord="fro")),
        "hermitization_distance": float(
            np.linalg.norm(hermitian - rho, ord="fro")
        ),
        "trace_after_projection": float(np.trace(projected).real),
        "min_eigenvalue_after_projection": float(
            np.min(np.linalg.eigvalsh(projected)).real
        ),
    }

    return projected, diagnostics


def complex_matrix_from_real_imag(
    real_matrix: list[list[float]],
    imag_matrix: list[list[float]] | None,
) -> np.ndarray:
    real = np.array(real_matrix, dtype=float)

    if imag_matrix is None:
        raise ValueError(
            "raw QIS sample is missing rho_imag; refusing to project a "
            "real-only approximation of the complex density matrix"
        )

    imag = np.array(imag_matrix, dtype=float)

    if real.shape != (4, 4) or imag.shape != (4, 4):
        raise ValueError(
            f"expected 4x4 rho matrices, got real={real.shape}, imag={imag.shape}"
        )

    return real + 1j * imag


def matrix_to_json(matrix: np.ndarray) -> dict[str, list[list[float]]]:
    return {
        "real": [[float(x.real) for x in row] for row in matrix],
        "imag": [[float(x.imag) for x in row] for row in matrix],
    }


def projected_qis_metrics(rho: np.ndarray) -> dict[str, Any]:
    eigvals = sorted(float(x.real) for x in np.linalg.eigvalsh(rho))

    purity = float(np.trace(rho @ rho).real)

    rho_pt = QIS.partial_transpose_second_qubit(rho)
    pt_eigvals = sorted(float(x.real) for x in np.linalg.eigvalsh(rho_pt))

    negativity = float(sum(abs(x) for x in pt_eigvals if x < 0.0))
    concurrence = float(QIS.concurrence_candidate(rho))

    return {
        "rho_trace_real": float(np.trace(rho).real),
        "rho_trace_imag": float(np.trace(rho).imag),
        "rho_hermiticity_max_abs_residual": float(
            np.max(np.abs(rho - rho.conjugate().T))
        ),
        "rho_min_eigenvalue": float(min(eigvals)),
        "rho_eigenvalues": eigvals,
        "purity_tr_rho2": purity,
        "linear_entropy_1_minus_purity": float(1.0 - purity),
        "partial_transpose_min_eigenvalue": float(min(pt_eigvals)),
        "partial_transpose_eigenvalues": pt_eigvals,
        "negativity_candidate": negativity,
        "concurrence_candidate": concurrence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-qis-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--summary-json", required=True)
    args = parser.parse_args()

    raw_path = Path(args.raw_qis_json)
    payload = json.loads(raw_path.read_text(encoding="utf-8"))

    output_samples = []

    for sample in payload.get("samples", []):
        parent = sample["parent_label"]

        raw_rho = complex_matrix_from_real_imag(
            sample["rho_real"],
            sample.get("rho_imag"),
        )

        # Validate that the serialized complex matrix reproduces the metrics
        # recorded by the upstream raw-QIS builder. This prevents accidental
        # projection of a truncated or schema-incompatible matrix.
        reconstructed_raw_eigenvalues = np.linalg.eigvalsh(raw_rho)
        reconstructed_raw_min_eigenvalue = float(
            np.min(reconstructed_raw_eigenvalues).real
        )
        reconstructed_raw_purity = float(
            np.trace(raw_rho @ raw_rho).real
        )

        expected_raw_min_eigenvalue = float(sample["rho_min_eigenvalue"])
        expected_raw_purity = float(sample["purity_tr_rho2"])

        min_eigenvalue_residual = abs(
            reconstructed_raw_min_eigenvalue
            - expected_raw_min_eigenvalue
        )
        purity_residual = abs(
            reconstructed_raw_purity
            - expected_raw_purity
        )

        if min_eigenvalue_residual > 1.0e-10:
            raise ValueError(
                f"{parent}: serialized rho does not reproduce raw minimum "
                f"eigenvalue: reconstructed={reconstructed_raw_min_eigenvalue}, "
                f"expected={expected_raw_min_eigenvalue}, "
                f"residual={min_eigenvalue_residual}"
            )

        if purity_residual > 1.0e-10:
            raise ValueError(
                f"{parent}: serialized rho does not reproduce raw purity: "
                f"reconstructed={reconstructed_raw_purity}, "
                f"expected={expected_raw_purity}, "
                f"residual={purity_residual}"
            )

        projected_rho, projection = project_density_matrix(raw_rho)
        projected_metrics = projected_qis_metrics(projected_rho)

        raw_min_eig = float(sample["rho_min_eigenvalue"])
        projected_min_eig = float(projected_metrics["rho_min_eigenvalue"])

        output_samples.append({
            "parent_label": parent,
            "n_events": int(sample.get("n_events", 0)),
            "basis": sample.get("basis", payload.get("basis")),
            "raw": {
                "rho_min_eigenvalue": raw_min_eig,
                "purity_tr_rho2": float(sample["purity_tr_rho2"]),
                "partial_transpose_min_eigenvalue": float(
                    sample["partial_transpose_min_eigenvalue"]
                ),
                "negativity_candidate": float(
                    sample["negativity_candidate"]
                ),
                "concurrence_candidate": float(
                    sample["concurrence_candidate"]
                ),
                "bell_chsh_horodecki_max": float(
                    sample["bell_chsh_horodecki_max"]
                ),
            },
            "projection": projection,
            "projected": projected_metrics,
            "projected_rho": matrix_to_json(projected_rho),
            "projection_changed_matrix": bool(
                projection["frobenius_distance"] > 1.0e-12
            ),
            "raw_was_positive_semidefinite": bool(raw_min_eig >= -1.0e-8),
            "projected_is_positive_semidefinite": bool(
                projected_min_eig >= -1.0e-10
            ),
        })

    output_samples.sort(key=lambda row: row["parent_label"])

    status = "PASS"

    for sample in output_samples:
        if not sample["projected_is_positive_semidefinite"]:
            status = "FAIL"

        trace = sample["projected"]["rho_trace_real"]
        if abs(trace - 1.0) > 1.0e-10:
            status = "FAIL"

    output = {
        "schema_version": 1,
        "status": status,
        "raw_qis_json": str(raw_path),
        "basis": payload.get("basis"),
        "component_order": payload.get("component_order"),
        "projection_method": {
            "name": "nearest_psd_trace_one_frobenius",
            "steps": [
                "Hermitize rho.",
                "Diagonalize the Hermitian matrix.",
                "Project its eigenvalue vector onto the probability simplex.",
                "Reconstruct and normalize the projected matrix.",
            ],
        },
        "samples": output_samples,
        "notes": [
            "Raw and projected density matrices are both retained.",
            "Projection is a physicality correction, not a substitute for reporting raw estimator behavior.",
            "CHSH depends only on the original moment correlation tensor in the current raw product and is therefore retained from the raw calculation.",
            "Projected concurrence and negativity are calculated from the projected density matrix.",
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

    csv_fields = [
        "parent_label",
        "n_events",
        "raw_rho_min_eigenvalue",
        "projected_rho_min_eigenvalue",
        "raw_purity",
        "projected_purity",
        "raw_partial_transpose_min_eigenvalue",
        "projected_partial_transpose_min_eigenvalue",
        "raw_negativity",
        "projected_negativity",
        "raw_concurrence",
        "projected_concurrence",
        "raw_chsh",
        "projection_frobenius_distance",
        "projection_changed_matrix",
        "raw_was_positive_semidefinite",
        "projected_is_positive_semidefinite",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()

        for sample in output_samples:
            writer.writerow({
                "parent_label": sample["parent_label"],
                "n_events": sample["n_events"],
                "raw_rho_min_eigenvalue": sample["raw"]["rho_min_eigenvalue"],
                "projected_rho_min_eigenvalue": sample["projected"]["rho_min_eigenvalue"],
                "raw_purity": sample["raw"]["purity_tr_rho2"],
                "projected_purity": sample["projected"]["purity_tr_rho2"],
                "raw_partial_transpose_min_eigenvalue": sample["raw"]["partial_transpose_min_eigenvalue"],
                "projected_partial_transpose_min_eigenvalue": sample["projected"]["partial_transpose_min_eigenvalue"],
                "raw_negativity": sample["raw"]["negativity_candidate"],
                "projected_negativity": sample["projected"]["negativity_candidate"],
                "raw_concurrence": sample["raw"]["concurrence_candidate"],
                "projected_concurrence": sample["projected"]["concurrence_candidate"],
                "raw_chsh": sample["raw"]["bell_chsh_horodecki_max"],
                "projection_frobenius_distance": sample["projection"]["frobenius_distance"],
                "projection_changed_matrix": sample["projection_changed_matrix"],
                "raw_was_positive_semidefinite": sample["raw_was_positive_semidefinite"],
                "projected_is_positive_semidefinite": sample["projected_is_positive_semidefinite"],
            })

    summary = {
        "schema_version": 1,
        "status": status,
        "raw_qis_json": str(raw_path),
        "projected_qis_json": str(output_json),
        "projected_qis_csv": str(output_csv),
        "basis": output.get("basis"),
        "projection_method": output["projection_method"],
        "samples": [
            {
                "parent_label": sample["parent_label"],
                "n_events": sample["n_events"],
                "raw_rho_min_eigenvalue": sample["raw"]["rho_min_eigenvalue"],
                "projected_rho_min_eigenvalue": sample["projected"]["rho_min_eigenvalue"],
                "projection_frobenius_distance": sample["projection"]["frobenius_distance"],
                "raw_was_positive_semidefinite": sample["raw_was_positive_semidefinite"],
                "projected_is_positive_semidefinite": sample["projected_is_positive_semidefinite"],
                "raw_purity": sample["raw"]["purity_tr_rho2"],
                "projected_purity": sample["projected"]["purity_tr_rho2"],
                "raw_negativity": sample["raw"]["negativity_candidate"],
                "projected_negativity": sample["projected"]["negativity_candidate"],
                "raw_concurrence": sample["raw"]["concurrence_candidate"],
                "projected_concurrence": sample["projected"]["concurrence_candidate"],
                "raw_chsh": sample["raw"]["bell_chsh_horodecki_max"],
            }
            for sample in output_samples
        ],
        "notes": output["notes"],
    }

    summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"PHASE9_QIS_PROJECTION_STATUS={status}")

    for sample in output_samples:
        print(
            f"{sample['parent_label']:20s} "
            f"rawMinEig={sample['raw']['rho_min_eigenvalue']:+.8f} "
            f"projMinEig={sample['projected']['rho_min_eigenvalue']:+.8e} "
            f"distance={sample['projection']['frobenius_distance']:.8e} "
            f"rawPurity={sample['raw']['purity_tr_rho2']:.6f} "
            f"projPurity={sample['projected']['purity_tr_rho2']:.6f} "
            f"projConc={sample['projected']['concurrence_candidate']:.6f} "
            f"projNeg={sample['projected']['negativity_candidate']:.6f}"
        )

    print(f"WROTE_JSON={output_json}")
    print(f"WROTE_CSV={output_csv}")
    print(f"WROTE_SUMMARY={summary_json}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
