"""Unbiased angular-moment estimators and full covariance propagation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .contracts import (
    AXES,
    COEFFICIENT_INDEX,
    COEFFICIENT_NAMES,
    coefficient_dict,
    coefficient_vector_to_parts,
)
from .io import AnalyzerSample


@dataclass(frozen=True)
class MomentResult:
    coefficient_vector: np.ndarray
    covariance: np.ndarray
    standard_errors: np.ndarray
    effective_events: float
    weight_sum: float
    events: int
    convention_name: str
    metadata: dict[str, Any]

    @property
    def coefficients(self) -> dict[str, float]:
        return coefficient_dict(self.coefficient_vector)


@dataclass(frozen=True)
class DerivedResult:
    names: tuple[str, ...]
    values: np.ndarray
    covariance: np.ndarray
    standard_errors: np.ndarray

    def as_dict(self) -> dict[str, float]:
        return {
            name: float(value)
            for name, value in zip(self.names, self.values, strict=True)
        }


def event_estimands(plus: np.ndarray, minus: np.ndarray) -> np.ndarray:
    """Return the 15 event-level unbiased estimands.

    With signed analyzers of unit analyzing power,

      E[3 a_i]       = B1_i
      E[3 b_j]       = B2_j
      E[9 a_i b_j]   = C_ij.
    """

    plus = np.asarray(plus, dtype=float)
    minus = np.asarray(minus, dtype=float)
    if plus.ndim != 2 or minus.ndim != 2:
        raise ValueError("plus and minus must be two-dimensional arrays")
    if plus.shape != minus.shape or plus.shape[1] != 3:
        raise ValueError(
            f"Expected plus/minus shape (N,3), got {plus.shape} and {minus.shape}"
        )
    outer = np.einsum("ni,nj->nij", plus, minus).reshape(len(plus), 9)
    return np.concatenate([3.0 * plus, 3.0 * minus, 9.0 * outer], axis=1)


def weighted_mean_and_covariance_of_mean(
    values: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Calculate weighted mean and an unbiased covariance of that mean.

    Let normalized weights be a_i=w_i/sum(w).  The covariance estimator is

      Cov(mean) = [sum_i a_i^2 (x_i-xbar)(x_i-xbar)^T]
                  / [1 - sum_i a_i^2].

    For equal weights this reduces exactly to sample_covariance/N.
    """

    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if values.ndim != 2:
        raise ValueError(f"values must have shape (N,D), got {values.shape}")
    if weights.shape != (len(values),):
        raise ValueError(
            f"weights must have shape ({len(values)},), got {weights.shape}"
        )
    if len(values) < 2:
        raise ValueError("At least two events are required")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(weights)):
        raise ValueError("Non-finite values or weights")
    if np.any(weights < 0):
        raise ValueError(
            "This covariance estimator requires non-negative weights.  Signed-weight "
            "samples require a dedicated sandwich/replica treatment."
        )
    weight_sum = float(np.sum(weights))
    if weight_sum <= 0:
        raise ValueError("Total weight must be positive")

    normalized = weights / weight_sum
    mean = np.einsum("n,nd->d", normalized, values)
    centered = values - mean
    sum_a2 = float(np.dot(normalized, normalized))
    denominator = 1.0 - sum_a2
    if denominator <= 0:
        raise ValueError("Effective sample size is not greater than one")
    covariance = np.einsum(
        "n,ni,nj->ij",
        normalized * normalized,
        centered,
        centered,
    ) / denominator
    covariance = 0.5 * (covariance + covariance.T)
    effective_events = 1.0 / sum_a2
    return mean, covariance, effective_events


def estimate_moments(sample: AnalyzerSample) -> MomentResult:
    estimands = event_estimands(sample.plus, sample.minus)
    mean, covariance, effective_events = weighted_mean_and_covariance_of_mean(
        estimands,
        sample.weights,
    )
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    return MomentResult(
        coefficient_vector=mean,
        covariance=covariance,
        standard_errors=standard_errors,
        effective_events=effective_events,
        weight_sum=float(np.sum(sample.weights)),
        events=len(sample.weights),
        convention_name=sample.convention_name,
        metadata=dict(sample.metadata),
    )


def _linear_row(terms: dict[str, float]) -> np.ndarray:
    row = np.zeros(15, dtype=float)
    for name, coefficient in terms.items():
        row[COEFFICIENT_INDEX[name]] = float(coefficient)
    return row


