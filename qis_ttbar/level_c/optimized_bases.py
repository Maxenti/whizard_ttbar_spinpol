from __future__ import annotations

import dataclasses
import numpy as np


@dataclasses.dataclass(frozen=True)
class OptimizedBasis:
    top_rotation: np.ndarray
    antitop_rotation: np.ndarray
    diagonal_correlation: np.ndarray
    singular_values: np.ndarray


def _proper(rotation: np.ndarray) -> np.ndarray:
    result = np.asarray(rotation, float).copy()
    if np.linalg.det(result) < 0:
        result[:, -1] *= -1
    return result


def optimize_correlation_basis(correlation: np.ndarray) -> OptimizedBasis:
    c = np.asarray(correlation, float).reshape(3, 3)
    left, singular, right_t = np.linalg.svd(c)
    left, right = _proper(left), _proper(right_t.T)
    diagonal = left.T @ c @ right
    return OptimizedBasis(left.T, right.T, diagonal, singular)
