from __future__ import annotations

import math
import numpy as np
from scipy.linalg import sqrtm

from ..tomography.density import partial_trace, partial_transpose, coefficients_from_density_matrix, pauli_matrices


def _eigenvalues(rho: np.ndarray) -> np.ndarray:
    values = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T)).real
    return np.clip(values, 0.0, None)


def von_neumann_entropy(rho: np.ndarray, base: float = 2.0) -> float:
    values = _eigenvalues(np.asarray(rho, complex))
    nonzero = values[values > 1e-15]
    return float(-np.sum(nonzero * np.log(nonzero)) / np.log(base))


def renyi_entropy(rho: np.ndarray, alpha: float = 2.0, base: float = 2.0) -> float:
    if alpha <= 0 or abs(alpha - 1.0) < 1e-12:
        raise ValueError("alpha must be positive and different from 1")
    values = _eigenvalues(rho)
    return float(np.log(np.sum(values**alpha)) / ((1.0 - alpha) * np.log(base)))


def purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


def concurrence(rho: np.ndarray) -> float:
    sy = pauli_matrices()[1]
    spin_flip = np.kron(sy, sy)
    transformed = rho @ spin_flip @ rho.conj() @ spin_flip
    eigenvalues = np.linalg.eigvals(transformed)
    roots = np.sort(np.sqrt(np.clip(eigenvalues.real, 0.0, None)))[::-1]
    return float(max(0.0, roots[0] - roots[1] - roots[2] - roots[3]))


def entanglement_of_formation(rho: np.ndarray) -> float:
    c = concurrence(rho)
    if c <= 0:
        return 0.0
    x = 0.5 * (1.0 + math.sqrt(max(0.0, 1.0 - c * c)))
    return float(-x * math.log2(x) - (1.0 - x) * math.log2(1.0 - x))


def negativity(rho: np.ndarray) -> float:
    values = np.linalg.eigvalsh(partial_transpose(rho)).real
    return float(np.sum(np.abs(values[values < 0.0])))


def logarithmic_negativity(rho: np.ndarray) -> float:
    return float(math.log2(2.0 * negativity(rho) + 1.0))


def mutual_information(rho: np.ndarray, base: float = 2.0) -> float:
    return float(von_neumann_entropy(partial_trace(rho, 0), base) + von_neumann_entropy(partial_trace(rho, 1), base) - von_neumann_entropy(rho, base))


def chsh_horodecki(rho: np.ndarray) -> float:
    _, _, c = coefficients_from_density_matrix(rho)
    eigenvalues = np.sort(np.linalg.eigvalsh(c.T @ c).real)[::-1]
    return float(2.0 * np.sqrt(max(0.0, eigenvalues[0] + eigenvalues[1])))


def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    singular = np.linalg.svd(rho - sigma, compute_uv=False)
    return float(0.5 * singular.sum())


def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    root = sqrtm(rho)
    product = root @ sigma @ root
    value = np.trace(sqrtm(product))
    return float(np.clip((value.real) ** 2, 0.0, 1.0))


def bures_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.sqrt(max(0.0, 2.0 - 2.0 * np.sqrt(fidelity(rho, sigma)))))


def l1_coherence(rho: np.ndarray) -> float:
    matrix = np.asarray(rho, complex)
    return float(np.sum(np.abs(matrix)) - np.sum(np.abs(np.diag(matrix))))


def correlation_singular_values(rho: np.ndarray) -> np.ndarray:
    return np.linalg.svd(coefficients_from_density_matrix(rho)[2], compute_uv=False)


def all_measures(rho: np.ndarray, *, entropy_base: float = 2.0) -> dict[str, float | list[float]]:
    rho = np.asarray(rho, dtype=complex).reshape(4, 4)
    values = np.linalg.eigvalsh(rho).real
    ppt_values = np.linalg.eigvalsh(partial_transpose(rho)).real
    top = partial_trace(rho, 0)
    antitop = partial_trace(rho, 1)
    singular = correlation_singular_values(rho)
    return {
        "purity": purity(rho),
        "von_neumann_entropy": von_neumann_entropy(rho, entropy_base),
        "top_entropy": von_neumann_entropy(top, entropy_base),
        "antitop_entropy": von_neumann_entropy(antitop, entropy_base),
        "mutual_information": mutual_information(rho, entropy_base),
        "concurrence": concurrence(rho),
        "entanglement_of_formation": entanglement_of_formation(rho),
        "negativity": negativity(rho),
        "logarithmic_negativity": logarithmic_negativity(rho),
        "chsh_max": chsh_horodecki(rho),
        "chsh_violation": max(0.0, chsh_horodecki(rho) - 2.0),
        "l1_coherence": l1_coherence(rho),
        "rho_min_eigenvalue": float(values.min()),
        "ppt_min_eigenvalue": float(ppt_values.min()),
        "ppt_entangled": bool(ppt_values.min() < -1e-10),
        "correlation_singular_values": singular.tolist(),
    }
