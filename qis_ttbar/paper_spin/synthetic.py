"""Synthetic physical states and coefficient-injection closure utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import coefficient_vector_to_parts, parts_to_coefficient_vector
from .density import (
    coefficients_from_density_matrix,
    density_matrix_from_coefficients,
    project_density_matrix,
    validate_density_matrix,
)
from .io import AnalyzerSample
from .moments import MomentResult, estimate_moments


@dataclass(frozen=True)
class SyntheticClosure:
    name: str
    injected: np.ndarray
    estimated: np.ndarray
    standard_errors: np.ndarray
    pulls: np.ndarray
    max_abs_pull: float
    events: int


def random_unit_vectors(rng: np.random.Generator, count: int) -> np.ndarray:
    vectors = rng.normal(size=(count, 3))
    norms = np.linalg.norm(vectors, axis=1)
    return vectors / norms[:, None]


def angular_bracket(
    plus: np.ndarray,
    minus: np.ndarray,
    coefficients: np.ndarray,
) -> np.ndarray:
    b1, b2, c = coefficient_vector_to_parts(coefficients)
    return (
        1.0
        + plus @ b1
        + minus @ b2
        + np.einsum("ni,ij,nj->n", plus, c, minus)
    )


def rejection_bound(coefficients: np.ndarray) -> float:
    b1, b2, c = coefficient_vector_to_parts(coefficients)
    return float(
        1.0
        + np.linalg.norm(b1)
        + np.linalg.norm(b2)
        + np.linalg.svd(c, compute_uv=False)[0]
        + 1.0e-12
    )


def sample_angular_density(
    coefficients: np.ndarray,
    events: int,
    seed: int,
    batch_size: int = 100_000,
) -> tuple[np.ndarray, np.ndarray]:
    coefficients = np.asarray(coefficients, dtype=float)
    rho = density_matrix_from_coefficients(coefficients)
    validation = validate_density_matrix(rho)
    if not validation.valid:
        raise ValueError(
            f"Injected coefficients do not define a physical density matrix: "
            f"min eigenvalue={validation.min_eigenvalue:.6g}"
        )

    rng = np.random.default_rng(seed)
    bound = rejection_bound(coefficients)
    accepted_plus: list[np.ndarray] = []
    accepted_minus: list[np.ndarray] = []
    total = 0

    while total < events:
        count = min(batch_size, max(batch_size // 4, 2 * (events - total)))
        plus = random_unit_vectors(rng, count)
        minus = random_unit_vectors(rng, count)
        bracket = angular_bracket(plus, minus, coefficients)
        if float(bracket.min()) < -1.0e-10:
            raise RuntimeError(
                f"Physical injected state produced negative angular density: "
                f"min bracket={bracket.min():.6g}"
            )
        probability = np.clip(bracket / bound, 0.0, 1.0)
        keep = rng.random(count) < probability
        if np.any(keep):
            accepted_plus.append(plus[keep])
            accepted_minus.append(minus[keep])
            total += int(np.count_nonzero(keep))

    plus_result = np.concatenate(accepted_plus, axis=0)[:events]
    minus_result = np.concatenate(accepted_minus, axis=0)[:events]
    return plus_result, minus_result


def synthetic_states() -> dict[str, np.ndarray]:
    states: dict[str, np.ndarray] = {}
    states["maximally_mixed"] = np.zeros(15, dtype=float)

    b1 = np.array([0.35, -0.20, 0.05])
    b2 = np.array([-0.25, 0.15, -0.05])
    states["product_polarized"] = parts_to_coefficient_vector(
        b1,
        b2,
        np.outer(b1, b2),
    )

    states["singlet"] = parts_to_coefficient_vector(
        np.zeros(3),
        np.zeros(3),
        -np.eye(3),
    )

    states["triplet_k"] = parts_to_coefficient_vector(
        np.zeros(3),
        np.zeros(3),
        np.diag([-1.0, 1.0, 1.0]),
    )

    # A populated but safely mixed state.  Build it from an arbitrary Hermitian
    # matrix and project exactly onto the physical density-matrix set.
    trial = parts_to_coefficient_vector(
        np.array([0.25, -0.12, 0.04]),
        np.array([-0.18, 0.08, -0.03]),
        np.array(
            [
                [-0.35, 0.10, 0.03],
                [-0.06, 0.20, -0.02],
                [0.01, 0.04, -0.15],
            ]
        ),
    )
    projected = project_density_matrix(density_matrix_from_coefficients(trial))
    states["mixed_off_diagonal"] = coefficients_from_density_matrix(projected.rho)
    return states


def run_moment_closure(
    name: str,
    coefficients: np.ndarray,
    events: int,
    seed: int,
) -> SyntheticClosure:
    plus, minus = sample_angular_density(coefficients, events, seed)
    sample = AnalyzerSample(
        plus=plus,
        minus=minus,
        weights=np.ones(events, dtype=float),
        event_keys=np.arange(events),
        source_path=Path(f"synthetic:{name}"),
        convention_name="lepton_collider_paper_v1",
        metadata={"synthetic_state": name},
    )
    result: MomentResult = estimate_moments(sample)
    delta = result.coefficient_vector - coefficients
    pulls = np.divide(
        delta,
        result.standard_errors,
        out=np.zeros_like(delta),
        where=result.standard_errors > 0.0,
    )
    return SyntheticClosure(
        name=name,
        injected=np.asarray(coefficients, dtype=float),
        estimated=result.coefficient_vector,
        standard_errors=result.standard_errors,
        pulls=pulls,
        max_abs_pull=float(np.max(np.abs(pulls))),
        events=events,
    )


def run_default_closure_suite(
    events: int = 200_000,
    seed: int = 20260721,
) -> list[SyntheticClosure]:
    closures: list[SyntheticClosure] = []
    for offset, (name, coefficients) in enumerate(synthetic_states().items()):
        closures.append(
            run_moment_closure(
                name,
                coefficients,
                events,
                seed + 1009 * offset,
            )
        )
    return closures
