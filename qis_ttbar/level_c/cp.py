from __future__ import annotations

import numpy as np


def antisymmetric_correlation(correlation: np.ndarray) -> np.ndarray:
    c = np.asarray(correlation, float).reshape(3, 3)
    return 0.5 * (c - c.T)


def cp_observables(correlation: np.ndarray, event_triple_products: np.ndarray | None = None, weights: np.ndarray | None = None) -> dict[str, float]:
    c = np.asarray(correlation, float).reshape(3, 3)
    output = {
        "C_rn_minus_C_nr": float(c[1, 2] - c[2, 1]),
        "C_kn_minus_C_nk": float(c[0, 2] - c[2, 0]),
        "C_kr_minus_C_rk": float(c[0, 1] - c[1, 0]),
        "antisymmetric_norm": float(np.linalg.norm(antisymmetric_correlation(c), ord="fro")),
    }
    if event_triple_products is not None:
        values = np.asarray(event_triple_products, float)
        w = np.ones(len(values)) if weights is None else np.asarray(weights, float)
        output["triple_product_mean"] = float(np.average(values, weights=w))
        output["triple_product_sign_asymmetry"] = float(np.average(np.sign(values), weights=w))
    return output
