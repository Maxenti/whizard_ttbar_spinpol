"""Contracts and named conventions for paper-grade ttbar spin tomography.

The canonical convention in this package follows the lepton-collider basis of
Maltoni, Severi, Tentori, and Vryonidou (arXiv:2404.08049):

  k_hat = top direction in the ttbar rest frame
  r_hat = (p_plus - k_hat cos(theta)) / sin(theta)
  n_hat = (p_plus x k_hat) / sin(theta)

where p_plus is the incoming positively charged lepton direction.

The charged-lepton analyzers are signed so that both have analyzing power +1:

  a_plus  =  direction(l+) in the top rest frame
  a_minus = -direction(l-) in the antitop rest frame

With these signed analyzers, the angular density is

  p(a_plus, a_minus) = 1/(4pi)^2 * [1 + B1.a_plus + B2.a_minus
                                      + a_plus.C.a_minus]

and the density matrix is

  rho = 1/4 [I x I + B1_i sigma_i x I + B2_j I x sigma_j
             + C_ij sigma_i x sigma_j].

This keeps the density-matrix convention and the event-level moment convention
identical.  The legacy baseline is preserved through an explicit adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np

AXES: Final[tuple[str, ...]] = ("k", "r", "n")
B1_NAMES: Final[tuple[str, ...]] = tuple(f"B1{axis}" for axis in AXES)
B2_NAMES: Final[tuple[str, ...]] = tuple(f"B2{axis}" for axis in AXES)
C_NAMES: Final[tuple[str, ...]] = tuple(
    f"C{first}{second}" for first in AXES for second in AXES
)
COEFFICIENT_NAMES: Final[tuple[str, ...]] = B1_NAMES + B2_NAMES + C_NAMES
COEFFICIENT_INDEX: Final[dict[str, int]] = {
    name: index for index, name in enumerate(COEFFICIENT_NAMES)
}


@dataclass(frozen=True)
class SpinConvention:
    """Complete convention metadata needed to interpret the 15 coefficients."""

    name: str
    description: str
    beam_reference: str
    top_axes_definition: str
    antitop_axes_definition: str
    plus_analyzer_sign: float
    minus_analyzer_sign: float
    kappa_plus: float
    kappa_minus_signed: float
    # Pauli operators are represented by vectors in a fixed right-handed
    # abstract Cartesian basis.  The lepton-collider paper axes are reflected:
    # k x r = -n.  We therefore represent k=z, r=x, n=-y.
    pauli_axis_vectors: dict[str, tuple[float, float, float]]

    def pauli_axis_vector(self, axis: str) -> np.ndarray:
        try:
            value = self.pauli_axis_vectors[axis]
        except KeyError as exc:
            raise ValueError(f"Unknown axis {axis!r}") from exc
        return np.asarray(value, dtype=float)


LEPTON_COLLIDER_PAPER_V1: Final[SpinConvention] = SpinConvention(
    name="lepton_collider_paper_v1",
    description=(
        "Incoming positive-lepton beam defines p_hat; k is the top direction; "
        "r=(p-k cos(theta))/sin(theta); n=(p x k)/sin(theta).  The antilepton "
        "analyzer is sign-flipped so both charged-lepton analyzers have kappa=+1."
    ),
    beam_reference="incoming_positive_lepton",
    top_axes_definition="Maltoni et al. Eq. (2.2)",
    antitop_axes_definition="same named spin axes as top in the ttbar frame",
    plus_analyzer_sign=+1.0,
    minus_analyzer_sign=-1.0,
    kappa_plus=1.0,
    kappa_minus_signed=1.0,
    pauli_axis_vectors={
        "k": (0.0, 0.0, 1.0),
        "r": (1.0, 0.0, 0.0),
        "n": (0.0, -1.0, 0.0),
    },
)

LEGACY_INTERNAL_V1: Final[SpinConvention] = SpinConvention(
    name="legacy_internal_v1",
    description=(
        "Compatibility convention for the existing Spin-15 ntuples: b1 is the "
        "positive-lepton direction, b2 is the raw negative-lepton direction, "
        "and cij=b1i*b2j.  This convention is retained only for exact baseline "
        "comparison and is not the publication convention."
    ),
    beam_reference="legacy_repo_definition",
    top_axes_definition="legacy_repo_definition",
    antitop_axes_definition="legacy_repo_definition",
    plus_analyzer_sign=+1.0,
    minus_analyzer_sign=+1.0,
    kappa_plus=1.0,
    kappa_minus_signed=-1.0,
    pauli_axis_vectors={
        "k": (0.0, 0.0, 1.0),
        "r": (1.0, 0.0, 0.0),
        "n": (0.0, 1.0, 0.0),
    },
)

CONVENTIONS: Final[dict[str, SpinConvention]] = {
    LEPTON_COLLIDER_PAPER_V1.name: LEPTON_COLLIDER_PAPER_V1,
    LEGACY_INTERNAL_V1.name: LEGACY_INTERNAL_V1,
}


def get_convention(name: str) -> SpinConvention:
    try:
        return CONVENTIONS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown spin convention {name!r}; available: {sorted(CONVENTIONS)}"
        ) from exc


def coefficient_vector_to_parts(
    vector: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.asarray(vector, dtype=float)
    if values.shape != (15,):
        raise ValueError(f"Expected coefficient vector shape (15,), got {values.shape}")
    b1 = values[0:3].copy()
    b2 = values[3:6].copy()
    c = values[6:15].reshape(3, 3).copy()
    return b1, b2, c


def parts_to_coefficient_vector(
    b1: np.ndarray,
    b2: np.ndarray,
    c: np.ndarray,
) -> np.ndarray:
    b1 = np.asarray(b1, dtype=float)
    b2 = np.asarray(b2, dtype=float)
    c = np.asarray(c, dtype=float)
    if b1.shape != (3,) or b2.shape != (3,) or c.shape != (3, 3):
        raise ValueError(
            f"Expected b1=(3,), b2=(3,), c=(3,3); got {b1.shape}, {b2.shape}, {c.shape}"
        )
    return np.concatenate([b1, b2, c.reshape(-1)])


def coefficient_dict(vector: np.ndarray) -> dict[str, float]:
    values = np.asarray(vector, dtype=float)
    if values.shape != (15,):
        raise ValueError(f"Expected shape (15,), got {values.shape}")
    return {
        name: float(value)
        for name, value in zip(COEFFICIENT_NAMES, values, strict=True)
    }
