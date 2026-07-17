from __future__ import annotations

import dataclasses
import numpy as np

from .estimators import TomographyResult, estimate_moments


@dataclasses.dataclass(frozen=True)
class BootstrapResult:
    central: TomographyResult
    replicas: np.ndarray
    covariance: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    seed: int


def bootstrap_tomography(
    u_plus: np.ndarray,
    u_minus: np.ndarray,
    *,
    weights: np.ndarray | None = None,
    replicas: int = 1000,
    seed: int = 730001,
    confidence_level: float = 0.68,
    alpha_plus: float = 1.0,
    alpha_minus: float = 1.0,
    basis_order: tuple[str, str, str] = ("k", "r", "n"),
) -> BootstrapResult:
    if replicas < 2:
        raise ValueError("replicas must be at least 2")
    plus = np.asarray(u_plus, dtype=float)
    minus = np.asarray(u_minus, dtype=float)
    n = len(plus)
    w = None if weights is None else np.asarray(weights, dtype=float)
    central = estimate_moments(
        plus, minus, weights=w, alpha_plus=alpha_plus, alpha_minus=alpha_minus, basis_order=basis_order
    )
    rng = np.random.default_rng(seed)
    result = np.empty((replicas, 15), dtype=float)
    probability = None
    if w is not None and np.all(w >= 0) and w.sum() > 0:
        probability = w / w.sum()
    for index in range(replicas):
        selected = rng.choice(n, size=n, replace=True, p=probability)
        replica_weights = None if w is None or probability is not None else w[selected]
        result[index] = estimate_moments(
            plus[selected], minus[selected], weights=replica_weights,
            alpha_plus=alpha_plus, alpha_minus=alpha_minus, basis_order=basis_order,
        ).coefficient_vector
    covariance = np.cov(result, rowvar=False, ddof=1)
    tail = 0.5 * (1.0 - confidence_level)
    lower = np.quantile(result, tail, axis=0)
    upper = np.quantile(result, 1.0 - tail, axis=0)
    central = dataclasses.replace(central, covariance=covariance)
    return BootstrapResult(central=central, replicas=result, covariance=covariance, lower=lower, upper=upper, seed=seed)
