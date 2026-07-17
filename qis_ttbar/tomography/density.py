from __future__ import annotations

import dataclasses
import itertools
import numpy as np


@dataclasses.dataclass(frozen=True)
class DensityValidation:
    hermiticity_error: float
    trace_error: float
    minimum_eigenvalue: float
    maximum_eigenvalue: float
    positive_semidefinite: bool
    valid: bool


def pauli_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return sx, sy, sz


def density_matrix_from_coefficients(
    b_plus: np.ndarray,
    b_minus: np.ndarray,
    correlation: np.ndarray,
) -> np.ndarray:
    b_plus = np.asarray(b_plus, dtype=float).reshape(3)
    b_minus = np.asarray(b_minus, dtype=float).reshape(3)
    correlation = np.asarray(correlation, dtype=float).reshape(3, 3)
    identity = np.eye(2, dtype=complex)
    sigma = pauli_matrices()
    rho = np.kron(identity, identity)
    for i in range(3):
        rho = rho + b_plus[i] * np.kron(sigma[i], identity)
        rho = rho + b_minus[i] * np.kron(identity, sigma[i])
    for i, j in itertools.product(range(3), repeat=2):
        rho = rho + correlation[i, j] * np.kron(sigma[i], sigma[j])
    return 0.25 * rho


def coefficients_from_density_matrix(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rho = np.asarray(rho, dtype=complex).reshape(4, 4)
    identity = np.eye(2, dtype=complex)
    sigma = pauli_matrices()
    b_plus = np.array([np.trace(rho @ np.kron(s, identity)).real for s in sigma])
    b_minus = np.array([np.trace(rho @ np.kron(identity, s)).real for s in sigma])
    correlation = np.array([
        [np.trace(rho @ np.kron(sigma[i], sigma[j])).real for j in range(3)]
        for i in range(3)
    ])
    return b_plus, b_minus, correlation


def validate_density_matrix(rho: np.ndarray, *, atol: float = 1e-10) -> DensityValidation:
    rho = np.asarray(rho, dtype=complex).reshape(4, 4)
    herm = float(np.linalg.norm(rho - rho.conj().T, ord="fro"))
    trace_error = float(abs(np.trace(rho) - 1.0))
    eigenvalues = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T)).real
    minimum, maximum = float(eigenvalues.min()), float(eigenvalues.max())
    psd = minimum >= -atol
    return DensityValidation(
        hermiticity_error=herm,
        trace_error=trace_error,
        minimum_eigenvalue=minimum,
        maximum_eigenvalue=maximum,
        positive_semidefinite=psd,
        valid=herm <= atol and trace_error <= atol and psd,
    )


def _simplex_projection(values: np.ndarray) -> np.ndarray:
    """Euclidean projection of real values onto the probability simplex."""
    values = np.asarray(values, dtype=float)
    sorted_values = np.sort(values)[::-1]
    cumulative = np.cumsum(sorted_values)
    candidates = sorted_values - (cumulative - 1.0) / np.arange(1, len(values) + 1)
    positive = np.nonzero(candidates > 0)[0]
    threshold = (cumulative[positive[-1]] - 1.0) / (positive[-1] + 1) if len(positive) else 0.0
    return np.maximum(values - threshold, 0.0)


def project_density_matrix(rho: np.ndarray) -> np.ndarray:
    """Nearest Hermitian PSD trace-one matrix in Frobenius norm."""
    hermitian = 0.5 * (np.asarray(rho, dtype=complex) + np.asarray(rho, dtype=complex).conj().T)
    eigenvalues, eigenvectors = np.linalg.eigh(hermitian)
    projected = _simplex_projection(eigenvalues.real)
    result = (eigenvectors * projected) @ eigenvectors.conj().T
    return 0.5 * (result + result.conj().T)


def partial_trace(rho: np.ndarray, keep: int) -> np.ndarray:
    """Trace a two-qubit density matrix over the other subsystem; keep=0 or 1."""
    tensor = np.asarray(rho, dtype=complex).reshape(2, 2, 2, 2)
    if keep == 0:
        return np.einsum("abcb->ac", tensor)
    if keep == 1:
        return np.einsum("abad->bd", tensor)
    raise ValueError("keep must be 0 or 1")


def partial_transpose(rho: np.ndarray, subsystem: int = 1) -> np.ndarray:
    tensor = np.asarray(rho, dtype=complex).reshape(2, 2, 2, 2)
    if subsystem == 0:
        return tensor.transpose(2, 1, 0, 3).reshape(4, 4)
    if subsystem == 1:
        return tensor.transpose(0, 3, 2, 1).reshape(4, 4)
    raise ValueError("subsystem must be 0 or 1")
