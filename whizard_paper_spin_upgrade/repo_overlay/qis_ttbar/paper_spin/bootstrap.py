"""Deterministic replica propagation for nonlinear tomography observables.

The fifteen linear angular coefficients already receive an analytic full
covariance from the event-level estimands.  Replica resampling is used here for
quantities that are nonlinear in those coefficients: density-matrix
physicality, Euclidean physical projection, entanglement markers, concurrence,
negativity, and CHSH reach.

Replicas use the ordinary nonparametric bootstrap (multinomial event counts).
For weighted positive-event samples, the original event weights are multiplied
by the replica multiplicities.  This preserves the empirical event and weight
distribution without introducing an unvalidated signed-weight prescription.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .density import (
    all_density_measures,
    density_matrix_from_coefficients,
    project_density_matrix,
    validate_density_matrix,
)
from .io import AnalyzerSample
from .moments import estimate_moments


DEFAULT_MEASURE_NAMES: tuple[str, ...] = (
    "purity",
    "min_eigenvalue",
    "partial_transpose_min_eigenvalue",
    "negativity",
    "concurrence",
    "von_neumann_entropy_bits",
    "chsh_maximum",
    "D_lc_1",
    "D_lc_k",
    "D_lc_r",
    "D_lc_n",
    "D_lc_min",
)


@dataclass(frozen=True)
class ReplicaResult:
    coefficient_replicas: np.ndarray
    raw_measure_replicas: np.ndarray
    projected_measure_replicas: np.ndarray
    measure_names: tuple[str, ...]
    seed: int
    replica_start: int
    replica_stop: int
    metadata: dict[str, Any]

    @property
    def replicas(self) -> int:
        return int(self.replica_stop - self.replica_start)

    def coefficient_covariance(self) -> np.ndarray:
        if self.replicas < 2:
            raise ValueError("At least two replicas are required")
        return np.cov(self.coefficient_replicas, rowvar=False, ddof=1)

    def raw_measure_covariance(self) -> np.ndarray:
        if self.replicas < 2:
            raise ValueError("At least two replicas are required")
        return np.cov(self.raw_measure_replicas, rowvar=False, ddof=1)

    def projected_measure_covariance(self) -> np.ndarray:
        if self.replicas < 2:
            raise ValueError("At least two replicas are required")
        return np.cov(self.projected_measure_replicas, rowvar=False, ddof=1)


def _measures_vector(rho: np.ndarray, names: tuple[str, ...]) -> np.ndarray:
    mapping = all_density_measures(rho)
    return np.asarray([float(mapping[name]) for name in names], dtype=float)


def bootstrap_tomography(
    sample: AnalyzerSample,
    replicas: int,
    seed: int,
    replica_start: int = 0,
    replica_stop: int | None = None,
    measure_names: tuple[str, ...] = DEFAULT_MEASURE_NAMES,
) -> ReplicaResult:
    """Run a reproducible slice of the nonparametric bootstrap.

    Each replica has a seed derived from ``SeedSequence([seed, replica_id])``.
    This means independently submitted replica ranges reproduce exactly the
    same result as a single local run and can be merged without overlap.
    """

    if replicas <= 0:
        raise ValueError("replicas must be positive")
    if replica_stop is None:
        replica_stop = replicas
    if not (0 <= replica_start < replica_stop <= replicas):
        raise ValueError(
            f"Invalid replica range [{replica_start},{replica_stop}) for {replicas}"
        )
    if np.any(sample.weights < 0.0):
        raise ValueError("Bootstrap implementation requires non-negative weights")

    event_count = len(sample.weights)
    coefficient_rows: list[np.ndarray] = []
    raw_rows: list[np.ndarray] = []
    projected_rows: list[np.ndarray] = []
    raw_unphysical = 0

    for replica_id in range(replica_start, replica_stop):
        rng = np.random.default_rng(np.random.SeedSequence([seed, replica_id]))
        multiplicity = rng.multinomial(
            event_count,
            np.full(event_count, 1.0 / event_count),
        )
        replica_weights = sample.weights * multiplicity
        nonzero = replica_weights > 0.0
        replica_sample = AnalyzerSample(
            plus=sample.plus[nonzero],
            minus=sample.minus[nonzero],
            weights=replica_weights[nonzero],
            event_keys=None,
            source_path=sample.source_path,
            convention_name=sample.convention_name,
            metadata={
                **sample.metadata,
                "bootstrap_replica": replica_id,
            },
        )
        moments = estimate_moments(replica_sample)
        coefficients = moments.coefficient_vector
        rho_raw = density_matrix_from_coefficients(
            coefficients,
            sample.convention_name,
        )
        validation = validate_density_matrix(rho_raw)
        if not validation.valid:
            raw_unphysical += 1
        projection = project_density_matrix(rho_raw)

        coefficient_rows.append(coefficients)
        raw_rows.append(_measures_vector(rho_raw, measure_names))
        projected_rows.append(_measures_vector(projection.rho, measure_names))

    return ReplicaResult(
        coefficient_replicas=np.vstack(coefficient_rows),
        raw_measure_replicas=np.vstack(raw_rows),
        projected_measure_replicas=np.vstack(projected_rows),
        measure_names=measure_names,
        seed=int(seed),
        replica_start=int(replica_start),
        replica_stop=int(replica_stop),
        metadata={
            "events": int(event_count),
            "raw_unphysical_replicas": int(raw_unphysical),
            "raw_unphysical_fraction": float(
                raw_unphysical / (replica_stop - replica_start)
            ),
            "resampling": "nonparametric_multinomial",
        },
    )


def percentile_summary(
    values: np.ndarray,
    names: tuple[str, ...],
    confidence_level: float = 0.68,
) -> list[dict[str, float | str]]:
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[1] != len(names):
        raise ValueError("values shape and names are inconsistent")
    alpha = 0.5 * (1.0 - confidence_level)
    quantiles = np.quantile(values, [alpha, 0.5, 1.0 - alpha], axis=0)
    result: list[dict[str, float | str]] = []
    for index, name in enumerate(names):
        result.append(
            {
                "name": name,
                "mean": float(np.mean(values[:, index])),
                "std": float(np.std(values[:, index], ddof=1)),
                "lower": float(quantiles[0, index]),
                "median": float(quantiles[1, index]),
                "upper": float(quantiles[2, index]),
                "confidence_level": float(confidence_level),
            }
        )
    return result
