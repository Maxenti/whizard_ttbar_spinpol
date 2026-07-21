"""Physical unbinned likelihood fit of all 15 spin coefficients.

The fit uses the exact full-angular density for unit signed analyzers,

  p(a,b) = 1/(4pi)^2 [1 + B1.a + B2.b + a.C.b],

and parameterizes rho=T T^dagger / Tr(T T^dagger).  This guarantees a
Hermitian, positive-semidefinite, unit-trace density matrix throughout the
optimization.  It is therefore a simultaneous CMS-style full-matrix fit,
adapted to truth-level lepton-collider analyzers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize

from .contracts import SpinConvention, get_convention
from .density import (
    coefficients_from_density_matrix,
    density_matrix_from_coefficients,
    project_density_matrix,
    validate_density_matrix,
)
from .io import AnalyzerSample


@dataclass(frozen=True)
class ShapeFitResult:
    success: bool
    message: str
    objective: float
    iterations: int
    parameters: np.ndarray
    rho: np.ndarray
    coefficient_vector: np.ndarray
    parameter_covariance: np.ndarray | None
    coefficient_covariance: np.ndarray | None
    min_pdf_bracket: float
    metadata: dict[str, Any]


def params_to_cholesky(params: np.ndarray) -> np.ndarray:
    params = np.asarray(params, dtype=float)
    if params.shape != (15,):
        raise ValueError(f"Expected 15 fit parameters, got {params.shape}")
    t = np.zeros((4, 4), dtype=complex)
    t[0, 0] = 1.0
    t[1, 1] = np.exp(params[0])
    t[2, 2] = np.exp(params[1])
    t[3, 3] = np.exp(params[2])
    cursor = 3
    for row in range(1, 4):
        for column in range(row):
            t[row, column] = params[cursor] + 1.0j * params[cursor + 1]
            cursor += 2
    return t


def params_to_density(params: np.ndarray) -> np.ndarray:
    t = params_to_cholesky(params)
    rho = t @ t.conj().T
    trace = float(np.trace(rho).real)
    if not np.isfinite(trace) or trace <= 0.0:
        raise ValueError("Invalid Cholesky density trace")
    return rho / trace


def initial_params_from_density(rho: np.ndarray) -> np.ndarray:
    projection = project_density_matrix(rho)
    regularized = projection.rho + 1.0e-10 * np.eye(4)
    regularized /= np.trace(regularized).real
    t = np.linalg.cholesky(regularized)
    scale = abs(t[0, 0])
    if scale <= 1.0e-14:
        return np.zeros(15, dtype=float)
    t = t / scale
    params = np.zeros(15, dtype=float)
    params[0:3] = np.log(np.clip(np.real(np.diag(t)[1:]), 1.0e-14, None))
    cursor = 3
    for row in range(1, 4):
        for column in range(row):
            params[cursor] = float(t[row, column].real)
            params[cursor + 1] = float(t[row, column].imag)
            cursor += 2
    return params


def angular_pdf_bracket(
    plus: np.ndarray,
    minus: np.ndarray,
    coefficient_vector: np.ndarray,
) -> np.ndarray:
    plus = np.asarray(plus, dtype=float)
    minus = np.asarray(minus, dtype=float)
    coefficients = np.asarray(coefficient_vector, dtype=float)
    b1 = coefficients[0:3]
    b2 = coefficients[3:6]
    c = coefficients[6:15].reshape(3, 3)
    return (
        1.0
        + plus @ b1
        + minus @ b2
        + np.einsum("ni,ij,nj->n", plus, c, minus)
    )


def negative_log_likelihood(
    params: np.ndarray,
    plus: np.ndarray,
    minus: np.ndarray,
    weights: np.ndarray,
    convention: SpinConvention,
    pdf_floor: float,
) -> float:
    rho = params_to_density(params)
    coefficients = coefficients_from_density_matrix(rho, convention)
    bracket = angular_pdf_bracket(plus, minus, coefficients)
    if not np.all(np.isfinite(bracket)):
        return 1.0e100
    if np.any(bracket <= 0.0):
        # A physical rho should give nonnegative probabilities.  A smooth but
        # severe penalty protects the optimizer against numerical excursions.
        deficit = np.minimum(bracket, 0.0)
        return 1.0e50 + float(np.sum(deficit * deficit)) * 1.0e20
    return float(-np.dot(weights, np.log(np.maximum(bracket, pdf_floor))))


def finite_difference_hessian(
    function,
    point: np.ndarray,
    relative_step: float = 2.0e-4,
) -> np.ndarray:
    point = np.asarray(point, dtype=float)
    dimension = len(point)
    steps = relative_step * np.maximum(1.0, np.abs(point))
    hessian = np.zeros((dimension, dimension), dtype=float)
    f0 = float(function(point))
    for i in range(dimension):
        ei = np.zeros(dimension)
        ei[i] = steps[i]
        f_plus = float(function(point + ei))
        f_minus = float(function(point - ei))
        hessian[i, i] = (f_plus - 2.0 * f0 + f_minus) / (steps[i] ** 2)
        for j in range(i):
            ej = np.zeros(dimension)
            ej[j] = steps[j]
            value = (
                float(function(point + ei + ej))
                - float(function(point + ei - ej))
                - float(function(point - ei + ej))
                + float(function(point - ei - ej))
            ) / (4.0 * steps[i] * steps[j])
            hessian[i, j] = value
            hessian[j, i] = value
    return 0.5 * (hessian + hessian.T)


def finite_difference_jacobian_coefficients(
    point: np.ndarray,
    convention: SpinConvention,
    relative_step: float = 2.0e-5,
) -> np.ndarray:
    point = np.asarray(point, dtype=float)
    jacobian = np.zeros((15, 15), dtype=float)
    steps = relative_step * np.maximum(1.0, np.abs(point))
    for index in range(15):
        direction = np.zeros(15)
        direction[index] = steps[index]
        plus = coefficients_from_density_matrix(
            params_to_density(point + direction), convention
        )
        minus = coefficients_from_density_matrix(
            params_to_density(point - direction), convention
        )
        jacobian[:, index] = (plus - minus) / (2.0 * steps[index])
    return jacobian


def fit_physical_density_matrix(
    sample: AnalyzerSample,
    initial_coefficient_vector: np.ndarray | None = None,
    convention: SpinConvention | str = "lepton_collider_paper_v1",
    max_iterations: int = 2000,
    gradient_tolerance: float = 1.0e-8,
    pdf_floor: float = 1.0e-14,
    calculate_covariance: bool = True,
) -> ShapeFitResult:
    if isinstance(convention, str):
        convention = get_convention(convention)
    if initial_coefficient_vector is None:
        initial_params = np.zeros(15, dtype=float)
    else:
        initial_rho = density_matrix_from_coefficients(
            initial_coefficient_vector,
            convention,
        )
        initial_params = initial_params_from_density(initial_rho)

    objective = lambda params: negative_log_likelihood(
        params,
        sample.plus,
        sample.minus,
        sample.weights,
        convention,
        pdf_floor,
    )
    optimization = minimize(
        objective,
        initial_params,
        method="L-BFGS-B",
        options={
            "maxiter": int(max_iterations),
            "gtol": float(gradient_tolerance),
            "ftol": 1.0e-12,
            "maxls": 50,
        },
    )
    rho = params_to_density(optimization.x)
    coefficients = coefficients_from_density_matrix(rho, convention)
    bracket = angular_pdf_bracket(sample.plus, sample.minus, coefficients)
    parameter_covariance = None
    coefficient_covariance = None

    if calculate_covariance and optimization.success:
        hessian = finite_difference_hessian(objective, optimization.x)
        eigenvalues = np.linalg.eigvalsh(hessian)
        if float(eigenvalues.min()) > 0.0:
            parameter_covariance = np.linalg.inv(hessian)
        else:
            parameter_covariance = np.linalg.pinv(hessian, hermitian=True)
        jacobian = finite_difference_jacobian_coefficients(
            optimization.x,
            convention,
        )
        coefficient_covariance = (
            jacobian @ parameter_covariance @ jacobian.T
        )
        coefficient_covariance = 0.5 * (
            coefficient_covariance + coefficient_covariance.T
        )

    validation = validate_density_matrix(rho)
    return ShapeFitResult(
        success=bool(optimization.success and validation.valid),
        message=str(optimization.message),
        objective=float(optimization.fun),
        iterations=int(getattr(optimization, "nit", -1)),
        parameters=np.asarray(optimization.x, dtype=float),
        rho=rho,
        coefficient_vector=coefficients,
        parameter_covariance=parameter_covariance,
        coefficient_covariance=coefficient_covariance,
        min_pdf_bracket=float(np.min(bracket)),
        metadata={
            "optimizer_success": bool(optimization.success),
            "density_physical": bool(validation.valid),
            "density_min_eigenvalue": validation.min_eigenvalue,
            "pdf_floor": float(pdf_floor),
        },
    )
