from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.distribution_fit import fit_marginal_coefficients
from qis_ttbar.paper_spin.io import AnalyzerSample
from qis_ttbar.paper_spin.moments import estimate_moments
from qis_ttbar.paper_spin.synthetic import sample_angular_density, synthetic_states


def test_marginal_fit_recovers_physical_injection():
    injected = synthetic_states()["mixed_off_diagonal"]
    plus, minus = sample_angular_density(injected, 80000, 5501)
    sample = AnalyzerSample(
        plus, minus, np.ones(len(plus)), None, Path("synthetic"),
        "lepton_collider_paper_v1", {},
    )
    marginal = fit_marginal_coefficients(sample)
    moments = estimate_moments(sample)
    combined = np.sqrt(marginal.standard_errors**2 + moments.standard_errors**2)
    assert all(item.success for item in marginal.scalar_fits.values())
    assert np.max(np.abs(marginal.coefficient_vector - injected) / combined) < 5.0
    d_trace_moment = (
        moments.coefficients["Ckk"] + moments.coefficients["Crr"] + moments.coefficients["Cnn"]
    ) / 3.0
    assert abs(marginal.trace_fit.value - d_trace_moment) < 0.05
