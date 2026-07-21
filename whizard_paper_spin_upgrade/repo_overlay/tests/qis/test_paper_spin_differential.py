from pathlib import Path

import numpy as np
import pandas as pd

from qis_ttbar.paper_spin.differential import estimate_differential
from qis_ttbar.paper_spin.io import AnalyzerSample
from qis_ttbar.paper_spin.synthetic import sample_angular_density


def test_differential_moments_are_calculated_per_bin():
    plus, minus = sample_angular_density(np.zeros(15), 10000, 88)
    frame = pd.DataFrame({"costheta_reviewed": np.linspace(-1.0, 1.0, len(plus))})
    sample = AnalyzerSample(
        plus, minus, np.ones(len(plus)), None, Path("synthetic"),
        "lepton_collider_paper_v1", {},
    )
    results = estimate_differential(
        frame,
        sample,
        {
            "name": "costheta",
            "column": "costheta_reviewed",
            "mapping_reviewed": True,
            "sign": 1.0,
            "edges": [-1.0, -0.5, 0.0, 0.5, 1.0],
            "minimum_events": 100,
        },
    )
    assert len(results) == 4
    assert sum(item.events for item in results) == len(plus)
    assert all(item.moment.covariance.shape == (15, 15) for item in results)
