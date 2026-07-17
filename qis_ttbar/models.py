from __future__ import annotations

import dataclasses
from typing import Iterable

import numpy as np


@dataclasses.dataclass(frozen=True)
class FourVector:
    """Cartesian four-vector using (E, px, py, pz) and metric (+---)."""

    e: float
    px: float
    py: float
    pz: float

    @property
    def spatial(self) -> np.ndarray:
        return np.asarray([self.px, self.py, self.pz], dtype=float)

    @property
    def p2(self) -> float:
        return float(np.dot(self.spatial, self.spatial))

    @property
    def mass2(self) -> float:
        return float(self.e * self.e - self.p2)

    @property
    def mass(self) -> float:
        return float(np.sqrt(max(self.mass2, 0.0)))

    @property
    def pt(self) -> float:
        return float(np.hypot(self.px, self.py))

    @property
    def phi(self) -> float:
        return float(np.arctan2(self.py, self.px))

    @property
    def eta(self) -> float:
        p = float(np.sqrt(self.p2))
        if p <= abs(self.pz):
            return float(np.copysign(np.inf, self.pz))
        return float(0.5 * np.log((p + self.pz) / (p - self.pz)))

    @property
    def beta(self) -> np.ndarray:
        if self.e == 0:
            raise ZeroDivisionError("zero-energy four-vector has no rest-frame velocity")
        return self.spatial / self.e

    def __add__(self, other: "FourVector") -> "FourVector":
        return FourVector(self.e + other.e, self.px + other.px, self.py + other.py, self.pz + other.pz)

    def __sub__(self, other: "FourVector") -> "FourVector":
        return FourVector(self.e - other.e, self.px - other.px, self.py - other.py, self.pz - other.pz)

    def scale(self, value: float) -> "FourVector":
        return FourVector(value * self.e, value * self.px, value * self.py, value * self.pz)

    def boost(self, beta: Iterable[float]) -> "FourVector":
        """Active Lorentz boost by velocity beta; use -parent.beta for parent rest frame."""
        b = np.asarray(tuple(beta), dtype=float)
        b2 = float(np.dot(b, b))
        if b2 >= 1.0:
            raise ValueError(f"superluminal boost beta^2={b2}")
        if b2 < 1e-30:
            return self
        gamma = 1.0 / np.sqrt(1.0 - b2)
        bp = float(np.dot(b, self.spatial))
        gamma2 = (gamma - 1.0) / b2
        p = self.spatial + (gamma2 * bp + gamma * self.e) * b
        e = gamma * (self.e + bp)
        return FourVector(float(e), float(p[0]), float(p[1]), float(p[2]))

    def unit3(self, *, atol: float = 1e-14) -> np.ndarray:
        norm = float(np.linalg.norm(self.spatial))
        if norm <= atol:
            raise ValueError("cannot normalize zero three-vector")
        return self.spatial / norm


@dataclasses.dataclass(frozen=True)
class Particle:
    pdg: int
    status: int
    mother1: int
    mother2: int
    color1: int
    color2: int
    p4: FourVector
    mass_record: float
    lifetime: float
    spin: float


@dataclasses.dataclass(frozen=True)
class LHEEvent:
    index: int
    idprup: int
    weight: float
    scale: float
    aqed: float
    aqcd: float
    particles: tuple[Particle, ...]

    def particle(self, one_based_index: int) -> Particle:
        if one_based_index < 1 or one_based_index > len(self.particles):
            raise IndexError(one_based_index)
        return self.particles[one_based_index - 1]


@dataclasses.dataclass(frozen=True)
class TTbarTruth:
    event_index: int
    event_weight: float
    beam_minus: FourVector
    beam_plus: FourVector
    top: FourVector
    antitop: FourVector
    b: FourVector
    bbar: FourVector
    lepton_plus: FourVector
    lepton_minus: FourVector
    neutrino: FourVector
    antineutrino: FourVector
    initial_state: str
    decay_channel: str
