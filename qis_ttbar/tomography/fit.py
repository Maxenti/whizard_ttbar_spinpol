from __future__ import annotations

import dataclasses
import numpy as np
from scipy.optimize import minimize

from .density import coefficients_from_density_matrix, project_density_matrix


@dataclasses.dataclass(frozen=True)
class PhysicalFitResult:
    rho: np.ndarray
    b_plus: np.ndarray
    b_minus: np.ndarray
    correlation: np.ndarray
    success: bool
    objective: float
    iterations: int
    message: str


def _rho_from_parameters(parameters: np.ndarray) -> np.ndarray:
    p = np.asarray(parameters, dtype=float).reshape(16)
    # Keep the Cholesky parameterization numerically finite even when an
    # optimizer probes a very poor direction. The external minimizer uses the
    # same bounds; clipping is a final defensive layer for direct calls.
    diagonal = np.exp(np.clip(p[:4], -30.0, 30.0))
    lower = np.zeros((4, 4), dtype=complex)
    lower[np.diag_indices(4)] = diagonal
    cursor = 4
    for row in range(1, 4):
        for column in range(row):
            lower[row, column] = p[cursor] + 1j * p[cursor + 1]
            cursor += 2
    rho = lower @ lower.conj().T
    trace = float(np.trace(rho).real)
    if not np.isfinite(trace) or trace <= 0.0 or not np.all(np.isfinite(rho)):
        return np.eye(4, dtype=complex) / 4.0
    return rho / trace


def _initial_parameters(rho: np.ndarray) -> np.ndarray:
    physical = project_density_matrix(rho) + 1e-10 * np.eye(4)
    physical /= np.trace(physical)
    lower = np.linalg.cholesky(physical)
    values = [float(np.log(max(lower[i, i].real, 1e-12))) for i in range(4)]
    for row in range(1, 4):
        for column in range(row):
            values.extend([float(lower[row, column].real), float(lower[row, column].imag)])
    return np.asarray(values)


def fit_physical_density_matrix(
    target_rho: np.ndarray,
    *,
    target_coefficients: np.ndarray | None = None,
    covariance: np.ndarray | None = None,
    max_iterations: int = 2000,
) -> PhysicalFitResult:
    target_rho = np.asarray(target_rho, dtype=complex).reshape(4, 4)
    if target_coefficients is None:
        bp, bm, c = coefficients_from_density_matrix(target_rho)
        target_coefficients = np.concatenate([bp, bm, c.reshape(9)])
    target_coefficients = np.asarray(target_coefficients, dtype=float).reshape(15)
    if covariance is None:
        inverse = np.eye(15)
    else:
        inverse = np.linalg.pinv(np.asarray(covariance, dtype=float).reshape(15, 15), hermitian=True)

    def objective(parameters: np.ndarray) -> float:
        rho = _rho_from_parameters(parameters)
        bp, bm, c = coefficients_from_density_matrix(rho)
        residual = np.concatenate([bp, bm, c.reshape(9)]) - target_coefficients
        value = float(residual @ inverse @ residual)
        return value if np.isfinite(value) else 1.0e100

    bounds = [(-30.0, 30.0)] * 4 + [(-10.0, 10.0)] * 12
    result = minimize(
        objective, _initial_parameters(target_rho), method="L-BFGS-B", bounds=bounds,
        options={"maxiter": max_iterations, "ftol": 1e-12, "gtol": 1e-9, "maxls": 50},
    )
    rho = _rho_from_parameters(result.x)
    bp, bm, c = coefficients_from_density_matrix(rho)
    return PhysicalFitResult(
        rho=rho, b_plus=bp, b_minus=bm, correlation=c,
        success=bool(result.success), objective=float(result.fun),
        iterations=int(result.nit), message=str(result.message),
    )
