from __future__ import annotations

import math
from typing import Any

import numpy as np

from ..models import TTbarTruth
from .bases import build_krn_basis
from .ancestry import validate_truth_closure


# Event-level angular analyzers used to extract the complete 15-parameter
# ttbar spin density matrix in the ordered (k,r,n) basis.  Lower-case names
# denote bounded per-event observables.  Their weighted means give the
# conventional upper-case coefficients through
#
#   B1_i = 3 <b1i> / alpha_plus
#   B2_i = 3 <b2i> / alpha_minus
#   C_ij = 9 <cij> / (alpha_plus alpha_minus)
#
# because event_observables applies antitop_analyzer_sign=-1 by default.
SPIN15_EVENT_COLUMNS: tuple[str, ...] = (
    "b1k", "b1r", "b1n",
    "b2k", "b2r", "b2n",
    "ckk", "crr", "cnn",
    "ckr", "crk", "ckn", "cnk", "crn", "cnr",
)

SPIN15_COEFFICIENT_NAMES: tuple[str, ...] = (
    "B1k", "B1r", "B1n",
    "B2k", "B2r", "B2n",
    "Ckk", "Crr", "Cnn",
    "Ckr", "Crk", "Ckn", "Cnk", "Crn", "Cnr",
)


def wrap_delta_phi(value: float) -> float:
    return float((value + math.pi) % (2.0 * math.pi) - math.pi)


def event_observables(
    truth: TTbarTruth,
    *,
    basis_order: tuple[str, str, str] = ("k", "r", "n"),
    antitop_analyzer_sign: float = -1.0,
    alpha_plus: float = 1.0,
    alpha_minus: float = 1.0,
) -> dict[str, Any]:
    tt = truth.top + truth.antitop
    beta_tt = tt.beta
    top_tt = truth.top.boost(-beta_tt)
    antitop_tt = truth.antitop.boost(-beta_tt)
    beam_minus_tt = truth.beam_minus.boost(-beta_tt)
    lp_tt = truth.lepton_plus.boost(-beta_tt)
    lm_tt = truth.lepton_minus.boost(-beta_tt)

    basis = build_krn_basis(beam_minus_tt, top_tt, antitop_tt, order=basis_order)
    lp_top = truth.lepton_plus.boost(-truth.top.beta)
    lm_bar = truth.lepton_minus.boost(-truth.antitop.beta)
    u_plus = lp_top.unit3()
    u_minus = antitop_analyzer_sign * lm_bar.unit3()
    coordinates_plus = basis.top_axes.T @ u_plus
    coordinates_minus = basis.antitop_axes.T @ u_minus

    beam_hat = beam_minus_tt.unit3()
    cos_theta_t = float(np.dot(top_tt.unit3(), beam_hat))
    cos_opening_tt = float(np.clip(np.dot(lp_tt.unit3(), lm_tt.unit3()), -1.0, 1.0))
    delta_phi_lab = abs(wrap_delta_phi(truth.lepton_plus.phi - truth.lepton_minus.phi))
    delta_phi_tt = abs(wrap_delta_phi(lp_tt.phi - lm_tt.phi))
    closure = validate_truth_closure(truth)

    output: dict[str, Any] = {
        "event_index": truth.event_index,
        "event_weight": truth.event_weight,
        "initial_state": truth.initial_state,
        "decay_channel": truth.decay_channel,
        "mtt_GeV": tt.mass,
        "sqrt_s_hard_GeV": (truth.beam_minus + truth.beam_plus).mass,
        "beta_top_tt": float(np.linalg.norm(top_tt.beta)),
        "cos_theta_t": cos_theta_t,
        "delta_phi_ll_lab": delta_phi_lab,
        "delta_phi_ll_tt": delta_phi_tt,
        "cos_opening_ll_tt": cos_opening_tt,
        "opening_ll_tt": float(np.arccos(np.clip(cos_opening_tt, -1.0, 1.0))),
        "top_pt_GeV": truth.top.pt,
        "antitop_pt_GeV": truth.antitop.pt,
        "lepton_plus_pt_GeV": truth.lepton_plus.pt,
        "lepton_minus_pt_GeV": truth.lepton_minus.pt,
        "top_decay_closure_valid": closure.valid,
        "top_decay_residual_GeV": max(closure.top_energy_residual, closure.top_momentum_residual),
        "antitop_decay_residual_GeV": max(closure.antitop_energy_residual, closure.antitop_momentum_residual),
        "alpha_plus": alpha_plus,
        "alpha_minus": alpha_minus,
        "antitop_analyzer_sign": antitop_analyzer_sign,
    }
    for index, name in enumerate(basis_order):
        output[f"uplus_{name}"] = float(coordinates_plus[index])
        output[f"uminus_{name}"] = float(coordinates_minus[index])
    for i, left in enumerate(basis_order):
        for j, right in enumerate(basis_order):
            output[f"uproduct_{left}{right}"] = float(coordinates_plus[i] * coordinates_minus[j])

    # Stable, analysis-facing aliases for the complete 6+9 spin set.  These
    # aliases intentionally remain independent of basis_order serialization: the
    # named coordinates are looked up by axis name, not by numerical position.
    coordinate_plus = {name: float(coordinates_plus[index]) for index, name in enumerate(basis_order)}
    coordinate_minus = {name: float(coordinates_minus[index]) for index, name in enumerate(basis_order)}
    for axis in ("k", "r", "n"):
        output[f"b1{axis}"] = coordinate_plus[axis]
        output[f"b2{axis}"] = coordinate_minus[axis]
    for left in ("k", "r", "n"):
        for right in ("k", "r", "n"):
            output[f"c{left}{right}"] = coordinate_plus[left] * coordinate_minus[right]

    # CP-odd/T-odd triple product in the ttbar frame.
    output["cp_triple_product"] = float(np.dot(beam_hat, np.cross(lp_tt.unit3(), lm_tt.unit3())))
    return output


def truth_to_row(truth: TTbarTruth, **kwargs: Any) -> dict[str, Any]:
    row = event_observables(truth, **kwargs)
    for name in (
        "beam_minus", "beam_plus", "top", "antitop", "b", "bbar",
        "lepton_plus", "lepton_minus", "neutrino", "antineutrino",
    ):
        vector = getattr(truth, name)
        for component in ("e", "px", "py", "pz", "mass", "pt", "eta", "phi"):
            row[f"{name}_{component}"] = float(getattr(vector, component))
    return row
