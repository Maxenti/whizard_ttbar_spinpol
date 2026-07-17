from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from ..qis.measures import all_measures
from ..qis.magic import stabilizer_renyi2_magic
from ..qis.steering import linear_three_setting_steering
from ..tomography.bootstrap import bootstrap_tomography
from ..tomography.binning import BinSelection, inclusive_selection, one_dimensional_bins, two_dimensional_bins
from ..tomography.fit import fit_physical_density_matrix


def _arrays(frame: pd.DataFrame, order: tuple[str, str, str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    plus = frame[[f"uplus_{name}" for name in order]].to_numpy(float)
    minus = frame[[f"uminus_{name}" for name in order]].to_numpy(float)
    weights = frame["event_weight"].to_numpy(float) if "event_weight" in frame else np.ones(len(frame))
    return plus, minus, weights


def run_tomography_for_frame(
    frame: pd.DataFrame,
    *, output_dir: str | Path,
    basis_order: tuple[str, str, str] = ("k", "r", "n"),
    replicas: int = 1000,
    seed: int = 730001,
    confidence_level: float = 0.68,
    alpha_plus: float = 1.0,
    alpha_minus: float = 1.0,
    mtt_edges: Iterable[float] | None = None,
    cos_theta_edges: Iterable[float] | None = None,
    minimum_events: int = 100,
    physical_fit: bool = True,
) -> list[dict[str, object]]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    selections: list[BinSelection] = [inclusive_selection(frame)]
    if mtt_edges is not None:
        selections.extend(one_dimensional_bins(frame, "mtt_GeV", mtt_edges))
    if cos_theta_edges is not None:
        selections.extend(one_dimensional_bins(frame, "cos_theta_t", cos_theta_edges))
    if mtt_edges is not None and cos_theta_edges is not None:
        selections.extend(two_dimensional_bins(frame, "mtt_GeV", mtt_edges, "cos_theta_t", cos_theta_edges))
    results = []
    for bin_index, selection in enumerate(selections):
        selected = frame.loc[selection.mask]
        if len(selected) < minimum_events:
            results.append({"bin": selection.name, "events": len(selected), "status": "insufficient_statistics", **selection.metadata})
            continue
        plus, minus, weights = _arrays(selected, basis_order)
        bootstrap = bootstrap_tomography(
            plus, minus, weights=weights, replicas=replicas, seed=seed + bin_index,
            confidence_level=confidence_level, alpha_plus=alpha_plus, alpha_minus=alpha_minus,
            basis_order=basis_order,
        )
        central = bootstrap.central
        rho = central.rho_physical
        fit_payload = None
        if physical_fit:
            fit = fit_physical_density_matrix(central.rho_raw, target_coefficients=central.coefficient_vector, covariance=bootstrap.covariance)
            rho = fit.rho
            fit_payload = {"success": fit.success, "objective": fit.objective, "iterations": fit.iterations, "message": fit.message}
        payload = {
            "bin": selection.name, "events": len(selected), "status": "success", **selection.metadata,
            "tomography": central.as_serializable(),
            "bootstrap_lower": bootstrap.lower.tolist(), "bootstrap_upper": bootstrap.upper.tolist(),
            "physical_fit": fit_payload,
            "qis": {**all_measures(rho), "stabilizer_renyi2_magic": stabilizer_renyi2_magic(rho), **linear_three_setting_steering(rho)},
        }
        (output_dir / f"{selection.name}.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        results.append(payload)
    summary_rows = []
    for result in results:
        row = {key: value for key, value in result.items() if key not in {"tomography", "qis", "physical_fit", "bootstrap_lower", "bootstrap_upper"}}
        if result.get("status") == "success":
            row.update(result["qis"])
        summary_rows.append(row)
    pd.DataFrame(summary_rows).to_csv(output_dir / "tomography_summary.csv", index=False)
    return results
