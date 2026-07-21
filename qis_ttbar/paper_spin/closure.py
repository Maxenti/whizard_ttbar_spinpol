"""Moment-versus-shape closure with correct same-sample replica covariance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .io import AnalyzerSample
from .moments import estimate_moments
from .shape_fit import fit_physical_density_matrix
from .synthetic import sample_angular_density


@dataclass(frozen=True)
class EstimatorClosureResult:
    moment_coefficients: np.ndarray
    shape_coefficients: np.ndarray
    delta_shape_minus_moment: np.ndarray
    delta_covariance: np.ndarray | None
    delta_standard_errors: np.ndarray | None
    pulls: np.ndarray | None
    max_abs_pull: float | None
    delta_replicas: np.ndarray | None
    shape_fit_success: bool
    metadata: dict[str, Any]


def fit_moment_and_shape(
    sample: AnalyzerSample,
    shape_max_iterations: int = 2000,
    calculate_shape_covariance: bool = True,
) -> tuple[np.ndarray, np.ndarray, bool, dict[str, Any]]:
    moments = estimate_moments(sample)
    shape = fit_physical_density_matrix(
        sample,
        initial_coefficient_vector=moments.coefficient_vector,
        convention=sample.convention_name,
        max_iterations=shape_max_iterations,
        calculate_covariance=calculate_shape_covariance,
    )
    return (
        moments.coefficient_vector,
        shape.coefficient_vector,
        shape.success,
        {
            "shape_message": shape.message,
            "shape_objective": shape.objective,
            "shape_iterations": shape.iterations,
            "shape_min_pdf_bracket": shape.min_pdf_bracket,
        },
    )


def joint_bootstrap_moment_shape_closure(
    sample: AnalyzerSample,
    replicas: int,
    seed: int,
    replica_start: int = 0,
    replica_stop: int | None = None,
    shape_max_iterations: int = 1200,
) -> EstimatorClosureResult:
    if replica_stop is None:
        replica_stop = replicas
    if not (0 <= replica_start < replica_stop <= replicas):
        raise ValueError("Invalid replica range")

    moment_central, shape_central, success, central_metadata = fit_moment_and_shape(
        sample,
        shape_max_iterations=shape_max_iterations,
        calculate_shape_covariance=True,
    )
    deltas: list[np.ndarray] = []
    failed = 0
    event_count = len(sample.weights)

    for replica_id in range(replica_start, replica_stop):
        rng = np.random.default_rng(np.random.SeedSequence([seed, replica_id]))
        multiplicity = rng.multinomial(
            event_count,
            np.full(event_count, 1.0 / event_count),
        )
        replica_weights = sample.weights * multiplicity
        nonzero = replica_weights > 0.0
        replica = AnalyzerSample(
            plus=sample.plus[nonzero],
            minus=sample.minus[nonzero],
            weights=replica_weights[nonzero],
            event_keys=None,
            source_path=sample.source_path,
            convention_name=sample.convention_name,
            metadata={**sample.metadata, "closure_replica": replica_id},
        )
        moment, shape, fit_success, _ = fit_moment_and_shape(
            replica,
            shape_max_iterations=shape_max_iterations,
            calculate_shape_covariance=False,
        )
        if not fit_success or not np.all(np.isfinite(shape)):
            failed += 1
            continue
        deltas.append(shape - moment)

    if len(deltas) < 2:
        raise RuntimeError(
            f"Only {len(deltas)} successful joint closure replicas; failed={failed}"
        )
    delta_replicas = np.vstack(deltas)
    covariance = np.cov(delta_replicas, rowvar=False, ddof=1)
    covariance = 0.5 * (covariance + covariance.T)
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    central_delta = shape_central - moment_central
    pulls = np.divide(
        central_delta,
        standard_errors,
        out=np.full_like(central_delta, np.nan),
        where=standard_errors > 0.0,
    )
    return EstimatorClosureResult(
        moment_coefficients=moment_central,
        shape_coefficients=shape_central,
        delta_shape_minus_moment=central_delta,
        delta_covariance=covariance,
        delta_standard_errors=standard_errors,
        pulls=pulls,
        max_abs_pull=float(np.nanmax(np.abs(pulls))),
        delta_replicas=delta_replicas,
        shape_fit_success=success,
        metadata={
            **central_metadata,
            "replicas_requested": int(replica_stop - replica_start),
            "replicas_successful": int(len(deltas)),
            "replicas_failed": int(failed),
            "replica_start": int(replica_start),
            "replica_stop": int(replica_stop),
            "seed": int(seed),
            "same_sample_covariance": "joint_nonparametric_bootstrap",
        },
    )


def synthetic_moment_shape_closure(
    injected_coefficients: np.ndarray,
    events: int,
    seed: int,
    shape_max_iterations: int = 2000,
) -> EstimatorClosureResult:
    plus, minus = sample_angular_density(injected_coefficients, events, seed)
    sample = AnalyzerSample(
        plus=plus,
        minus=minus,
        weights=np.ones(events, dtype=float),
        event_keys=np.arange(events),
        source_path=__import__("pathlib").Path("synthetic:moment_shape"),
        convention_name="lepton_collider_paper_v1",
        metadata={"synthetic": True},
    )
    moment, shape, success, metadata = fit_moment_and_shape(
        sample,
        shape_max_iterations=shape_max_iterations,
        calculate_shape_covariance=True,
    )
    return EstimatorClosureResult(
        moment_coefficients=moment,
        shape_coefficients=shape,
        delta_shape_minus_moment=shape - moment,
        delta_covariance=None,
        delta_standard_errors=None,
        pulls=None,
        max_abs_pull=None,
        delta_replicas=None,
        shape_fit_success=success,
        metadata={
            **metadata,
            "events": int(events),
            "seed": int(seed),
            "injected_coefficients": np.asarray(injected_coefficients).tolist(),
        },
    )
