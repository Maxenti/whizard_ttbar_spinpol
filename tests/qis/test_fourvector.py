import numpy as np
from qis_ttbar.models import FourVector


def test_boost_to_rest_frame():
    p = FourVector(10.0, 3.0, 0.0, 0.0)
    rest = p.boost(-p.beta)
    assert np.allclose(rest.spatial, 0.0, atol=1e-12)
    assert np.isclose(rest.e, p.mass, atol=1e-12)


def test_mass_invariant_under_boost():
    p = FourVector(20.0, 2.0, 3.0, 5.0)
    boosted = p.boost([0.1, -0.2, 0.05])
    assert np.isclose(boosted.mass2, p.mass2, atol=1e-10)
