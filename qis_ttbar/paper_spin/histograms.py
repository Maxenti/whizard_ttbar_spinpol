"""Normalized angular distributions with full bin covariance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .contracts import AXES
from .io import AnalyzerSample
from .moments import weighted_mean_and_covariance_of_mean


@dataclass(frozen=True)
class HistogramResult:
    observable: str
    edges: np.ndarray
    centers: np.ndarray
    probabilities: np.ndarray
    probability_covariance: np.ndarray
    densities: np.ndarray
    density_covariance: np.ndarray
    underflow: int
    overflow: int
    events: int
    weight_sum: float
    metadata: dict[str, Any]


def angular_observables(sample: AnalyzerSample) -> dict[str, np.ndarray]:
    values: dict[str, np.ndarray] = {}
    for i, axis in enumerate(AXES):
        values[f"B1{axis}"] = sample.plus[:, i]
        values[f"B2{axis}"] = sample.minus[:, i]
    for i, first in enumerate(AXES):
        for j, second in enumerate(AXES):
            values[f"C{first}{second}"] = sample.plus[:, i] * sample.minus[:, j]
    for first, second in (("k", "r"), ("k", "n"), ("r", "n")):
        i, j = AXES.index(first), AXES.index(second)
        direct = sample.plus[:, i] * sample.minus[:, j]
        transpose = sample.plus[:, j] * sample.minus[:, i]
        values[f"xplus_{first}{second}"] = direct + transpose
        values[f"xminus_{first}{second}"] = direct - transpose
    values["cosphi_signed"] = np.einsum("ni,ni->n", sample.plus, sample.minus)
    return values


def normalized_histogram(
    observable: str,
    values: np.ndarray,
    weights: np.ndarray,
    edges: np.ndarray,
) -> HistogramResult:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    edges = np.asarray(edges, dtype=float)
    if len(edges) < 2 or not np.all(np.diff(edges) > 0.0):
        raise ValueError("Histogram edges must be strictly increasing")
    finite = np.isfinite(values) & np.isfinite(weights)
    values = values[finite]
    weights = weights[finite]
    if np.any(weights < 0.0):
        raise ValueError("Histogram covariance requires non-negative weights")

    bin_index = np.searchsorted(edges, values, side="right") - 1
    # Include an exact upper-edge value in the final bin.
    bin_index[values == edges[-1]] = len(edges) - 2
    underflow = int(np.count_nonzero(bin_index < 0))
    overflow = int(np.count_nonzero(bin_index >= len(edges) - 1))
    in_range = (bin_index >= 0) & (bin_index < len(edges) - 1)
    if not np.all(in_range):
        # The histogram explicitly reports excluded events. The normalization is
        # over in-range events, matching a normalized differential distribution
        # on the declared support.
        values = values[in_range]
        weights = weights[in_range]
        bin_index = bin_index[in_range]
    one_hot = np.eye(len(edges) - 1, dtype=float)[bin_index]
    probabilities, covariance, effective_events = weighted_mean_and_covariance_of_mean(
        one_hot,
        weights,
    )
    widths = np.diff(edges)
    scale = np.diag(1.0 / widths)
    density = probabilities / widths
    density_covariance = scale @ covariance @ scale
    return HistogramResult(
        observable=observable,
        edges=edges,
        centers=0.5 * (edges[:-1] + edges[1:]),
        probabilities=probabilities,
        probability_covariance=covariance,
        densities=density,
        density_covariance=density_covariance,
        underflow=underflow,
        overflow=overflow,
        events=int(len(values)),
        weight_sum=float(np.sum(weights)),
        metadata={
            "effective_events": float(effective_events),
            "normalization": "unit integral over declared support",
            "covariance": "full normalized-bin covariance from event one-hot estimands",
        },
    )


def default_edges(observable: str, bins: int = 20) -> np.ndarray:
    if observable.startswith("xplus_") or observable.startswith("xminus_"):
        return np.linspace(-2.0, 2.0, bins + 1)
    return np.linspace(-1.0, 1.0, bins + 1)
