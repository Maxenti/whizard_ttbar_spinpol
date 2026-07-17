from __future__ import annotations

import dataclasses
import itertools
import numpy as np
from scipy.optimize import least_squares

from ..exceptions import ReconstructionError
from ..models import FourVector


@dataclasses.dataclass(frozen=True)
class ReconstructionSolution:
    neutrino: FourVector
    antineutrino: FourVector
    top: FourVector
    antitop: FourVector
    pairing: tuple[int, int]
    chi2: float
    residuals: np.ndarray
    success: bool
    message: str


class DileptonReconstructor:
    """Constrained dilepton ttbar reconstruction using known initial four-momentum.

    Six neutrino momentum components are fitted to missing four-momentum plus
    W/top mass constraints. Multiple deterministic/random starts and both
    b-lepton pairings are evaluated. ISR photons can be accounted for by using
    the measured hard-system initial four-vector rather than nominal beams.
    """

    def __init__(
        self, *, top_mass_GeV: float = 173.1, w_mass_GeV: float = 80.379,
        top_width_GeV: float = 1.523, w_width_GeV: float = 2.085,
        solver_starts: int = 32, seed: int = 820001,
    ):
        self.mt, self.mw = top_mass_GeV, w_mass_GeV
        self.gt, self.gw = top_width_GeV, w_width_GeV
        self.solver_starts = solver_starts
        self.rng = np.random.default_rng(seed)

    @staticmethod
    def _mass_residual(vector: FourVector, target: float, width: float) -> float:
        return (vector.mass - target) / max(width, 1e-9)

    def _residuals(
        self, x: np.ndarray, initial: FourVector, visible: FourVector,
        b: FourVector, bbar: FourVector, lp: FourVector, lm: FourVector,
    ) -> np.ndarray:
        n = FourVector(float(np.linalg.norm(x[:3])), *map(float, x[:3]))
        nb = FourVector(float(np.linalg.norm(x[3:])), *map(float, x[3:]))
        missing = initial - visible
        momentum = (n + nb) - missing
        top = b + lp + n
        antitop = bbar + lm + nb
        return np.array([
            momentum.px / 1.0, momentum.py / 1.0, momentum.pz / 1.0, momentum.e / 1.0,
            self._mass_residual(lp + n, self.mw, self.gw),
            self._mass_residual(lm + nb, self.mw, self.gw),
            self._mass_residual(top, self.mt, self.gt),
            self._mass_residual(antitop, self.mt, self.gt),
        ])

    def reconstruct(
        self, initial: FourVector, lepton_plus: FourVector, lepton_minus: FourVector,
        bjets: tuple[FourVector, FourVector], *, max_chi2: float | None = None,
    ) -> ReconstructionSolution:
        visible = lepton_plus + lepton_minus + bjets[0] + bjets[1]
        missing = initial - visible
        half = 0.5 * missing.spatial
        best: ReconstructionSolution | None = None
        for pairing in ((0, 1), (1, 0)):
            b, bbar = bjets[pairing[0]], bjets[pairing[1]]
            starts = [np.concatenate([half, half])]
            scale = max(float(np.linalg.norm(missing.spatial)), 20.0)
            starts.extend(np.concatenate([half + self.rng.normal(0, 0.5 * scale, 3), half + self.rng.normal(0, 0.5 * scale, 3)]) for _ in range(self.solver_starts - 1))
            for start in starts:
                result = least_squares(
                    self._residuals, start,
                    args=(initial, visible, b, bbar, lepton_plus, lepton_minus),
                    method="trf", max_nfev=3000, xtol=1e-11, ftol=1e-11, gtol=1e-11,
                )
                residuals = self._residuals(result.x, initial, visible, b, bbar, lepton_plus, lepton_minus)
                chi2 = float(residuals @ residuals)
                n = FourVector(float(np.linalg.norm(result.x[:3])), *map(float, result.x[:3]))
                nb = FourVector(float(np.linalg.norm(result.x[3:])), *map(float, result.x[3:]))
                candidate = ReconstructionSolution(
                    neutrino=n, antineutrino=nb, top=b + lepton_plus + n,
                    antitop=bbar + lepton_minus + nb, pairing=pairing, chi2=chi2,
                    residuals=residuals, success=bool(result.success), message=str(result.message),
                )
                if best is None or candidate.chi2 < best.chi2:
                    best = candidate
        if best is None:
            raise ReconstructionError("no reconstruction starts were evaluated")
        if max_chi2 is not None and best.chi2 > max_chi2:
            raise ReconstructionError(f"best dilepton solution chi2={best.chi2:.3g} exceeds {max_chi2}")
        return best
