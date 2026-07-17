import numpy as np

from qis_ttbar.tomography.density import density_matrix_from_coefficients, validate_density_matrix
from qis_ttbar.tomography.fit import fit_physical_density_matrix


def test_physical_fit_remains_finite_for_unphysical_moments():
    rho = density_matrix_from_coefficients(
        np.array([1.8, -0.7, 0.4]),
        np.array([-1.4, 0.2, 0.9]),
        np.array([[1.7, 0.8, -0.6], [0.5, -1.3, 0.7], [0.4, -0.9, 1.2]]),
    )
    result = fit_physical_density_matrix(rho, max_iterations=200)
    assert np.all(np.isfinite(result.rho))
    assert validate_density_matrix(result.rho).valid
    assert np.isfinite(result.objective)
