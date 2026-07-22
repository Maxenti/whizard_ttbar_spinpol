from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]


def load_module(relative: str, name: str):
    path = REPO / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_module(
    "scripts/qis/paper_spin_365_matrix_common.py",
    "paper_spin_365_matrix_common_test",
)
COLLECTOR = load_module(
    "scripts/qis/collect_365GeV_lhe_matrix.py",
    "collect_365_matrix_test",
)


def fixture_template(sample) -> str:
    beam_minus, beam_plus = COMMON.expected_beam_particles(sample.initial_state)
    top_daughters, antitop_daughters = COMMON.expected_decay_processes(
        sample.decay_channel
    )
    h1, h2 = COMMON.expected_helicities(sample.polarization)
    iso = "true" if sample.spin_mode == "iso" else "false"
    return f"""! META campaign_id=500GeV_ISR_{sample.spin_mode}_v1
! META sample_id={sample.source_sample_id}
! META initial_state={sample.initial_state}
! META sqrt_s_GeV=500
! META decay_channel={sample.decay_channel}
! META polarization={sample.polarization}
! META spin_mode={sample.spin_mode}
! META isr_enabled=true
! META seed=__SEED__
! META requested_events=__N_EVENTS__
model = SM
process tt_prod = {beam_minus}, {beam_plus} => t, tbar
process t_decay = t => {', '.join(top_daughters)}
process tbar_decay = tbar => {', '.join(antitop_daughters)}
sqrts = 500 GeV
beams = {beam_minus}, {beam_plus} => isr
?isr_handler = true
$isr_handler_mode = "recoil"
isr_mass = 0.000510997 GeV
isr_alpha = 0.0072973525693
beams_pol_density = @({h1:+d}), @({h2:+d})
beams_pol_fraction = 100%, 100%
?diagonal_decay = false
?isotropic_decay = {iso}
seed = __SEED__
n_events = __N_EVENTS__
sample_format = lhef
$sample = "__OUTPUT_SAMPLE__"
simulate (tt_prod) {{
  ?polarized_events = true
}}
"""


def test_matrix_is_complete_and_deterministic():
    matrix = COMMON.build_matrix(
        events=1000,
        seed_base=3651000,
        output_root="runs/test",
    )
    assert len(matrix) == 16
    assert len({sample.sample_id for sample in matrix}) == 16
    assert len({sample.source_sample_id for sample in matrix}) == 16
    assert [sample.index for sample in matrix] == list(range(1, 17))
    assert [sample.random_seed for sample in matrix] == list(
        range(3651001, 3651017)
    )


def test_all_16_production_template_forms_materialize():
    campaign_id = "paper_spin_365GeV_lhe_matrix_pilot_v1"
    matrix = COMMON.build_matrix(
        events=1000,
        seed_base=3651000,
        output_root="runs/test",
    )
    for sample in matrix:
        source = fixture_template(sample)
        transformed, counts, checks = COMMON.transform_template(
            source,
            campaign_id,
            sample,
        )
        assert all(check["status"] == "pass" for check in checks)
        assert counts["sqrts_assignments"] == 1
        assert counts["seed_assignments"] == 1
        assert counts["event_assignments"] == 1
        assert counts["sample_assignments"] == 1
        assert f"sqrts = 365 GeV" in transformed
        assert f"seed = {sample.random_seed}" in transformed
        assert f"n_events = {sample.events}" in transformed
        assert f'$sample = "{sample.sample_id}"' in transformed
        assert sample.source_sample_id not in transformed
        assert "500GeV" not in transformed
        assert "__SEED__" not in transformed
        assert "__N_EVENTS__" not in transformed
        assert "__OUTPUT_SAMPLE__" not in transformed


def test_non_isr_source_is_rejected():
    sample = COMMON.build_matrix(
        events=1000,
        seed_base=3651000,
        output_root="runs/test",
    )[0]
    source = fixture_template(sample).replace(
        "! META isr_enabled=true", "! META isr_enabled=false"
    )
    with pytest.raises(ValueError, match="source template contract"):
        COMMON.transform_template(
            source,
            "paper_spin_365GeV_lhe_matrix_pilot_v1",
            sample,
        )


def test_cross_section_comparison_pull():
    left = {
        "sample_id": "left",
        "cross_section_pb": 1.000,
        "cross_section_error_pb": 0.010,
    }
    right = {
        "sample_id": "right",
        "cross_section_pb": 1.020,
        "cross_section_error_pb": 0.010,
    }
    row = COLLECTOR.comparison(
        name="test",
        left=left,
        right=right,
        maximum_pull=5.0,
    )
    assert row["status"] == "pass"
    assert 1.4 < abs(row["pull"]) < 1.5
