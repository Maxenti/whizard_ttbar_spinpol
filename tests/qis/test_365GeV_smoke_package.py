from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml


REPO = Path(__file__).resolve().parents[2]


def load_module(relative: str, name: str):
    path = REPO / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pilot():
    return yaml.safe_load((REPO / "configs/qis/paper_spin_365GeV_pilot.yaml").read_text())


def qualified_isr_template() -> str:
    return """! META sample_id=ee_ttbar_epmum_LR100_sc_ISR_500GeV
! META initial_state=ee
! META sqrt_s_GeV=500
! META decay_channel=epmum
! META polarization=LR100
! META spin_mode=sc
! META isr_enabled=true
! META seed=111001
! META requested_events=10000
! Qualified ISR structure is retained below.
$ISR_HANDLER = \"qualified-placeholder-for-test\"
process tt_prod = e1, E1 => t, tbar
process t_decay = t => b, E1, n1
process tbar_decay = tbar => bbar, e2, N2
sqrts = 500 GeV
seed = 111001
n_events = 10000
$sample = \"ee_ttbar_epmum_LR100_sc_ISR_500GeV\"
"""


def test_365_configs_pass_contract_checks():
    module = load_module(
        "scripts/qis/validate_365GeV_threshold_inputs.py",
        "validate_365",
    )
    paper = yaml.safe_load((REPO / "configs/qis/paper_spin_365GeV.yaml").read_text())
    sm = yaml.safe_load((REPO / "configs/qis/paper_spin_365GeV_sm_parameters.yaml").read_text())
    checks = module.config_checks(paper, pilot(), sm)
    assert [check for check in checks if check["status"] != "pass"] == []


def test_non_isr_template_is_rejected(tmp_path: Path):
    module = load_module("scripts/qis/prepare_365GeV_smoke.py", "prepare_365_nonisr")
    source = qualified_isr_template().replace("isr_enabled=true", "isr_enabled=false")
    path = tmp_path / "input.sin"
    path.write_text(source)
    with pytest.raises(ValueError, match="not an eligible qualified 500 GeV ISR source"):
        module.require_template_contract(path, pilot())


def test_sindarin_transform_normalizes_metadata():
    module = load_module("scripts/qis/prepare_365GeV_smoke.py", "prepare_365_transform")
    source = qualified_isr_template()
    transformed, counts, checks = module.transform_input(source, pilot())
    assert counts["sqrts_assignments"] == 1
    assert counts["event_assignments"] == 1
    assert counts["seed_assignments"] == 1
    assert all(check["status"] == "pass" for check in checks)
    assert transformed.count("! META sample_id=") == 1
    assert transformed.count("! META isr_enabled=true") == 1
    assert transformed.count("! META requested_events=200") == 1
    assert "! META requested_events=10000" not in transformed
    assert "! META seed=111001" not in transformed
    assert "500GeV" not in transformed
    assert "sqrts = 365 GeV" in transformed
    assert "n_events = 200" in transformed
    assert "seed = 365001" in transformed
    assert "$ISR_HANDLER" in transformed


def test_prepared_contract_detects_stale_metadata():
    module = load_module("scripts/qis/prepare_365GeV_smoke.py", "prepare_365_stale")
    transformed, _, _ = module.transform_input(qualified_isr_template(), pilot())
    broken = transformed + "! META isr_enabled=false\n"
    checks = module.prepared_contract_checks(broken, pilot())
    failures = {item["check"] for item in checks if item["status"] != "pass"}
    assert "prepared_meta_isr_enabled" in failures
    assert "prepared_no_isr_false" in failures


def test_sindarin_transform_accepts_template_event_placeholder():
    module = load_module(
        "scripts/qis/prepare_365GeV_smoke.py",
        "prepare_365_placeholder_events",
    )
    source = qualified_isr_template().replace(
        "n_events = 10000",
        "n_events = @REQUESTED_EVENTS@  ! rendered by production tooling",
    )
    transformed, counts, checks = module.transform_input(source, pilot())
    assert counts["event_assignments"] == 1
    assert all(check["status"] == "pass" for check in checks)
    assert (
        "n_events = 200  ! rendered by production tooling"
        in transformed
    )
    assert "@REQUESTED_EVENTS@" not in transformed


def test_sindarin_transform_accepts_production_placeholders_together():
    module = load_module(
        "scripts/qis/prepare_365GeV_smoke.py",
        "prepare_365_all_placeholders",
    )
    source = qualified_isr_template()
    source = source.replace("! META seed=111001", "! META seed=__SEED__")
    source = source.replace(
        "! META requested_events=10000",
        "! META requested_events=__N_EVENTS__",
    )
    source = source.replace("seed = 111001", "seed = __SEED__")
    source = source.replace("n_events = 10000", "n_events = __N_EVENTS__")
    source = source.replace(
        '$sample = "ee_ttbar_epmum_LR100_sc_ISR_500GeV"',
        '$sample = "__OUTPUT_SAMPLE__"',
    )
    source = source.replace(
        "! META sample_id=ee_ttbar_epmum_LR100_sc_ISR_500GeV",
        "! META campaign_id=500GeV_ISR_sc_v1\n"
        "! META sample_id=ee_ttbar_epmum_LR100_sc_ISR_500GeV",
    )

    transformed, counts, checks = module.transform_input(source, pilot())

    assert counts["event_assignments"] == 1
    assert counts["seed_assignments"] == 1
    assert counts["sample_assignments"] == 1
    assert all(check["status"] == "pass" for check in checks)
    assert "seed = 365001" in transformed
    assert "n_events = 200" in transformed
    assert (
        '$sample = "ee_ttbar_epmum_LR100_sc_ISR_365GeV"'
        in transformed
    )
    assert "__SEED__" not in transformed
    assert "__N_EVENTS__" not in transformed
    assert "__OUTPUT_SAMPLE__" not in transformed
    assert "500GeV_ISR_sc_v1" not in transformed
    assert "! META campaign_id=paper_spin_365GeV_pilot_v1p1" in transformed


def test_threshold_validator_accepts_repository_e_fourvector():
    module = load_module(
        "scripts/qis/validate_365GeV_threshold_inputs.py",
        "validate_365_e_vector",
    )

    class RepositoryFourVector:
        def __init__(self, e, px, py, pz):
            self.e = e
            self.px = px
            self.py = py
            self.pz = pz

    vector = RepositoryFourVector(10.0, 1.0, 2.0, 3.0)
    assert module.p4_values(vector) == (10.0, 1.0, 2.0, 3.0)
    assert module.mass(module.p4_values(vector)) == pytest.approx(\
        (10.0**2 - 1.0**2 - 2.0**2 - 3.0**2) ** 0.5
    )


def test_threshold_validator_retains_energy_fourvector_compatibility():
    module = load_module(
        "scripts/qis/validate_365GeV_threshold_inputs.py",
        "validate_365_energy_vector",
    )

    class AnalysisFourVector:
        def __init__(self, energy, px, py, pz):
            self.energy = energy
            self.px = px
            self.py = py
            self.pz = pz

    vector = AnalysisFourVector(12.0, 4.0, 0.0, 0.0)
    assert module.p4_values(vector) == (12.0, 4.0, 0.0, 0.0)
