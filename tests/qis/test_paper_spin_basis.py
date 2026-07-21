import numpy as np

from qis_ttbar.paper_spin.basis import boost_four_vectors, reconstruct_analyzers


def test_independent_basis_and_rest_frame_reconstruction():
    mt = 172.5
    energy = 250.0
    momentum = np.sqrt(energy**2 - mt**2)
    costheta = 0.3
    sintheta = np.sqrt(1.0 - costheta**2)
    k = np.array([sintheta, 0.0, costheta])
    top = np.array([[energy, *(momentum * k)]])
    antitop = np.array([[energy, *(-momentum * k)]])
    incoming_positive = np.array([[250.0, 0.0, 0.0, 250.0]])

    lepton_energy = 40.0
    lplus_rest = np.array([[lepton_energy, *(lepton_energy * k)]])
    lminus_rest = np.array([[lepton_energy, *(-lepton_energy * k)]])
    top_beta = top[:, 1:] / top[:, 0, None]
    antitop_beta = antitop[:, 1:] / antitop[:, 0, None]
    lplus = boost_four_vectors(lplus_rest, top_beta)
    lminus = boost_four_vectors(lminus_rest, antitop_beta)

    result = reconstruct_analyzers(
        incoming_positive, top, antitop, lplus, lminus
    )
    assert not result.singular[0]
    assert result.orthonormal_residual[0] < 1e-12
    assert np.isclose(result.handedness[0], -1.0, atol=1e-12)
    assert np.allclose(result.plus[0], [1.0, 0.0, 0.0], atol=1e-12)
    assert np.allclose(result.minus[0], [1.0, 0.0, 0.0], atol=1e-12)
