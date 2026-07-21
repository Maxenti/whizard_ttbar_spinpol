"""Independent Standard-Model benchmark and cross-sample closure utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .analytic_tree import TreeLevelSM
from .contracts import COEFFICIENT_NAMES
from .io import SampleDescriptor
from .moments import MomentResult, compare_independent


@dataclass(frozen=True)
class AnalyticBenchmarkResult:
    coefficient_vector: np.ndarray
    comparison_delta: np.ndarray
    comparison_z: np.ndarray
    chi2: float
    ndof: int
    mode: str
    strict_eligible: bool
    metadata: dict[str, Any]


def first_present(frame: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    for name in candidates:
        if name in frame.columns:
            return name
    return None


def extract_event_conditioning(
    frame: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    analytic = config.get("analytic_benchmark", {})
    reviewed = bool(analytic.get("kinematics_map_reviewed", False))

    sqrt_s_column = analytic.get("sqrt_s_column") or first_present(
        frame,
        analytic.get(
            "sqrt_s_candidates",
            ["mtt_GeV", "sqrt_s_hat_GeV", "ttbar_mass_GeV", "m_tt_GeV"],
        ),
    )
    costheta_column = analytic.get("costheta_column") or first_present(
        frame,
        analytic.get(
            "costheta_candidates",
            [
                "top_costheta_beam_plus",
                "costheta_top_beam_plus",
                "cos_theta_top_beam_plus",
                "top_costheta",
                "cos_theta_top",
            ],
        ),
    )
    weight_column = analytic.get("weight_column") or first_present(
        frame,
        analytic.get(
            "weight_candidates",
            ["weight", "event_weight", "nominal_weight"],
        ),
    )
    if sqrt_s_column is None or costheta_column is None:
        raise KeyError(
            "Cannot construct event-conditioned analytic benchmark. Set "
            "analytic_benchmark.sqrt_s_column and costheta_column explicitly. "
            f"Available columns: {list(frame.columns)}"
        )
    if not reviewed:
        raise RuntimeError(
            "analytic_benchmark.kinematics_map_reviewed is false. The sign of "
            "cos(theta) must be audited against the incoming positive-lepton "
            "direction before comparing signed coefficients."
        )

    sqrt_s = pd.to_numeric(frame[sqrt_s_column], errors="coerce").to_numpy(float)
    costheta = (
        float(analytic.get("costheta_sign", 1.0))
        * pd.to_numeric(frame[costheta_column], errors="coerce").to_numpy(float)
    )
    if weight_column is None:
        weights = np.ones(len(frame), dtype=float)
    else:
        weights = pd.to_numeric(frame[weight_column], errors="coerce").to_numpy(float)

    finite = np.isfinite(sqrt_s) & np.isfinite(costheta) & np.isfinite(weights)
    if np.any(weights[finite] < 0.0):
        raise ValueError("Analytic event conditioning requires non-negative weights")
    return (
        sqrt_s[finite],
        costheta[finite],
        weights[finite],
        {
            "sqrt_s_column": sqrt_s_column,
            "costheta_column": costheta_column,
            "costheta_sign": float(analytic.get("costheta_sign", 1.0)),
            "weight_column": weight_column,
            "rows_input": int(len(frame)),
            "rows_finite": int(np.count_nonzero(finite)),
        },
    )


def compare_to_analytic(
    measured: MomentResult,
    descriptor: SampleDescriptor,
    frame: pd.DataFrame,
    tree: TreeLevelSM,
    config: dict[str, Any],
) -> AnalyticBenchmarkResult:
    analytic_config = config.get("analytic_benchmark", {})
    mode = str(analytic_config.get("mode", "event_conditioned"))

    if descriptor.spin_mode != "sc":
        raise ValueError("Production spin-density benchmark applies to SC samples only")

    if mode == "integrated_born":
        prediction = tree.integrated_density(
            float(analytic_config.get("sqrt_s_GeV", 500.0)),
            descriptor.initial_state,
            descriptor.polarization,
            int(analytic_config.get("quadrature_points", 256)),
        )
        kinematics_metadata: dict[str, Any] = {}
    elif mode == "event_conditioned":
        sqrt_s, costheta, weights, kinematics_metadata = extract_event_conditioning(
            frame,
            config,
        )
        prediction = tree.event_conditioned_density(
            sqrt_s,
            costheta,
            weights,
            descriptor.initial_state,
            descriptor.polarization,
        )
    else:
        raise ValueError(f"Unsupported analytic benchmark mode {mode!r}")

    predicted = np.asarray(prediction["coefficient_vector"], dtype=float)
    delta = measured.coefficient_vector - predicted
    covariance = measured.covariance
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    z = np.divide(
        delta,
        standard_errors,
        out=np.full_like(delta, np.nan),
        where=standard_errors > 0.0,
    )
    inverse = np.linalg.pinv(covariance, hermitian=True)
    chi2 = float(delta @ inverse @ delta)
    ndof = int(np.linalg.matrix_rank(covariance))

    parameters_reviewed = bool(tree.parameters.generator_match_reviewed)
    strict_eligible = bool(
        parameters_reviewed
        and analytic_config.get("kinematics_map_reviewed", False)
        and descriptor.stage == "lhe"
        and descriptor.spin_mode == "sc"
    )

    return AnalyticBenchmarkResult(
        coefficient_vector=predicted,
        comparison_delta=delta,
        comparison_z=z,
        chi2=chi2,
        ndof=ndof,
        mode=mode,
        strict_eligible=strict_eligible,
        metadata={
            **kinematics_metadata,
            "prediction": {
                key: value
                for key, value in prediction.items()
                if key not in {"rho", "coefficient_vector"}
            },
            "sm_parameters_generator_match_reviewed": parameters_reviewed,
            "strict_eligibility_reason": (
                "eligible"
                if strict_eligible
                else "requires reviewed generator SM inputs, reviewed kinematics map, "
                "LHE stage, and spin-correlated decays"
            ),
        },
    )


def comparison_rows(
    result: AnalyticBenchmarkResult,
    descriptor: SampleDescriptor,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, name in enumerate(COEFFICIENT_NAMES):
        rows.append(
            {
                "dataset": descriptor.dataset,
                "sample_id": descriptor.sample_id,
                "initial_state": descriptor.initial_state,
                "decay_channel": descriptor.decay_channel,
                "polarization": descriptor.polarization,
                "stage": descriptor.stage,
                "coefficient_name": name,
                "analytic_coefficient": float(result.coefficient_vector[index]),
                "measured_minus_analytic": float(result.comparison_delta[index]),
                "z": float(result.comparison_z[index]),
                "benchmark_mode": result.mode,
                "strict_eligible": result.strict_eligible,
            }
        )
    return rows


def compare_lepton_universality(
    ee: MomentResult,
    mumu: MomentResult,
) -> dict[str, Any]:
    """Compare e+e- and mu+mu- samples with full independent covariance."""

    result = compare_independent(ee, mumu)
    return {
        **result,
        "coefficient_names": COEFFICIENT_NAMES,
        "interpretation": (
            "At 500 GeV the initial-lepton mass difference is negligible for the "
            "hard electroweak spin density. Residual differences can reflect finite "
            "statistics, generator settings, or sample-specific ISR realizations."
        ),
    }
