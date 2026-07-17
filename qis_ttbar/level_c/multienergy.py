from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd

from ..tomography.density import validate_density_matrix


@dataclasses.dataclass(frozen=True)
class CombinedEnergyState:
    rho: np.ndarray
    total_expected_events: float
    normalized_weights: dict[float, float]
    covariance: np.ndarray | None


def combine_energy_points(
    frames: Mapping[float, pd.DataFrame],
    *,
    energy_column: str = "sqrt_s_nominal_GeV",
) -> pd.DataFrame:
    output = []
    for energy, frame in sorted(frames.items()):
        copy = frame.copy()
        copy[energy_column] = float(energy)
        output.append(copy)
    if not output:
        raise ValueError("no energy points supplied")
    return pd.concat(output, ignore_index=True)


def combine_density_matrices(
    states: Mapping[float, np.ndarray],
    *,
    cross_sections: Mapping[float, float],
    luminosities: Mapping[float, float],
    efficiencies: Mapping[float, float] | None = None,
    covariances: Mapping[float, np.ndarray] | None = None,
) -> CombinedEnergyState:
    """Combine states using expected selected yields `L * sigma * efficiency`."""
    efficiencies = efficiencies or {}
    weighted = np.zeros((4, 4), dtype=complex)
    yields: dict[float, float] = {}
    for energy, state in states.items():
        rho = np.asarray(state, complex).reshape(4, 4)
        validation = validate_density_matrix(rho)
        if not validation.valid:
            raise ValueError(f"unphysical state at {energy}: {validation}")
        sigma = float(cross_sections[energy])
        luminosity = float(luminosities[energy])
        efficiency = float(efficiencies.get(energy, 1.0))
        if sigma < 0 or luminosity < 0 or not 0 <= efficiency <= 1:
            raise ValueError(f"invalid yield inputs at {energy}")
        expected = sigma * luminosity * efficiency
        yields[float(energy)] = expected
        weighted += expected * rho
    total = sum(yields.values())
    if total <= 0:
        raise ValueError("combined expected yield is zero")
    normalized = {energy: value / total for energy, value in yields.items()}
    covariance = None
    if covariances is not None:
        covariance = np.zeros((15, 15), dtype=float)
        for energy, fraction in normalized.items():
            if energy in covariances:
                covariance += fraction * fraction * np.asarray(covariances[energy], float).reshape(15, 15)
    return CombinedEnergyState(weighted / total, total, normalized, covariance)
