"""First-principles tree-level gamma/Z benchmark for l+l- -> ttbar.

The implementation evaluates explicit Dirac spinors and the full coherent
photon/Z amplitude.  It does not use fitted coefficient templates.  Final-state
spin amplitudes are computed in the lepton-collider k,r,n basis and integrated
with Gauss-Legendre quadrature.

This is a generator-closure benchmark, not a substitute for higher-order EW/QCD
predictions.  A strict comparison requires the same SM input scheme and masses
as the WHIZARD campaign.  The pipeline records those inputs explicitly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .contracts import AXES, get_convention
from .density import coefficients_from_density_matrix, validate_density_matrix

GEV2_TO_FB = 0.389379338e12


@dataclass(frozen=True)
class SMParameters:
    alpha_em_inverse: float
    sin2_theta_w: float
    mass_z_GeV: float
    width_z_GeV: float
    mass_top_GeV: float
    mass_electron_GeV: float = 0.00051099895
    mass_muon_GeV: float = 0.1056583755
    color_factor: float = 3.0
    source: str = "explicit_config"
    generator_match_reviewed: bool = False

    @property
    def alpha_em(self) -> float:
        return 1.0 / self.alpha_em_inverse

    @property
    def sin_theta_w(self) -> float:
        return float(np.sqrt(self.sin2_theta_w))

    @property
    def cos_theta_w(self) -> float:
        return float(np.sqrt(1.0 - self.sin2_theta_w))


def load_sm_parameters(path: str | Path) -> SMParameters:
    source = Path(path)
    data = yaml.safe_load(source.read_text())
    return SMParameters(**data)


I2 = np.eye(2, dtype=complex)
Z2 = np.zeros((2, 2), dtype=complex)
SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
SIGMA = np.stack([SIGMA_X, SIGMA_Y, SIGMA_Z])
GAMMA_0 = np.block([[I2, Z2], [Z2, -I2]])
GAMMA = [GAMMA_0]
for sigma in SIGMA:
    GAMMA.append(np.block([[Z2, sigma], [-sigma, Z2]]))
GAMMA_5 = 1.0j * GAMMA[0] @ GAMMA[1] @ GAMMA[2] @ GAMMA[3]
IDENTITY_4 = np.eye(4, dtype=complex)


def _normalize(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0:
        raise ValueError("Cannot normalize zero vector")
    return vector / norm


def pauli_spinor(axis: np.ndarray, eigenvalue: int) -> np.ndarray:
    axis = _normalize(axis)
    operator = sum(axis[i] * SIGMA[i] for i in range(3))
    values, vectors = np.linalg.eigh(operator)
    index = int(np.argmax(values) if eigenvalue > 0 else np.argmin(values))
    spinor = vectors[:, index]
    largest = int(np.argmax(np.abs(spinor)))
    spinor *= np.exp(-1.0j * np.angle(spinor[largest]))
    return spinor


def charge_conjugate_pauli_spinor(spinor: np.ndarray) -> np.ndarray:
    """Return eta=-i sigma_y chi* for a physical antiparticle spin state."""

    return -1.0j * SIGMA_Y @ np.asarray(spinor, dtype=complex).conj()


def particle_spinor(momentum: np.ndarray, mass: float, spinor: np.ndarray) -> np.ndarray:
    energy = float(momentum[0])
    spatial = np.asarray(momentum[1:], dtype=float)
    factor = np.sqrt(energy + mass)
    sigma_p = sum(spatial[i] * SIGMA[i] for i in range(3))
    return factor * np.concatenate(
        [spinor, sigma_p @ spinor / (energy + mass)]
    )


def antiparticle_spinor(
    momentum: np.ndarray,
    mass: float,
    physical_spinor: np.ndarray,
) -> np.ndarray:
    energy = float(momentum[0])
    spatial = np.asarray(momentum[1:], dtype=float)
    eta = charge_conjugate_pauli_spinor(physical_spinor)
    factor = np.sqrt(energy + mass)
    sigma_p = sum(spatial[i] * SIGMA[i] for i in range(3))
    return factor * np.concatenate(
        [sigma_p @ eta / (energy + mass), eta]
    )


def dirac_bar(spinor: np.ndarray) -> np.ndarray:
    return np.asarray(spinor, dtype=complex).conj().T @ GAMMA_0


def current_vu(
    antiparticle: np.ndarray,
    particle: np.ndarray,
    vector_coupling: float,
    axial_coupling: float,
) -> np.ndarray:
    vertex = vector_coupling * IDENTITY_4 - axial_coupling * GAMMA_5
    return np.array(
        [
            dirac_bar(antiparticle) @ GAMMA[mu] @ vertex @ particle
            for mu in range(4)
        ],
        dtype=complex,
    )


def current_uv(
    particle: np.ndarray,
    antiparticle: np.ndarray,
    vector_coupling: float,
    axial_coupling: float,
) -> np.ndarray:
    vertex = vector_coupling * IDENTITY_4 - axial_coupling * GAMMA_5
    return np.array(
        [
            dirac_bar(particle) @ GAMMA[mu] @ vertex @ antiparticle
            for mu in range(4)
        ],
        dtype=complex,
    )


def minkowski_contract(first: np.ndarray, second: np.ndarray) -> complex:
    return first[0] * second[0] - np.dot(first[1:], second[1:])


def physical_spin_basis(
    k_hat: np.ndarray,
    r_hat: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Spin up/down along k with phase fixed by sigma_r |up> = |down>."""

    up = pauli_spinor(k_hat, +1)
    sigma_r = sum(r_hat[i] * SIGMA[i] for i in range(3))
    down = sigma_r @ up
    down /= np.linalg.norm(down)
    return up, down


