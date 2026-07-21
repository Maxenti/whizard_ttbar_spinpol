"""Independent Lorentz reconstruction of the lepton-collider k,r,n analyzers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BasisAuditResult:
    plus: np.ndarray
    minus: np.ndarray
    singular: np.ndarray
    orthonormal_residual: np.ndarray
    handedness: np.ndarray
    metadata: dict[str, Any]


def boost_four_vectors(vectors: np.ndarray, beta: np.ndarray) -> np.ndarray:
    """Apply active Lorentz boosts with possibly event-dependent beta.

    Input vectors use `(E,px,py,pz)`. To transform a vector into the rest frame
    of a parent with velocity `parent_beta`, pass `beta=-parent_beta`.
    """

    vectors = np.asarray(vectors, dtype=float)
    beta = np.asarray(beta, dtype=float)
    if vectors.shape[-1] != 4 or beta.shape[-1] != 3:
        raise ValueError("Expected vectors (...,4) and beta (...,3)")
    beta2 = np.sum(beta * beta, axis=-1)
    if np.any(beta2 >= 1.0):
        raise ValueError("Superluminal boost")
    gamma = 1.0 / np.sqrt(1.0 - beta2)
    spatial = vectors[..., 1:]
    energy = vectors[..., 0]
    beta_dot_p = np.sum(beta * spatial, axis=-1)
    factor = np.zeros_like(beta_dot_p)
    nonzero = beta2 > 0.0
    factor[nonzero] = (
        (gamma[nonzero] - 1.0) * beta_dot_p[nonzero] / beta2[nonzero]
        + gamma[nonzero] * energy[nonzero]
    )
    spatial_prime = spatial + factor[..., None] * beta
    energy_prime = gamma * (energy + beta_dot_p)
    return np.concatenate([energy_prime[..., None], spatial_prime], axis=-1)


def unit(vectors: np.ndarray, tolerance: float = 1.0e-15) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=float)
    norm = np.linalg.norm(vectors, axis=-1)
    if np.any(norm <= tolerance):
        raise ValueError("Cannot normalize zero spatial vector")
    return vectors / norm[..., None]


def reconstruct_analyzers(
    incoming_positive: np.ndarray,
    top: np.ndarray,
    antitop: np.ndarray,
    lepton_positive: np.ndarray,
    lepton_negative: np.ndarray,
    singular_tolerance: float = 1.0e-10,
) -> BasisAuditResult:
    arrays = [
        np.asarray(value, dtype=float)
        for value in (incoming_positive, top, antitop, lepton_positive, lepton_negative)
    ]
    if len({array.shape for array in arrays}) != 1 or arrays[0].ndim != 2 or arrays[0].shape[1] != 4:
        raise ValueError("All four-vector arrays must have identical shape (N,4)")

    incoming_positive, top, antitop, lepton_positive, lepton_negative = arrays
    total = top + antitop
    ttbar_beta = total[:, 1:] / total[:, 0, None]
    boost_to_ttbar = -ttbar_beta
    pplus_tt = boost_four_vectors(incoming_positive, boost_to_ttbar)
    top_tt = boost_four_vectors(top, boost_to_ttbar)
    antitop_tt = boost_four_vectors(antitop, boost_to_ttbar)
    lplus_tt = boost_four_vectors(lepton_positive, boost_to_ttbar)
    lminus_tt = boost_four_vectors(lepton_negative, boost_to_ttbar)

    p_hat = unit(pplus_tt[:, 1:])
    k_hat = unit(top_tt[:, 1:])
    cos_theta = np.einsum("ni,ni->n", p_hat, k_hat)
    r_raw = p_hat - cos_theta[:, None] * k_hat
    sin_theta = np.linalg.norm(r_raw, axis=1)
    singular = sin_theta <= singular_tolerance
    if np.any(singular):
        # Keep finite placeholders; singular rows are explicitly flagged and
        # excluded from numerical comparisons.
        r_raw = r_raw.copy()
        r_raw[singular] = np.array([1.0, 0.0, 0.0])
    r_hat = unit(r_raw)
    n_raw = np.cross(p_hat, k_hat)
    if np.any(singular):
        n_raw = n_raw.copy()
        n_raw[singular] = np.array([0.0, 1.0, 0.0])
    n_hat = unit(n_raw)

    axes = np.stack([k_hat, r_hat, n_hat], axis=1)
    gram = np.einsum("nai,nbi->nab", axes, axes)
    orthonormal_residual = np.linalg.norm(
        gram - np.eye(3)[None, :, :], axis=(1, 2)
    )
    handedness = np.einsum(
        "ni,ni->n",
        np.cross(k_hat, r_hat),
        n_hat,
    )

    top_beta_tt = top_tt[:, 1:] / top_tt[:, 0, None]
    antitop_beta_tt = antitop_tt[:, 1:] / antitop_tt[:, 0, None]
    lplus_top = boost_four_vectors(lplus_tt, -top_beta_tt)
    lminus_antitop = boost_four_vectors(lminus_tt, -antitop_beta_tt)
    lplus_hat = unit(lplus_top[:, 1:])
    lminus_hat = unit(lminus_antitop[:, 1:])

    plus = np.einsum("ni,nai->na", lplus_hat, axes)
    minus = -np.einsum("ni,nai->na", lminus_hat, axes)
    plus[singular] = np.nan
    minus[singular] = np.nan

    return BasisAuditResult(
        plus=plus,
        minus=minus,
        singular=singular,
        orthonormal_residual=orthonormal_residual,
        handedness=handedness,
        metadata={
            "beam_reference": "incoming_positive_lepton",
            "axis_order": ["k", "r", "n"],
            "expected_labelled_handedness": -1.0,
            "minus_analyzer_sign": -1.0,
            "singular_tolerance": singular_tolerance,
        },
    )


def _four_vector(frame: pd.DataFrame, mapping: dict[str, str]) -> np.ndarray:
    columns = [mapping[key] for key in ("e", "px", "py", "pz")]
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise KeyError(f"Missing four-vector columns {missing}")
    return frame[columns].to_numpy(float)


def reconstruct_from_frame(
    frame: pd.DataFrame,
    mapping: dict[str, dict[str, str]],
    singular_tolerance: float = 1.0e-10,
) -> BasisAuditResult:
    required = ["incoming_positive", "top", "antitop", "lepton_positive", "lepton_negative"]
    missing = [name for name in required if name not in mapping]
    if missing:
        raise KeyError(f"Missing four-vector mappings for {missing}")
    return reconstruct_analyzers(
        *[_four_vector(frame, mapping[name]) for name in required],
        singular_tolerance=singular_tolerance,
    )
