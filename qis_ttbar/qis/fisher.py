from __future__ import annotations

import numpy as np


def classical_fisher_information(probabilities: np.ndarray, derivatives: np.ndarray, *, floor: float = 1e-15) -> np.ndarray:
    """Fisher matrix for discrete probabilities and parameter derivatives.

    probabilities has shape (bins,), derivatives has shape (parameters,bins).
    """
    p = np.asarray(probabilities, float).reshape(-1)
    d = np.asarray(derivatives, float)
    if d.ndim == 1:
        d = d.reshape(1, -1)
    if d.shape[1] != len(p):
        raise ValueError("derivative bin dimension does not match probabilities")
    safe = np.maximum(p, floor)
    return np.einsum("ib,jb,b->ij", d, d, 1.0 / safe)


def quantum_fisher_information(rho: np.ndarray, derivatives: np.ndarray, *, eigenvalue_floor: float = 1e-12) -> np.ndarray:
    """Symmetric-logarithmic-derivative QFI matrix.

    derivatives has shape (parameters,4,4) and contains d rho / d theta.
    """
    rho = np.asarray(rho, complex).reshape(4, 4)
    derivatives = np.asarray(derivatives, complex)
    if derivatives.ndim == 2:
        derivatives = derivatives[None, :, :]
    values, vectors = np.linalg.eigh(0.5 * (rho + rho.conj().T))
    transformed = np.einsum("ai,pab,bj->pij", vectors.conj(), derivatives, vectors)
    n = derivatives.shape[0]
    result = np.zeros((n, n), float)
    for a in range(n):
        for b in range(n):
            total = 0.0
            for i in range(4):
                for j in range(4):
                    denominator = values[i] + values[j]
                    if denominator > eigenvalue_floor:
                        total += 2.0 * (transformed[a, i, j] * transformed[b, j, i]).real / denominator
            result[a, b] = total
    return 0.5 * (result + result.T)
