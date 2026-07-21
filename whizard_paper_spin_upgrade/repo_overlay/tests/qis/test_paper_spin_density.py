import numpy as np

from qis_ttbar.paper_spin.density import (
    all_density_measures,
    coefficients_from_density_matrix,
    density_matrix_from_coefficients,
    project_density_matrix,
    validate_density_matrix,
)
from qis_ttbar.paper_spin.synthetic import synthetic_states


def test_density_roundtrip_all_synthetic_states():
    for coefficients in synthetic_states().values():
        rho = density_matrix_from_coefficients(coefficients)
        assert validate_density_matrix(rho).valid
        recovered = coefficients_from_density_matrix(rho)
        assert np.allclose(recovered, coefficients, atol=1e-11)


def test_exact_psd_trace_one_projection():
    vector = np.zeros(15)
    vector[0] = 1.8
    raw = density_matrix_from_coefficients(vector)
    assert not validate_density_matrix(raw).valid
    projection = project_density_matrix(raw)
    assert validate_density_matrix(projection.rho).valid
    assert np.isclose(np.trace(projection.rho), 1.0)


def test_singlet_quantum_measures():
    rho = density_matrix_from_coefficients(synthetic_states()["singlet"])
    measures = all_density_measures(rho)
    assert np.isclose(measures["purity"], 1.0)
    assert np.isclose(measures["negativity"], 0.5)
    assert np.isclose(measures["concurrence"], 1.0)
    assert np.isclose(measures["chsh_maximum"], 2.0 * np.sqrt(2.0))
