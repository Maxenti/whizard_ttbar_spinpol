from __future__ import annotations

import dataclasses
import math
from typing import Iterable

import numpy as np

from ..models import FourVector


@dataclasses.dataclass(frozen=True)
class ResponseConfig:
    lepton_efficiency: float = 0.98
    bjet_efficiency: float = 0.80
    lepton_relative_pt_resolution: float = 0.001
    lepton_eta_resolution: float = 5e-4
    lepton_phi_resolution: float = 5e-4
    jet_relative_energy_resolution: float = 0.05
    jet_angular_resolution: float = 0.01
    lepton_scale: float = 1.0
    jet_scale: float = 1.0


@dataclasses.dataclass(frozen=True)
class ReconstructedObject:
    p4: FourVector
    accepted: bool
    truth_index: int | None = None
    object_type: str = "unknown"


class DetectorResponse:
    """Reproducible parametric detector response for closure and method studies.

    This is not a substitute for full detector simulation. It is a functional
    Level-B response layer with explicit efficiencies, scales, and resolutions.
    """

    def __init__(self, config: ResponseConfig, seed: int = 810001):
        self.config = config
        self.rng = np.random.default_rng(seed)

    @staticmethod
    def _from_pt_eta_phi_mass(pt: float, eta: float, phi: float, mass: float) -> FourVector:
        px, py = pt * math.cos(phi), pt * math.sin(phi)
        pz = pt * math.sinh(eta)
        energy = math.sqrt(max(mass * mass + px * px + py * py + pz * pz, 0.0))
        return FourVector(energy, px, py, pz)

    def smear_lepton(self, p4: FourVector, truth_index: int | None = None) -> ReconstructedObject:
        accepted = bool(self.rng.random() < self.config.lepton_efficiency)
        if not accepted:
            return ReconstructedObject(p4, False, truth_index, "lepton")
        pt = max(0.0, p4.pt * self.config.lepton_scale * (1.0 + self.rng.normal(0.0, self.config.lepton_relative_pt_resolution)))
        eta = p4.eta + self.rng.normal(0.0, self.config.lepton_eta_resolution)
        phi = p4.phi + self.rng.normal(0.0, self.config.lepton_phi_resolution)
        return ReconstructedObject(self._from_pt_eta_phi_mass(pt, eta, phi, p4.mass), True, truth_index, "lepton")

    def smear_jet(self, p4: FourVector, truth_index: int | None = None, btag: bool = True) -> ReconstructedObject:
        accepted = bool(self.rng.random() < (self.config.bjet_efficiency if btag else 1.0))
        if not accepted:
            return ReconstructedObject(p4, False, truth_index, "bjet" if btag else "jet")
        energy = max(p4.mass, p4.e * self.config.jet_scale * (1.0 + self.rng.normal(0.0, self.config.jet_relative_energy_resolution)))
        eta = p4.eta + self.rng.normal(0.0, self.config.jet_angular_resolution)
        phi = p4.phi + self.rng.normal(0.0, self.config.jet_angular_resolution)
        momentum = math.sqrt(max(energy * energy - p4.mass * p4.mass, 0.0))
        pt = momentum / math.cosh(eta)
        return ReconstructedObject(self._from_pt_eta_phi_mass(pt, eta, phi, p4.mass), True, truth_index, "bjet" if btag else "jet")
