import numpy as np
from qis_ttbar.tomography.estimators import estimate_moments
from qis_ttbar.tomography.bootstrap import bootstrap_tomography


def test_isotropic_moments_near_zero():
    rng = np.random.default_rng(123)
    n = 200000
    def sphere():
        x = rng.normal(size=(n,3)); return x / np.linalg.norm(x, axis=1)[:,None]
    result = estimate_moments(sphere(), sphere())
    assert np.max(np.abs(result.b_plus)) < 0.03
    assert np.max(np.abs(result.b_minus)) < 0.03
    assert np.max(np.abs(result.correlation)) < 0.04


def test_bootstrap_reproducible():
    rng = np.random.default_rng(5)
    plus = rng.normal(size=(200,3)); plus /= np.linalg.norm(plus,axis=1)[:,None]
    minus = rng.normal(size=(200,3)); minus /= np.linalg.norm(minus,axis=1)[:,None]
    a = bootstrap_tomography(plus, minus, replicas=20, seed=7)
    b = bootstrap_tomography(plus, minus, replicas=20, seed=7)
    assert np.allclose(a.replicas, b.replicas)
