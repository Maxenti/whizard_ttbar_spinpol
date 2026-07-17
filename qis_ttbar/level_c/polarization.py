from __future__ import annotations

import dataclasses
import math
from collections.abc import Mapping

import numpy as np

from ..tomography.density import validate_density_matrix


@dataclasses.dataclass(frozen=True)
class HelicityMixture:
    """Incoherent fractions in negative-lepton/positive-antilepton order."""

    lr: float
    rl: float
    ll: float
    rr: float

    def as_dict(self) -> dict[str, float]:
        return dataclasses.asdict(self)

    def validate(self, *, atol: float = 1e-12) -> None:
        values = np.asarray([self.lr, self.rl, self.ll, self.rr], dtype=float)
        if np.any(values < -atol) or abs(float(values.sum()) - 1.0) > atol:
            raise ValueError(f"invalid helicity mixture: {self}")


@dataclasses.dataclass(frozen=True)
class PolarizedStateMixture:
    rho: np.ndarray
    cross_section: float
    component_yields: dict[str, float]
    fractions_after_cross_section: dict[str, float]


def longitudinal_mixture_weights(p_minus: float, p_plus: float) -> HelicityMixture:
    """Return beam-population fractions for arbitrary longitudinal polarization.

    `+1` denotes right-handed and `-1` left-handed for each beam particle.
    These are population probabilities before the helicity-dependent hard
    cross sections are applied.
    """
    if not -1 <= p_minus <= 1 or not -1 <= p_plus <= 1:
        raise ValueError("polarizations must lie in [-1,1]")
    left_minus, right_minus = (1 - p_minus) / 2, (1 + p_minus) / 2
    left_plus, right_plus = (1 - p_plus) / 2, (1 + p_plus) / 2
    result = HelicityMixture(
        lr=left_minus * right_plus,
        rl=right_minus * left_plus,
        ll=left_minus * left_plus,
        rr=right_minus * right_plus,
    )
    result.validate()
    return result


def beam_spin_density_matrix(
    *,
    longitudinal: float = 0.0,
    transverse: float = 0.0,
    azimuth: float = 0.0,
) -> np.ndarray:
    """Construct a physical one-beam helicity density matrix.

    The Bloch vector is `(P_T cos(phi), P_T sin(phi), P_L)`.  Physicality
    requires `P_L^2 + P_T^2 <= 1`.
    """
    if longitudinal * longitudinal + transverse * transverse > 1.0 + 1e-12:
        raise ValueError("beam polarization vector magnitude exceeds one")
    if transverse < 0:
        raise ValueError("transverse polarization magnitude must be nonnegative")
    px = transverse * math.cos(azimuth)
    py = transverse * math.sin(azimuth)
    pz = longitudinal
    return 0.5 * np.array([[1 + pz, px - 1j * py], [px + 1j * py, 1 - pz]], dtype=complex)


def mix_helicity_density_matrices(
    states: Mapping[str, np.ndarray],
    cross_sections: Mapping[str, float],
    *,
    p_minus: float,
    p_plus: float,
    allowed_missing_zero_rate: bool = True,
) -> PolarizedStateMixture:
    """Build a partially polarized final-state density matrix from basis samples.

    Component populations are multiplied by their helicity cross sections
    before density matrices are averaged.  This is an incoherent longitudinal
    mixture and must not be used for transverse polarization.
    """
    mixture = longitudinal_mixture_weights(p_minus, p_plus).as_dict()
    component_yields: dict[str, float] = {}
    accumulator = np.zeros((4, 4), dtype=complex)
    total = 0.0
    for key, population in mixture.items():
        sigma = float(cross_sections.get(key, 0.0))
        if sigma < 0 or not np.isfinite(sigma):
            raise ValueError(f"invalid cross section for {key}: {sigma}")
        yield_weight = population * sigma
        component_yields[key] = yield_weight
        if yield_weight == 0.0:
            continue
        if key not in states:
            if allowed_missing_zero_rate and sigma == 0.0:
                continue
            raise KeyError(f"missing density matrix for nonzero {key} contribution")
        rho = np.asarray(states[key], dtype=complex).reshape(4, 4)
        validation = validate_density_matrix(rho)
        if not validation.valid:
            raise ValueError(f"unphysical density matrix for {key}: {validation}")
        accumulator += yield_weight * rho
        total += yield_weight
    if total <= 0:
        raise ValueError("polarization mixture has zero total cross section")
    rho = accumulator / total
    fractions = {key: value / total for key, value in component_yields.items()}
    return PolarizedStateMixture(
        rho=rho,
        cross_section=total,
        component_yields=component_yields,
        fractions_after_cross_section=fractions,
    )


def validate_transverse_polarization_request(
    transverse_minus: float,
    transverse_plus: float,
    relative_azimuth: float,
    *,
    longitudinal_minus: float = 0.0,
    longitudinal_plus: float = 0.0,
) -> dict[str, object]:
    minus = beam_spin_density_matrix(
        longitudinal=longitudinal_minus,
        transverse=transverse_minus,
        azimuth=0.0,
    )
    plus = beam_spin_density_matrix(
        longitudinal=longitudinal_plus,
        transverse=transverse_plus,
        azimuth=relative_azimuth,
    )
    requires_coherence = transverse_minus > 0 or transverse_plus > 0
    return {
        "requires_direct_whizard_generation": requires_coherence,
        "cannot_be_built_from_incoherent_LR_RL_samples": requires_coherence,
        "relative_azimuth": float(relative_azimuth),
        "minus_density_matrix_real": minus.real.tolist(),
        "minus_density_matrix_imag": minus.imag.tolist(),
        "plus_density_matrix_real": plus.real.tolist(),
        "plus_density_matrix_imag": plus.imag.tolist(),
    }
