import numpy as np
from qis_ttbar.models import FourVector
from qis_ttbar.level_b.detector import DetectorResponse, ResponseConfig
from qis_ttbar.level_b.unfolding import iterative_bayes_unfold, tikhonov_unfold


def test_detector_determinism():
    p = FourVector(50, 30, 20, 30)
    a = DetectorResponse(ResponseConfig(), seed=1).smear_lepton(p)
    b = DetectorResponse(ResponseConfig(), seed=1).smear_lepton(p)
    assert a == b


def test_unfolding_identity():
    measured = np.array([10.,20.,30.])
    response = np.eye(3)
    assert np.allclose(iterative_bayes_unfold(measured,response,iterations=2), measured)
    unfolded,_ = tikhonov_unfold(measured,response,regularization=0)
    assert np.allclose(unfolded, measured)
