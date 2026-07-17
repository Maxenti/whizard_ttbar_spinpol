from __future__ import annotations

import dataclasses
from collections.abc import Sequence

import numpy as np

from .density import density_matrix_from_coefficients, project_density_matrix, validate_density_matrix


@dataclasses.dataclass(frozen=True)
class TomographyResult:
    basis_order: tuple[str, str, str]
    n_events: int
    effective_events: float
    weight_sum: float
    b_plus: np.ndarray
    b_minus: np.ndarray
    correlation: np.ndarray
    rho_raw: np.ndarray
    rho_physical: np.ndarray
    coefficient_vector: np.ndarray
    covariance: np.ndarray | None
    raw_valid: bool

    def as_serializable(self) -> dict[str, object]:
        return {
            "basis_order": list(self.basis_order), "n_events": self.n_events,
            "effective_events": self.effective_events, "weight_sum": self.weight_sum,
            "B_plus": self.b_plus.tolist(), "B_minus": self.b_minus.tolist(),
            "C": self.correlation.tolist(),
            "rho_raw_real": self.rho_raw.real.tolist(), "rho_raw_imag": self.rho_raw.imag.tolist(),
            "rho_physical_real": self.rho_physical.real.tolist(),
            "rho_physical_imag": self.rho_physical.imag.tolist(),
            "coefficient_vector": self.coefficient_vector.tolist(),
            "covariance": None if self.covariance is None else self.covariance.tolist(),
            "raw_valid": self.raw_valid,
        }


def coefficient_vector(b_plus: np.ndarray, b_minus: np.ndarray, correlation: np.ndarray) -> np.ndarray:
    return np.concatenate([np.asarray(b_plus).reshape(3), np.asarray(b_minus).reshape(3), np.asarray(correlation).reshape(9)])


def unpack_coefficient_vector(vector: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vector = np.asarray(vector, dtype=float).reshape(15)
    return vector[:3], vector[3:6], vector[6:].reshape(3, 3)


def estimate_moments(
    u_plus: np.ndarray,
    u_minus: np.ndarray,
    *,
    weights: np.ndarray | None = None,
    alpha_plus: float = 1.0,
    alpha_minus: float = 1.0,
    basis_order: Sequence[str] = ("k", "r", "n"),
    covariance: np.ndarray | None = None,
) -> TomographyResult:
    plus = np.asarray(u_plus, dtype=float)
    minus = np.asarray(u_minus, dtype=float)
    if plus.ndim != 2 or plus.shape[1] != 3 or minus.shape != plus.shape:
        raise ValueError("u_plus and u_minus must both have shape (N,3)")
    if alpha_plus == 0 or alpha_minus == 0:
        raise ValueError("spin analyzing powers must be nonzero")
    n = plus.shape[0]
    if n == 0:
        raise ValueError("cannot estimate tomography from zero events")
    w = np.ones(n, dtype=float) if weights is None else np.asarray(weights, dtype=float).reshape(n)
    if not np.all(np.isfinite(w)) or float(w.sum()) == 0.0:
        raise ValueError("weights must be finite with nonzero sum")
    normalized = w / w.sum()
    mean_plus = np.einsum("n,ni->i", normalized, plus)
    mean_minus = np.einsum("n,ni->i", normalized, minus)
    products = np.einsum("ni,nj->nij", plus, minus)
    mean_products = np.einsum("n,nij->ij", normalized, products)
    b_plus = 3.0 * mean_plus / alpha_plus
    b_minus = 3.0 * mean_minus / alpha_minus
    correlation = 9.0 * mean_products / (alpha_plus * alpha_minus)
    rho_raw = density_matrix_from_coefficients(b_plus, b_minus, correlation)
    rho_physical = project_density_matrix(rho_raw)
    effective = float(w.sum() ** 2 / np.square(w).sum())
    vector = coefficient_vector(b_plus, b_minus, correlation)
    return TomographyResult(
        basis_order=tuple(basis_order), n_events=n, effective_events=effective,
        weight_sum=float(w.sum()), b_plus=b_plus, b_minus=b_minus,
        correlation=correlation, rho_raw=rho_raw, rho_physical=rho_physical,
        coefficient_vector=vector, covariance=covariance,
        raw_valid=validate_density_matrix(rho_raw).valid,
    )
