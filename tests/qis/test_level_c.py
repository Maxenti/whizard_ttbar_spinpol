import numpy as np
from qis_ttbar.level_c.polarization import longitudinal_mixture_weights
from qis_ttbar.level_c.optimized_bases import optimize_correlation_basis
from qis_ttbar.level_c.eft import fit_polynomial_weights


def test_longitudinal_basis_weights():
    lr = longitudinal_mixture_weights(-1, 1)
    assert lr.lr == 1 and lr.rl == lr.ll == lr.rr == 0


def test_optimized_basis_diagonalizes():
    c=np.array([[.2,.1,0],[0,.3,.1],[.1,0,-.4]])
    result=optimize_correlation_basis(c)
    off=result.diagonal_correlation-np.diag(np.diag(result.diagonal_correlation))
    assert np.linalg.norm(off)<1e-10


def test_eft_quadratic_fit():
    points=[{"c":x} for x in (-1.,0.,1.)]
    weights=np.array([[1.,2.],[2.,3.],[5.,6.]])
    model=fit_polynomial_weights(["c"],points,weights,order=2)
    assert np.allclose(model.weights({"c":0}),weights[1])


def test_cross_section_weighted_polarization_mixture():
    from qis_ttbar.level_c.polarization import mix_helicity_density_matrices
    rho_lr = np.diag([1.0, 0.0, 0.0, 0.0]).astype(complex)
    rho_rl = np.diag([0.0, 0.0, 0.0, 1.0]).astype(complex)
    result = mix_helicity_density_matrices(
        {"lr": rho_lr, "rl": rho_rl},
        {"lr": 2.0, "rl": 1.0, "ll": 0.0, "rr": 0.0},
        p_minus=0.0,
        p_plus=0.0,
    )
    assert np.isclose(result.cross_section, 0.75)
    assert np.isclose(result.rho[0, 0], 2.0 / 3.0)
    assert np.isclose(result.rho[3, 3], 1.0 / 3.0)


def test_transverse_beam_density_matrix_physical():
    from qis_ttbar.level_c.polarization import beam_spin_density_matrix
    rho = beam_spin_density_matrix(longitudinal=0.3, transverse=0.4, azimuth=0.7)
    assert np.isclose(np.trace(rho), 1.0)
    assert np.min(np.linalg.eigvalsh(rho)) >= -1e-12
