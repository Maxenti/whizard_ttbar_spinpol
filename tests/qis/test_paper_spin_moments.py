from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.io import AnalyzerSample
from qis_ttbar.paper_spin.moments import (
    derive_connected_correlation,
    derive_linear_quantities,
    estimate_moments,
)
from qis_ttbar.paper_spin.synthetic import sample_angular_density, synthetic_states


def test_isotropic_moments_and_full_covariance():
    plus, minus = sample_angular_density(np.zeros(15), 100000, 1234)
    sample = AnalyzerSample(
        plus, minus, np.ones(len(plus)), np.arange(len(plus)), Path("synthetic"),
        "lepton_collider_paper_v1", {},
    )
    result = estimate_moments(sample)
    assert result.covariance.shape == (15, 15)
    assert np.allclose(result.covariance, result.covariance.T)
    assert np.linalg.eigvalsh(result.covariance).min() > -1e-12
    assert np.max(np.abs(result.coefficient_vector / result.standard_errors)) < 5.0


def test_derived_quantities_have_propagated_covariance():
    coefficients = synthetic_states()["mixed_off_diagonal"]
    plus, minus = sample_angular_density(coefficients, 30000, 73)
    sample = AnalyzerSample(
        plus, minus, np.ones(len(plus)), None, Path("synthetic"),
        "lepton_collider_paper_v1", {},
    )
    result = estimate_moments(sample)
    linear = derive_linear_quantities(result)
    connected = derive_connected_correlation(result)
    assert linear.covariance.shape == (len(linear.names), len(linear.names))
    assert connected.covariance.shape == (9, 9)
    assert "D_lc_1" in linear.names
    assert "Cconn_kr" in connected.names
