from __future__ import annotations

import numpy as np
from ..qis.measures import trace_distance, fidelity, bures_distance


def compare_states(rho: np.ndarray, sigma: np.ndarray) -> dict[str, float]:
    return {
        "trace_distance": trace_distance(rho, sigma),
        "fidelity": fidelity(rho, sigma),
        "bures_distance": bures_distance(rho, sigma),
        "frobenius_distance": float(np.linalg.norm(np.asarray(rho) - np.asarray(sigma), ord="fro")),
    }
