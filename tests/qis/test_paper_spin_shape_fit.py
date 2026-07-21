import os
import subprocess
import sys
from pathlib import Path


def test_simultaneous_shape_fit_is_physical_and_closes():
    code = r'''
from pathlib import Path
import numpy as np
from qis_ttbar.paper_spin.io import AnalyzerSample
from qis_ttbar.paper_spin.moments import estimate_moments
from qis_ttbar.paper_spin.shape_fit import fit_physical_density_matrix
from qis_ttbar.paper_spin.synthetic import sample_angular_density, synthetic_states
injected = synthetic_states()["mixed_off_diagonal"]
plus, minus = sample_angular_density(injected, 8000, 823)
sample = AnalyzerSample(
    plus, minus, np.ones(len(plus)), None, Path("synthetic"),
    "lepton_collider_paper_v1", {},
)
moments = estimate_moments(sample)
fit = fit_physical_density_matrix(
    sample, moments.coefficient_vector, max_iterations=600,
    calculate_covariance=False,
)
assert fit.success
assert fit.min_pdf_bracket > 0.0
assert np.max(np.abs(fit.coefficient_vector - injected)) < 0.18
'''
    environment = dict(os.environ)
    root = Path(__file__).resolve().parents[2]
    environment["PYTHONPATH"] = str(root) + os.pathsep + environment.get("PYTHONPATH", "")
    completed = subprocess.run(
        [sys.executable, "-c", code],
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
