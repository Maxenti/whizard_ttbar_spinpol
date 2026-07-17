import numpy as np
from qis_ttbar.tomography.density import (
    coefficients_from_density_matrix,
    density_matrix_from_coefficients,
    project_density_matrix,
    validate_density_matrix,
)
from qis_ttbar.validation import synthetic_states
from qis_ttbar.qis.measures import all_measures


def test_roundtrip_coefficients():
    bp = np.array([0.1, -0.2, 0.05])
    bm = np.array([-0.1, 0.02, 0.03])
    c = np.diag([-0.2, 0.1, 0.3])
    rho = density_matrix_from_coefficients(bp, bm, c)
    bp2, bm2, c2 = coefficients_from_density_matrix(rho)
    assert np.allclose(bp, bp2)
    assert np.allclose(bm, bm2)
    assert np.allclose(c, c2)


def test_projection_is_physical():
    rho = density_matrix_from_coefficients([2, 0, 0], [0, 0, 0], np.zeros((3,3)))
    projected = project_density_matrix(rho)
    assert validate_density_matrix(projected).valid


def test_singlet_measures():
    values = all_measures(synthetic_states()["singlet"])
    assert np.isclose(values["concurrence"], 1.0)
    assert np.isclose(values["negativity"], 0.5)
    assert np.isclose(values["chsh_max"], 2*np.sqrt(2))
