"""CMS-style one-dimensional likelihood extraction from angular observables.

For the canonical signed analyzers the exact full-phase-space marginals are

  f(a_i; B1_i) = 1/2 (1 + B1_i a_i),
  f(b_j; B2_j) = 1/2 (1 + B2_j b_j),
  f(x=a_i b_j; C_ij) = -1/2 log|x| (1 + C_ij x),
  f(cos(phi); D1) = 1/2 (1 + D1 cos(phi)),

where D1=Tr(C)/3 and cos(phi)=a_plus dot a_minus.  Terms independent
of the fitted coefficient are omitted from the likelihood.  The estimators are
therefore shape fits, not moment substitutions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize_scalar

from .contracts import AXES, COEFFICIENT_NAMES, parts_to_coefficient_vector
from .io import AnalyzerSample


@dataclass(frozen=True)
class ScalarFit:
    value: float
    standard_error: float
    objective: float
    success: bool
    boundary_distance: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class MarginalFitResult:
    coefficient_vector: np.ndarray
    covariance_diagonal_only: np.ndarray
    standard_errors: np.ndarray
    scalar_fits: dict[str, ScalarFit]
    trace_fit: ScalarFit
    metadata: dict[str, Any]


def fit_linear_shape(
    values: np.ndarray,
    weights: np.ndarray,
    bound: float = 1.0 - 1.0e-9,
) -> ScalarFit:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    finite = np.isfinite(values) & np.isfinite(weights)
    values = values[finite]
    weights = weights[finite]
    if len(values) < 2 or np.sum(weights) <= 0.0:
        raise ValueError("Insufficient finite positive-weight entries")
    if np.any(weights < 0.0):
        raise ValueError("Shape likelihood requires non-negative weights")
    if np.max(np.abs(values)) > 1.0 + 1.0e-10:
        raise ValueError("Angular fit variable lies outside [-1,1]")

    def objective(parameter: float) -> float:
        bracket = 1.0 + parameter * values
        if np.any(bracket <= 0.0):
            return float("inf")
        return float(-np.sum(weights * np.log(bracket)))

    optimization = minimize_scalar(
        objective,
        bounds=(-bound, bound),
        method="bounded",
        options={"xatol": 1.0e-12, "maxiter": 1000},
    )
    value = float(optimization.x)
    bracket = 1.0 + value * values
    hessian = float(np.sum(weights * values * values / (bracket * bracket)))
    standard_error = float(1.0 / np.sqrt(hessian)) if hessian > 0.0 else float("nan")
    return ScalarFit(
        value=value,
        standard_error=standard_error,
        objective=float(optimization.fun),
        success=bool(optimization.success and np.isfinite(standard_error)),
        boundary_distance=float(bound - abs(value)),
        metadata={
            "events": int(len(values)),
            "weight_sum": float(np.sum(weights)),
            "likelihood_term": "sum w log(1 + parameter*x)",
        },
    )


def fit_marginal_coefficients(sample: AnalyzerSample) -> MarginalFitResult:
    b1 = np.zeros(3)
    b2 = np.zeros(3)
    c = np.zeros((3, 3))
    errors = np.zeros(15)
    scalar_fits: dict[str, ScalarFit] = {}

    for index, axis in enumerate(AXES):
        name = f"B1{axis}"
        fit = fit_linear_shape(sample.plus[:, index], sample.weights)
        b1[index] = fit.value
        errors[COEFFICIENT_NAMES.index(name)] = fit.standard_error
        scalar_fits[name] = fit

    for index, axis in enumerate(AXES):
        name = f"B2{axis}"
        fit = fit_linear_shape(sample.minus[:, index], sample.weights)
        b2[index] = fit.value
        errors[COEFFICIENT_NAMES.index(name)] = fit.standard_error
        scalar_fits[name] = fit

    for first, axis_first in enumerate(AXES):
        for second, axis_second in enumerate(AXES):
            name = f"C{axis_first}{axis_second}"
            fit = fit_linear_shape(
                sample.plus[:, first] * sample.minus[:, second],
                sample.weights,
            )
            c[first, second] = fit.value
            errors[COEFFICIENT_NAMES.index(name)] = fit.standard_error
            scalar_fits[name] = fit

    trace_fit = fit_linear_shape(
        np.einsum("ni,ni->n", sample.plus, sample.minus),
        sample.weights,
    )
    vector = parts_to_coefficient_vector(b1, b2, c)
    covariance = np.diag(errors * errors)
    return MarginalFitResult(
        coefficient_vector=vector,
        covariance_diagonal_only=covariance,
        standard_errors=errors,
        scalar_fits=scalar_fits,
        trace_fit=trace_fit,
        metadata={
            "important_covariance_note": (
                "The one-dimensional marginal fits share events and are correlated. "
                "Use joint event bootstrap or the simultaneous angular likelihood for "
                "a full covariance; this diagonal matrix is not a 15D covariance."
            ),
            "D_lc_1_from_opening_angle": trace_fit.value,
        },
    )
