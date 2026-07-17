import numpy as np
from qis_ttbar.models import FourVector
from qis_ttbar.physics.bases import build_krn_basis


def test_krn_basis_orthonormal():
    beam = FourVector(250, 0, 0, 250)
    top = FourVector(250, 100, 20, 120)
    bar = FourVector(250, -100, -20, -120)
    basis = build_krn_basis(beam, top, bar)
    assert np.allclose(basis.top_axes.T @ basis.top_axes, np.eye(3), atol=1e-12)
    assert np.linalg.det(basis.top_axes) > 0
    assert np.linalg.det(basis.antitop_axes) > 0
