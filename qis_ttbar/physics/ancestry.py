from __future__ import annotations

import dataclasses
import numpy as np

from ..models import TTbarTruth


@dataclasses.dataclass(frozen=True)
class ClosureResult:
    top_energy_residual: float
    top_momentum_residual: float
    antitop_energy_residual: float
    antitop_momentum_residual: float
    valid: bool


def validate_truth_closure(truth: TTbarTruth, tolerance_GeV: float = 1e-5) -> ClosureResult:
    top_sum = truth.b + truth.lepton_plus + truth.neutrino
    bar_sum = truth.bbar + truth.lepton_minus + truth.antineutrino
    top_delta = truth.top - top_sum
    bar_delta = truth.antitop - bar_sum
    values = (
        abs(top_delta.e), float(np.linalg.norm(top_delta.spatial)),
        abs(bar_delta.e), float(np.linalg.norm(bar_delta.spatial)),
    )
    return ClosureResult(*values, valid=max(values) <= tolerance_GeV)
