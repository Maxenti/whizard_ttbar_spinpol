from __future__ import annotations

import dataclasses
import itertools
from collections.abc import Mapping, Sequence
import numpy as np


@dataclasses.dataclass(frozen=True)
class PolynomialReweighter:
    coefficient_names: tuple[str, ...]
    terms: tuple[tuple[int, ...], ...]
    event_coefficients: np.ndarray

    def weights(self, point: Mapping[str, float]) -> np.ndarray:
        values = np.array([float(point.get(name, 0.0)) for name in self.coefficient_names])
        monomials = np.array([np.prod(values[list(term)]) if term else 1.0 for term in self.terms])
        return self.event_coefficients @ monomials


def polynomial_terms(n_parameters: int, order: int = 2) -> tuple[tuple[int, ...], ...]:
    terms: list[tuple[int, ...]] = [()]
    for degree in range(1, order + 1):
        terms.extend(itertools.combinations_with_replacement(range(n_parameters), degree))
    return tuple(terms)


def design_matrix(points: Sequence[Mapping[str, float]], names: Sequence[str], order: int = 2) -> tuple[np.ndarray, tuple[tuple[int, ...], ...]]:
    terms = polynomial_terms(len(names), order)
    matrix = []
    for point in points:
        values = np.array([float(point.get(name, 0.0)) for name in names])
        matrix.append([np.prod(values[list(term)]) if term else 1.0 for term in terms])
    return np.asarray(matrix, float), terms


def fit_polynomial_weights(
    coefficient_names: Sequence[str],
    parameter_points: Sequence[Mapping[str, float]],
    event_weights: np.ndarray,
    *, order: int = 2, regularization: float = 1e-12,
) -> PolynomialReweighter:
    weights = np.asarray(event_weights, float)
    if weights.ndim != 2 or weights.shape[0] != len(parameter_points):
        raise ValueError("event_weights must have shape (points, events)")
    design, terms = design_matrix(parameter_points, coefficient_names, order)
    lhs = design.T @ design + regularization * np.eye(design.shape[1])
    coefficients = np.linalg.solve(lhs, design.T @ weights).T
    return PolynomialReweighter(tuple(coefficient_names), terms, coefficients)
