"""Spin-density-matrix construction, validation, projection, and observables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .contracts import (
    AXES,
    SpinConvention,
    coefficient_vector_to_parts,
    get_convention,
    parts_to_coefficient_vector,
)

I2 = np.eye(2, dtype=complex)
SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
PAULI_CARTESIAN = np.stack([SIGMA_X, SIGMA_Y, SIGMA_Z])


@dataclass(frozen=True)
class DensityValidation:
    valid: bool
    hermitian_residual: float
    trace_residual: float
    min_eigenvalue: float
    max_eigenvalue: float
    eigenvalues: np.ndarray
    purity: float


@dataclass(frozen=True)
class PhysicalProjection:
    rho: np.ndarray
    frobenius_distance: float
    eigenvalues_before: np.ndarray
    eigenvalues_after: np.ndarray


def convention_axis_matrix(convention: SpinConvention) -> np.ndarray:
    """Rows are physical named-axis vectors in Cartesian Pauli coordinates."""

    matrix = np.vstack(
        [convention.pauli_axis_vector(axis) for axis in AXES]
    )
    if not np.allclose(matrix @ matrix.T, np.eye(3), atol=1.0e-12, rtol=0.0):
        raise ValueError(
            f"Convention {convention.name} Pauli-axis map is not orthogonal: {matrix}"
        )
    return matrix


def named_to_cartesian(
    b1: np.ndarray,
    b2: np.ndarray,
    c: np.ndarray,
    convention: SpinConvention,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q = convention_axis_matrix(convention)
    return q.T @ b1, q.T @ b2, q.T @ c @ q


def cartesian_to_named(
    b1_cart: np.ndarray,
    b2_cart: np.ndarray,
    c_cart: np.ndarray,
    convention: SpinConvention,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q = convention_axis_matrix(convention)
    return q @ b1_cart, q @ b2_cart, q @ c_cart @ q.T


def density_matrix_from_parts(
    b1: np.ndarray,
    b2: np.ndarray,
    c: np.ndarray,
    convention: SpinConvention | str = "lepton_collider_paper_v1",
) -> np.ndarray:
    if isinstance(convention, str):
        convention = get_convention(convention)
    b1 = np.asarray(b1, dtype=float)
    b2 = np.asarray(b2, dtype=float)
    c = np.asarray(c, dtype=float)
    if b1.shape != (3,) or b2.shape != (3,) or c.shape != (3, 3):
        raise ValueError(
            f"Expected b1=(3,), b2=(3,), c=(3,3); got {b1.shape}, {b2.shape}, {c.shape}"
        )
    b1_cart, b2_cart, c_cart = named_to_cartesian(b1, b2, c, convention)
    rho = np.kron(I2, I2).astype(complex)
    for index, sigma in enumerate(PAULI_CARTESIAN):
        rho += b1_cart[index] * np.kron(sigma, I2)
        rho += b2_cart[index] * np.kron(I2, sigma)
    for first, sigma_first in enumerate(PAULI_CARTESIAN):
        for second, sigma_second in enumerate(PAULI_CARTESIAN):
            rho += c_cart[first, second] * np.kron(sigma_first, sigma_second)
    rho *= 0.25
    return 0.5 * (rho + rho.conj().T)


def density_matrix_from_coefficients(
    vector: np.ndarray,
    convention: SpinConvention | str = "lepton_collider_paper_v1",
) -> np.ndarray:
    b1, b2, c = coefficient_vector_to_parts(vector)
    return density_matrix_from_parts(b1, b2, c, convention)


def coefficients_from_density_matrix(
    rho: np.ndarray,
    convention: SpinConvention | str = "lepton_collider_paper_v1",
) -> np.ndarray:
    if isinstance(convention, str):
        convention = get_convention(convention)
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError(f"Expected rho shape (4,4), got {rho.shape}")
    b1_cart = np.array(
        [np.trace(rho @ np.kron(sigma, I2)).real for sigma in PAULI_CARTESIAN]
    )
    b2_cart = np.array(
        [np.trace(rho @ np.kron(I2, sigma)).real for sigma in PAULI_CARTESIAN]
    )
    c_cart = np.empty((3, 3), dtype=float)
    for first, sigma_first in enumerate(PAULI_CARTESIAN):
        for second, sigma_second in enumerate(PAULI_CARTESIAN):
            c_cart[first, second] = np.trace(
                rho @ np.kron(sigma_first, sigma_second)
            ).real
    b1, b2, c = cartesian_to_named(b1_cart, b2_cart, c_cart, convention)
    return parts_to_coefficient_vector(b1, b2, c)


def validate_density_matrix(
    rho: np.ndarray,
    tolerance: float = 1.0e-10,
) -> DensityValidation:
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError(f"Expected rho shape (4,4), got {rho.shape}")
    hermitian_residual = float(np.linalg.norm(rho - rho.conj().T, ord="fro"))
    trace_residual = float(abs(np.trace(rho) - 1.0))
    hermitian = 0.5 * (rho + rho.conj().T)
    eigenvalues = np.linalg.eigvalsh(hermitian).real
    purity = float(np.trace(hermitian @ hermitian).real)
    valid = (
        hermitian_residual <= tolerance
        and trace_residual <= tolerance
        and float(eigenvalues.min()) >= -tolerance
    )
    return DensityValidation(
        valid=valid,
        hermitian_residual=hermitian_residual,
        trace_residual=trace_residual,
        min_eigenvalue=float(eigenvalues.min()),
        max_eigenvalue=float(eigenvalues.max()),
        eigenvalues=eigenvalues,
        purity=purity,
    )


def _project_vector_to_probability_simplex(values: np.ndarray) -> np.ndarray:
    """Euclidean projection onto {x>=0, sum x=1}."""

    values = np.asarray(values, dtype=float)
    sorted_values = np.sort(values)[::-1]
    cumulative = np.cumsum(sorted_values)
    indices = np.arange(1, len(values) + 1)
    condition = sorted_values - (cumulative - 1.0) / indices > 0
    if not np.any(condition):
        return np.full_like(values, 1.0 / len(values))
    rho_index = int(np.nonzero(condition)[0][-1])
    theta = (cumulative[rho_index] - 1.0) / (rho_index + 1)
    return np.maximum(values - theta, 0.0)


def project_density_matrix(rho: np.ndarray) -> PhysicalProjection:
    rho = np.asarray(rho, dtype=complex)
    hermitian = 0.5 * (rho + rho.conj().T)
    eigenvalues, eigenvectors = np.linalg.eigh(hermitian)
    projected_eigenvalues = _project_vector_to_probability_simplex(eigenvalues.real)
    projected = (
        eigenvectors
        @ np.diag(projected_eigenvalues.astype(complex))
        @ eigenvectors.conj().T
    )
    projected = 0.5 * (projected + projected.conj().T)
    distance = float(np.linalg.norm(projected - rho, ord="fro"))
    return PhysicalProjection(
        rho=projected,
        frobenius_distance=distance,
        eigenvalues_before=eigenvalues.real,
        eigenvalues_after=projected_eigenvalues,
    )


def partial_transpose(rho: np.ndarray, subsystem: int = 1) -> np.ndarray:
    rho = np.asarray(rho, dtype=complex).reshape(2, 2, 2, 2)
    if subsystem == 0:
        transposed = rho.transpose(2, 1, 0, 3)
    elif subsystem == 1:
        transposed = rho.transpose(0, 3, 2, 1)
    else:
        raise ValueError("subsystem must be 0 or 1")
    return transposed.reshape(4, 4)


def negativity(rho: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(partial_transpose(rho, subsystem=1)).real
    return float(np.sum(np.abs(eigenvalues[eigenvalues < 0.0])))


def concurrence(rho: np.ndarray) -> float:
    rho = np.asarray(rho, dtype=complex)
    spin_flip = np.kron(SIGMA_Y, SIGMA_Y)
    rho_tilde = spin_flip @ rho.conj() @ spin_flip
    eigenvalues = np.linalg.eigvals(rho @ rho_tilde)
    roots = np.sqrt(np.clip(eigenvalues.real, 0.0, None))
    roots = np.sort(roots)[::-1]
    return float(max(0.0, roots[0] - roots[1] - roots[2] - roots[3]))


def von_neumann_entropy(rho: np.ndarray, base: float = 2.0) -> float:
    eigenvalues = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T)).real
    positive = eigenvalues[eigenvalues > 0.0]
    return float(-np.sum(positive * np.log(positive) / np.log(base)))


def chsh_maximum(
    coefficient_vector: np.ndarray,
    convention: SpinConvention | str = "lepton_collider_paper_v1",
) -> float:
    if isinstance(convention, str):
        convention = get_convention(convention)
    _, _, c = coefficient_vector_to_parts(coefficient_vector)
    _, _, c_cart = named_to_cartesian(np.zeros(3), np.zeros(3), c, convention)
    eigenvalues = np.linalg.eigvalsh(c_cart.T @ c_cart).real
    two_largest = np.sort(eigenvalues)[-2:]
    return float(2.0 * np.sqrt(max(0.0, float(np.sum(two_largest)))))


def entanglement_markers(c: np.ndarray) -> dict[str, float]:
    c = np.asarray(c, dtype=float)
    if c.shape != (3, 3):
        raise ValueError(f"Expected C shape (3,3), got {c.shape}")
    ckk, crr, cnn = c[0, 0], c[1, 1], c[2, 2]
    markers = {
        "D_lc_1": float((ckk + crr + cnn) / 3.0),
        "D_lc_k": float((ckk - crr - cnn) / 3.0),
        "D_lc_r": float((-ckk + crr - cnn) / 3.0),
        "D_lc_n": float((-ckk - crr + cnn) / 3.0),
        "D_cms_trace_if_same_C_labels": float(-(ckk + crr + cnn) / 3.0),
    }
    markers["D_lc_min"] = min(
        markers["D_lc_1"],
        markers["D_lc_k"],
        markers["D_lc_r"],
        markers["D_lc_n"],
    )
    markers["D_lc_entanglement_sufficient"] = float(markers["D_lc_min"] < -1.0 / 3.0)
    return markers


def all_density_measures(
    rho: np.ndarray,
    convention: SpinConvention | str = "lepton_collider_paper_v1",
) -> dict[str, Any]:
    validation = validate_density_matrix(rho)
    coefficients = coefficients_from_density_matrix(rho, convention)
    _, _, c = coefficient_vector_to_parts(coefficients)
    partial_eigenvalues = np.linalg.eigvalsh(partial_transpose(rho)).real
    result: dict[str, Any] = {
        "physical": bool(validation.valid),
        "trace": float(np.trace(rho).real),
        "purity": float(np.trace(rho @ rho).real),
        "min_eigenvalue": validation.min_eigenvalue,
        "max_eigenvalue": validation.max_eigenvalue,
        "eigenvalues": validation.eigenvalues.tolist(),
        "partial_transpose_eigenvalues": partial_eigenvalues.tolist(),
        "partial_transpose_min_eigenvalue": float(partial_eigenvalues.min()),
        "negativity": negativity(rho),
        "concurrence": concurrence(rho),
        "von_neumann_entropy_bits": von_neumann_entropy(rho),
        "chsh_maximum": chsh_maximum(coefficients, convention),
    }
    result.update(entanglement_markers(c))
    return result
