import numpy as np

from qis_ttbar.paper_spin.analytic_tree import GEV2_TO_FB, SMParameters, TreeLevelSM
from qis_ttbar.paper_spin.density import validate_density_matrix


def test_massless_qed_fixed_helicity_normalization():
    parameters = SMParameters(
        alpha_em_inverse=137.0,
        sin2_theta_w=0.23122,
        mass_z_GeV=1.0e12,
        width_z_GeV=0.0,
        mass_top_GeV=1.0e-6,
        color_factor=3.0,
    )
    model = TreeLevelSM(parameters)
    prediction = model.integrated_density(500.0, "ee", "LR100", 64)
    expected = (
        2.0
        * 3.0
        * (2.0 / 3.0) ** 2
        * 4.0
        * np.pi
        * parameters.alpha_em**2
        / (3.0 * 500.0**2)
        * GEV2_TO_FB
    )
    assert np.isclose(prediction["cross_section_fb"], expected, rtol=1e-10)
    assert validate_density_matrix(prediction["rho"]).valid


def test_electron_muon_universality_at_500gev():
    parameters = SMParameters(
        alpha_em_inverse=128.0,
        sin2_theta_w=0.23122,
        mass_z_GeV=91.1876,
        width_z_GeV=2.4952,
        mass_top_GeV=172.5,
    )
    model = TreeLevelSM(parameters)
    for polarization in ("LR100", "RL100"):
        ee = model.integrated_density(500.0, "ee", polarization, 48)
        mm = model.integrated_density(500.0, "mumu", polarization, 48)
        assert np.isclose(ee["cross_section_fb"], mm["cross_section_fb"], rtol=2e-6)
        assert np.allclose(ee["coefficient_vector"], mm["coefficient_vector"], atol=2e-6)
