from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.histograms import angular_observables, normalized_histogram
from qis_ttbar.paper_spin.io import AnalyzerSample
from qis_ttbar.paper_spin.synthetic import sample_angular_density


def test_normalized_histogram_and_covariance():
    plus, minus = sample_angular_density(np.zeros(15), 20000, 19)
    sample = AnalyzerSample(
        plus, minus, np.ones(len(plus)), None, Path("synthetic"),
        "lepton_collider_paper_v1", {},
    )
    values = angular_observables(sample)["B1k"]
    result = normalized_histogram("B1k", values, sample.weights, np.linspace(-1, 1, 21))
    assert np.isclose(np.sum(result.probabilities), 1.0)
    assert np.isclose(np.sum(result.densities * np.diff(result.edges)), 1.0)
    assert np.allclose(result.probability_covariance, result.probability_covariance.T)
    assert np.linalg.eigvalsh(result.probability_covariance).min() > -1e-12
