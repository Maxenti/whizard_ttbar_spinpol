from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.bootstrap import bootstrap_tomography
from qis_ttbar.paper_spin.io import AnalyzerSample
from qis_ttbar.paper_spin.synthetic import sample_angular_density, synthetic_states


def test_bootstrap_ranges_are_reproducible_and_mergeable():
    coefficients = synthetic_states()["product_polarized"]
    plus, minus = sample_angular_density(coefficients, 2000, 17)
    sample = AnalyzerSample(
        plus, minus, np.ones(len(plus)), None, Path("synthetic"),
        "lepton_collider_paper_v1", {},
    )
    full = bootstrap_tomography(sample, replicas=8, seed=91)
    first = bootstrap_tomography(sample, replicas=8, seed=91, replica_start=0, replica_stop=3)
    second = bootstrap_tomography(sample, replicas=8, seed=91, replica_start=3, replica_stop=8)
    merged = np.vstack([first.coefficient_replicas, second.coefficient_replicas])
    assert np.allclose(full.coefficient_replicas, merged)