def linear_derived_transform() -> tuple[tuple[str, ...], np.ndarray]:
    names: list[str] = []
    rows: list[np.ndarray] = []

    for first, second in (("k", "r"), ("k", "n"), ("r", "n")):
        direct = f"C{first}{second}"
        transpose = f"C{second}{first}"
        definitions = {
            f"{direct}_plus_{transpose}": {direct: 1.0, transpose: 1.0},
            f"{direct}_minus_{transpose}": {direct: 1.0, transpose: -1.0},
            f"Csym_{first}{second}": {direct: 0.5, transpose: 0.5},
            f"Canti_{first}{second}": {direct: 0.5, transpose: -0.5},
        }
        for name, terms in definitions.items():
            names.append(name)
            rows.append(_linear_row(terms))

    marker_definitions = {
        "D_lc_1": {"Ckk": 1.0 / 3.0, "Crr": 1.0 / 3.0, "Cnn": 1.0 / 3.0},
        "D_lc_k": {"Ckk": 1.0 / 3.0, "Crr": -1.0 / 3.0, "Cnn": -1.0 / 3.0},
        "D_lc_r": {"Ckk": -1.0 / 3.0, "Crr": 1.0 / 3.0, "Cnn": -1.0 / 3.0},
        "D_lc_n": {"Ckk": -1.0 / 3.0, "Crr": -1.0 / 3.0, "Cnn": 1.0 / 3.0},
        "trace_C_over_3": {"Ckk": 1.0 / 3.0, "Crr": 1.0 / 3.0, "Cnn": 1.0 / 3.0},
        # This is the scalar used in CMS opening-angle formulas when C is in
        # the corresponding CMS sign convention.  It is kept namespaced to
        # prevent collision with D_lc_1.
        "D_cms_trace_if_same_C_labels": {
            "Ckk": -1.0 / 3.0,
            "Crr": -1.0 / 3.0,
            "Cnn": -1.0 / 3.0,
        },
    }
    for name, terms in marker_definitions.items():
        names.append(name)
        rows.append(_linear_row(terms))

    return tuple(names), np.vstack(rows)


def derive_linear_quantities(result: MomentResult) -> DerivedResult:
    names, transform = linear_derived_transform()
    values = transform @ result.coefficient_vector
    covariance = transform @ result.covariance @ transform.T
    covariance = 0.5 * (covariance + covariance.T)
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    return DerivedResult(names, values, covariance, standard_errors)


def derive_connected_correlation(result: MomentResult) -> DerivedResult:
    b1, b2, c = coefficient_vector_to_parts(result.coefficient_vector)
    connected = c - np.outer(b1, b2)

    names: list[str] = []
    jacobian_rows: list[np.ndarray] = []
    values: list[float] = []

    for i, first in enumerate(AXES):
        for j, second in enumerate(AXES):
            names.append(f"Cconn_{first}{second}")
            values.append(float(connected[i, j]))
            row = np.zeros(15, dtype=float)
            row[COEFFICIENT_INDEX[f"C{first}{second}"]] = 1.0
            row[COEFFICIENT_INDEX[f"B1{first}"]] = -b2[j]
            row[COEFFICIENT_INDEX[f"B2{second}"]] = -b1[i]
            jacobian_rows.append(row)

    jacobian = np.vstack(jacobian_rows)
    covariance = jacobian @ result.covariance @ jacobian.T
    covariance = 0.5 * (covariance + covariance.T)
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    return DerivedResult(
        tuple(names),
        np.asarray(values, dtype=float),
        covariance,
        standard_errors,
    )


def compare_independent(
    first: MomentResult,
    second: MomentResult,
    rcond: float = 1.0e-12,
) -> dict[str, Any]:
    delta = first.coefficient_vector - second.coefficient_vector
    covariance = first.covariance + second.covariance
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    z = np.divide(
        delta,
        standard_errors,
        out=np.full_like(delta, np.nan),
        where=standard_errors > 0,
    )
    inverse = np.linalg.pinv(covariance, rcond=rcond, hermitian=True)
    chi2 = float(delta @ inverse @ delta)
    rank = int(np.linalg.matrix_rank(covariance, tol=rcond))
    return {
        "delta": delta,
        "covariance": covariance,
        "standard_errors": standard_errors,
        "z": z,
        "max_abs_z": float(np.nanmax(np.abs(z))),
        "chi2": chi2,
        "ndof": rank,
    }


def estimate_paired_difference(
    first_estimands: np.ndarray,
    second_estimands: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if first_estimands.shape != second_estimands.shape:
        raise ValueError(
            f"Paired estimand shapes differ: {first_estimands.shape} vs {second_estimands.shape}"
        )
    difference = first_estimands - second_estimands
    mean, covariance, _ = weighted_mean_and_covariance_of_mean(difference, weights)
    return mean, covariance
