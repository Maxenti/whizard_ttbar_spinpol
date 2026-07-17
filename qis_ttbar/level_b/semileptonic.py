from __future__ import annotations

import dataclasses
import itertools
from typing import Sequence
import numpy as np

from ..models import FourVector


@dataclasses.dataclass(frozen=True)
class SemileptonicSolution:
    hadronic_w: FourVector
    hadronic_top: FourVector
    leptonic_top: FourVector
    indices: tuple[int, int, int, int]
    chi2: float


class SemileptonicReconstructor:
    def __init__(self, top_mass_GeV: float = 173.1, w_mass_GeV: float = 80.379, top_sigma_GeV: float = 15.0, w_sigma_GeV: float = 10.0):
        self.mt, self.mw, self.st, self.sw = top_mass_GeV, w_mass_GeV, top_sigma_GeV, w_sigma_GeV

    def reconstruct(
        self, jets: Sequence[FourVector], btag_scores: Sequence[float],
        lepton: FourVector, neutrino: FourVector,
    ) -> SemileptonicSolution:
        if len(jets) < 4 or len(jets) != len(btag_scores):
            raise ValueError("need at least four jets and one btag score per jet")
        best = None
        for light1, light2 in itertools.combinations(range(len(jets)), 2):
            remaining = [i for i in range(len(jets)) if i not in {light1, light2}]
            for bhad, blep in itertools.permutations(remaining, 2):
                w = jets[light1] + jets[light2]
                thad = w + jets[bhad]
                tlep = lepton + neutrino + jets[blep]
                bpenalty = -2.0 * np.log(max(btag_scores[bhad] * btag_scores[blep], 1e-12))
                chi2 = ((w.mass - self.mw) / self.sw) ** 2 + ((thad.mass - self.mt) / self.st) ** 2 + ((tlep.mass - self.mt) / self.st) ** 2 + bpenalty
                candidate = SemileptonicSolution(w, thad, tlep, (light1, light2, bhad, blep), float(chi2))
                if best is None or candidate.chi2 < best.chi2:
                    best = candidate
        if best is None:
            raise RuntimeError("no semileptonic jet assignment")
        return best
