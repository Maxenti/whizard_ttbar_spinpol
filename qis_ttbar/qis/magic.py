from __future__ import annotations

import itertools
import numpy as np

from ..tomography.density import pauli_matrices


def stabilizer_renyi2_magic(rho: np.ndarray, *, floor: float = 1e-15) -> float:
    """Two-qubit stabilizer Rényi-2 magic diagnostic.

    Uses M2 = -log2[(1/d) sum_P |Tr(rho P)|^4 / Tr(rho^2)^2].
    It is zero for pure stabilizer states and positive for generic pure magic
    states; mixed-state interpretation must be documented with the analysis.
    """
    rho = np.asarray(rho, complex).reshape(4, 4)
    paulis = (np.eye(2, dtype=complex),) + pauli_matrices()
    moments = []
    for left, right in itertools.product(paulis, repeat=2):
        moments.append(abs(np.trace(rho @ np.kron(left, right))) ** 4)
    purity = float(np.trace(rho @ rho).real)
    normalized = max(float(np.sum(moments)) / 4.0 / max(purity * purity, floor), floor)
    return float(-np.log2(normalized))