def lepton_collider_axes(costheta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sintheta = float(np.sqrt(max(0.0, 1.0 - costheta * costheta)))
    if sintheta <= 1.0e-14:
        raise ValueError("k,r,n basis is singular at |cos(theta)|=1")
    p_plus_hat = np.array([0.0, 0.0, 1.0])
    k_hat = np.array([sintheta, 0.0, costheta])
    r_hat = (p_plus_hat - costheta * k_hat) / sintheta
    n_hat = np.cross(p_plus_hat, k_hat) / sintheta
    return _normalize(k_hat), _normalize(r_hat), _normalize(n_hat)


class TreeLevelSM:
    def __init__(self, parameters: SMParameters):
        self.parameters = parameters

    @staticmethod
    def helicities(polarization: str) -> tuple[int, int]:
        mapping = {
            "LR100": (-1, +1),
            "RL100": (+1, -1),
            "LL100": (-1, -1),
            "RR100": (+1, +1),
        }
        try:
            return mapping[polarization]
        except KeyError as exc:
            raise ValueError(f"Unsupported beam polarization {polarization!r}") from exc

    def _lepton_mass(self, initial_state: str) -> float:
        if initial_state == "ee":
            return self.parameters.mass_electron_GeV
        if initial_state == "mumu":
            return self.parameters.mass_muon_GeV
        raise ValueError(f"Unsupported initial state {initial_state!r}")

    def amplitude_matrix(
        self,
        sqrt_s_GeV: float,
        costheta: float,
        initial_state: str,
        polarization: str,
    ) -> tuple[np.ndarray, float]:
        parameters = self.parameters
        s = float(sqrt_s_GeV) ** 2
        energy = 0.5 * float(sqrt_s_GeV)
        lepton_mass = self._lepton_mass(initial_state)
        top_mass = parameters.mass_top_GeV
        if energy <= top_mass:
            raise ValueError(
                f"sqrt(s)={sqrt_s_GeV} GeV is below ttbar threshold"
            )
        p_in = float(np.sqrt(max(0.0, energy * energy - lepton_mass * lepton_mass)))
        p_out = float(np.sqrt(max(0.0, energy * energy - top_mass * top_mass)))
        beta = p_out / energy
        sintheta = float(np.sqrt(max(0.0, 1.0 - costheta * costheta)))

        p_plus = np.array([energy, 0.0, 0.0, +p_in])
        p_minus = np.array([energy, 0.0, 0.0, -p_in])
        top = np.array(
            [energy, p_out * sintheta, 0.0, p_out * costheta]
        )
        antitop = np.array(
            [energy, -p_out * sintheta, 0.0, -p_out * costheta]
        )

        k_hat, r_hat, _ = lepton_collider_axes(costheta)
        top_up, top_down = physical_spin_basis(k_hat, r_hat)
        spinors = [top_up, top_down]

        h_minus, h_plus = self.helicities(polarization)
        negative_lepton_chi = pauli_spinor(p_minus[1:], h_minus)
        positive_lepton_chi = pauli_spinor(p_plus[1:], h_plus)
        negative_lepton_u = particle_spinor(
            p_minus, lepton_mass, negative_lepton_chi
        )
        positive_lepton_v = antiparticle_spinor(
            p_plus, lepton_mass, positive_lepton_chi
        )

        q_lepton = -1.0
        q_top = 2.0 / 3.0
        t3_lepton = -0.5
        t3_top = +0.5
        sin2 = parameters.sin2_theta_w
        gv_lepton = t3_lepton / 2.0 - q_lepton * sin2
        ga_lepton = t3_lepton / 2.0
        gv_top = t3_top / 2.0 - q_top * sin2
        ga_top = t3_top / 2.0

        lepton_photon = current_vu(
            positive_lepton_v,
            negative_lepton_u,
            1.0,
            0.0,
        )
        lepton_z = current_vu(
            positive_lepton_v,
            negative_lepton_u,
            gv_lepton,
            ga_lepton,
        )

        e_squared = 4.0 * np.pi * parameters.alpha_em
        photon_factor = e_squared * q_lepton * q_top / s
        z_denominator = complex(
            s - parameters.mass_z_GeV**2,
            parameters.mass_z_GeV * parameters.width_z_GeV,
        )
        z_factor = (
            e_squared
            / (
                parameters.sin_theta_w**2
                * parameters.cos_theta_w**2
            )
            / z_denominator
        )

        amplitude = np.zeros((2, 2), dtype=complex)
        for top_index, top_chi in enumerate(spinors):
            top_u = particle_spinor(top, top_mass, top_chi)
            for antitop_index, antitop_physical_chi in enumerate(spinors):
                antitop_v = antiparticle_spinor(
                    antitop,
                    top_mass,
                    antitop_physical_chi,
                )
                top_photon = current_uv(top_u, antitop_v, 1.0, 0.0)
                top_z = current_uv(top_u, antitop_v, gv_top, ga_top)
                amplitude[top_index, antitop_index] = (
                    photon_factor
                    * minkowski_contract(lepton_photon, top_photon)
                    + z_factor * minkowski_contract(lepton_z, top_z)
                )
        return amplitude, beta

    def differential_density(
        self,
        sqrt_s_GeV: float,
        costheta: float,
        initial_state: str,
        polarization: str,
    ) -> dict[str, Any]:
        amplitude, beta = self.amplitude_matrix(
            sqrt_s_GeV,
            costheta,
            initial_state,
            polarization,
        )
        vector = amplitude.reshape(4)
        outer = np.outer(vector, vector.conj())
        matrix_element_squared = float(np.trace(outer).real)
        if matrix_element_squared <= 0.0:
            raise RuntimeError("Non-positive matrix-element norm")
        rho = outer / matrix_element_squared
        validation = validate_density_matrix(rho)
        if not validation.valid:
            raise RuntimeError(
                f"Analytic differential rho is not physical: {validation}"
            )
        s = float(sqrt_s_GeV) ** 2
        dsigma_dcostheta_GeV2 = (
            self.parameters.color_factor
            * beta
            * matrix_element_squared
            / (32.0 * np.pi * s)
        )
        return {
            "rho": rho,
            "coefficient_vector": coefficients_from_density_matrix(rho),
            "matrix_element_squared": matrix_element_squared,
            "dsigma_dcostheta_GeV2": dsigma_dcostheta_GeV2,
            "dsigma_dcostheta_fb": dsigma_dcostheta_GeV2 * GEV2_TO_FB,
            "beta": beta,
        }

    def integrated_density(
        self,
        sqrt_s_GeV: float,
        initial_state: str,
        polarization: str,
        quadrature_points: int = 256,
    ) -> dict[str, Any]:
        nodes, weights = np.polynomial.legendre.leggauss(quadrature_points)
        rho_numerator = np.zeros((4, 4), dtype=complex)
        cross_section_GeV2 = 0.0
        for costheta, weight in zip(nodes, weights, strict=True):
            differential = self.differential_density(
                sqrt_s_GeV,
                float(costheta),
                initial_state,
                polarization,
            )
            dsigma = differential["dsigma_dcostheta_GeV2"]
            rho_numerator += weight * dsigma * differential["rho"]
            cross_section_GeV2 += float(weight * dsigma)
        rho = rho_numerator / cross_section_GeV2
        rho = 0.5 * (rho + rho.conj().T)
        validation = validate_density_matrix(rho)
        if not validation.valid:
            raise RuntimeError(f"Integrated analytic rho is not physical: {validation}")
        return {
            "rho": rho,
            "coefficient_vector": coefficients_from_density_matrix(rho),
            "cross_section_GeV2": cross_section_GeV2,
            "cross_section_fb": cross_section_GeV2 * GEV2_TO_FB,
            "sqrt_s_GeV": float(sqrt_s_GeV),
            "initial_state": initial_state,
            "polarization": polarization,
            "quadrature_points": int(quadrature_points),
            "parameters": asdict(self.parameters),
        }

    def event_conditioned_density(
        self,
        sqrt_s_values_GeV: np.ndarray,
        costheta_values: np.ndarray,
        event_weights: np.ndarray,
        initial_state: str,
        polarization: str,
    ) -> dict[str, Any]:
        sqrt_s_values = np.asarray(sqrt_s_values_GeV, dtype=float)
        costheta_values = np.asarray(costheta_values, dtype=float)
        weights = np.asarray(event_weights, dtype=float)
        if not (
            sqrt_s_values.shape == costheta_values.shape == weights.shape
        ):
            raise ValueError("Event-conditioned arrays must have identical shapes")
        if np.any(weights < 0.0) or float(np.sum(weights)) <= 0.0:
            raise ValueError("Event-conditioned benchmark requires positive weights")
        normalized = weights / np.sum(weights)
        rho = np.zeros((4, 4), dtype=complex)
        used = 0
        for sqrt_s, costheta, weight in zip(
            sqrt_s_values,
            costheta_values,
            normalized,
            strict=True,
        ):
            if sqrt_s <= 2.0 * self.parameters.mass_top_GeV:
                continue
            if abs(costheta) >= 1.0:
                continue
            differential = self.differential_density(
                float(sqrt_s),
                float(costheta),
                initial_state,
                polarization,
            )
            rho += float(weight) * differential["rho"]
            used += 1
        if used == 0:
            raise ValueError("No events usable for event-conditioned benchmark")
        rho /= np.trace(rho).real
        rho = 0.5 * (rho + rho.conj().T)
        validation = validate_density_matrix(rho)
        if not validation.valid:
            raise RuntimeError(f"Event-conditioned rho is not physical: {validation}")
        return {
            "rho": rho,
            "coefficient_vector": coefficients_from_density_matrix(rho),
            "events_used": used,
            "initial_state": initial_state,
            "polarization": polarization,
            "parameters": asdict(self.parameters),
        }
