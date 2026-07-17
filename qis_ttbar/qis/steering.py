from __future__ import annotations

import numpy as np

from ..tomography.density import coefficients_from_density_matrix


def linear_three_setting_steering(rho: np.ndarray) -> dict[str, float | bool]:
    """CJWR-type three-setting linear steering diagnostic from C.

    S3 = sqrt(Tr(C^T C)); S3>1 violates the normalized three-setting bound.
    The returned quantity is a witness/diagnostic, not a full steering monotone.
    """
    correlation = coefficients_from_density_matrix(np.asarray(rho, complex))[2]
    value = float(np.sqrt(np.trace(correlation.T @ correlation).real))
    return {"steering_S3": value, "steering_violation": max(0.0, value - 1.0), "steerable_by_S3": value > 1.0 + 1e-10}
