from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO = Path(__file__).resolve().parents[2]

SC_QIS_CONFIG = (
    REPO
    / "configs"
    / "qis"
    / "qualification_365GeV_ee_sc_v1.yaml"
)

ISO_QIS_CONFIG = (
    REPO
    / "configs"
    / "qis"
    / "qualification_365GeV_ee_iso_v1.yaml"
)

SC_PRODUCTION_CONFIG = (
    REPO
    / "configs"
    / "production"
    / "production_365GeV_ee_sc_v1.csv"
)

ISO_PRODUCTION_CONFIG = (
    REPO
    / "configs"
    / "production"
    / "production_365GeV_ee_iso_v1.csv"
)

WRAPPER = (
    REPO
    / "scripts"
    / "qis"
    / "run_365GeV_ee_spin15_gate.sh"
)

VALIDATOR = (
    REPO
    / "scripts"
    / "qis"
    / "validate_spin15_gate.py"
)

CAMPAIGN_ID = "paper_spin_365GeV_lhe_matrix_10k_v1"

EXPECTED_SC = {
    "ee_ttbar_epmum_LR100_sc_ISR_365GeV",
    "ee_ttbar_epmum_RL100_sc_ISR_365GeV",
    "ee_ttbar_mupem_LR100_sc_ISR_365GeV",
    "ee_ttbar_mupem_RL100_sc_ISR_365GeV",
}

EXPECTED_ISO = {
    "ee_ttbar_epmum_LR100_iso_ISR_365GeV",
    "ee_ttbar_epmum_RL100_iso_ISR_365GeV",
    "ee_ttbar_mupem_LR100_iso_ISR_365GeV",
    "ee_ttbar_mupem_RL100_iso_ISR_365GeV",
}


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())

    assert isinstance(payload, dict)

    return payload


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "spin15_validator_for_contract_test",
        VALIDATOR,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


@pytest.mark.parametrize(
    ("path", "spin_mode", "expected_samples"),
    [
        (SC_QIS_CONFIG, "sc", EXPECTED_SC),
        (ISO_QIS_CONFIG, "iso", EXPECTED_ISO),
    ],
)
def test_qis_config_contract(
    path: Path,
    spin_mode: str,
    expected_samples: set[str],
) -> None:
    config = load_yaml(path)

    assert config["schema_version"] == 2
    assert config["level"] == "A"

    campaign = config["campaign"]
    inputs = config["inputs"]
    showering = config["showering"]

    assert campaign["source_campaign_id"] == CAMPAIGN_ID
    assert campaign["negative_lepton_defines_plus_z"] is True

    assert inputs["mode"] == "manifest"
    assert inputs["allowed_initial_states"] == ["ee"]
    assert set(inputs["allowed_polarizations"]) == {"LR100", "RL100"}
    assert set(inputs["allowed_decay_channels"]) == {"epmum", "mupem"}
    assert inputs["allowed_spin_modes"] == [spin_mode]

    assert config["physics"]["basis_order"] == ["k", "r", "n"]
    assert (
        config["physics"]["antitop_axis_convention"]
        == "particle_helicity_right_handed"
    )
    assert config["physics"]["antitop_analyzer_sign"] == -1.0

    assert config["physics"]["top_mass_GeV"] == pytest.approx(173.1)
    assert config["physics"]["w_mass_GeV"] == pytest.approx(80.379)

    assert showering["total_events_per_sample"] == 10_000
    assert showering["default_jobs_per_sample"] == 10

    assert (
        showering["lhe_preparation_policy"]
        == "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3"
    )

    assert showering["qed_shower_by_gamma"] is True
    assert showering["preserve_whizard_top_decays"] is True
    assert showering["preserve_whizard_w_decay_kinematics"] is True

    source_manifest_name = Path(
        campaign["source_manifest"]
    ).name

    assert source_manifest_name == (
        f"source_manifest_ee_{spin_mode}.csv"
    )

    assert all(
        sample.endswith(f"_{spin_mode}_ISR_365GeV")
        for sample in expected_samples
    )


@pytest.mark.parametrize(
    ("path", "spin_correlated", "expected_samples"),
    [
        (SC_PRODUCTION_CONFIG, True, EXPECTED_SC),
        (ISO_PRODUCTION_CONFIG, False, EXPECTED_ISO),
    ],
)
def test_production_csv_contract(
    path: Path,
    spin_correlated: bool,
    expected_samples: set[str],
) -> None:
    rows = read_csv(path)

    assert len(rows) == 4
    assert {row["sample_id"] for row in rows} == expected_samples
    assert {row["campaign_id"] for row in rows} == {CAMPAIGN_ID}
    assert {row["initial_state"] for row in rows} == {"ee"}
    assert {row["sqrt_s_GeV"] for row in rows} == {"365"}

    assert {row["decay_channel"] for row in rows} == {
        "epmum",
        "mupem",
    }

    assert {row["polarization"] for row in rows} == {
        "LR100",
        "RL100",
    }

    assert all(row["enabled"] == "true" for row in rows)
    assert all(row["beam1"] == "e1" for row in rows)
    assert all(row["beam2"] == "E1" for row in rows)

    assert all(
        row["beam1_pol_fraction"] == "1.0"
        for row in rows
    )

    assert all(
        row["beam2_pol_fraction"] == "1.0"
        for row in rows
    )

    assert all(row["isr_enabled"] == "true" for row in rows)
    assert all(row["beam_spectrum"] == "none" for row in rows)
    assert all(row["n_shards"] == "1" for row in rows)
    assert all(row["events_per_shard"] == "10000" for row in rows)

    for row in rows:
        expected_helicities = {
            "LR100": ("-1", "1"),
            "RL100": ("1", "-1"),
        }[row["polarization"]]

        assert (
            row["beam1_helicity"],
            row["beam2_helicity"],
        ) == expected_helicities

        assert (
            row["spin_correlated"] == "true"
        ) is spin_correlated


def test_validator_accepts_production_configs() -> None:
    validator = load_validator()

    sc_rows = validator.audit_production_config(
        SC_PRODUCTION_CONFIG
    )

    iso_rows = validator.audit_production_config(
        ISO_PRODUCTION_CONFIG
    )

    assert len(sc_rows) == 4
    assert len(iso_rows) == 4

    assert all(row["status"] == "pass" for row in sc_rows)
    assert all(row["status"] == "pass" for row in iso_rows)


def test_sc_iso_sample_matrix_is_disjoint_and_complete() -> None:
    assert EXPECTED_SC.isdisjoint(EXPECTED_ISO)
    assert len(EXPECTED_SC | EXPECTED_ISO) == 8


def test_wrapper_shell_syntax() -> None:
    result = subprocess.run(
        ["bash", "-n", str(WRAPPER)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr


def test_wrapper_has_365_specific_defaults() -> None:
    text = WRAPPER.read_text()

    required_fragments = [
        "qualification_365GeV_ee_sc_v1.yaml",
        "qualification_365GeV_ee_iso_v1.yaml",
        "production_365GeV_ee_sc_v1.csv",
        "production_365GeV_ee_iso_v1.csv",
        "paper_spin_365GeV_ee_spin15_10k_v1",
        "MAX_EVENTS=${MAX_EVENTS:-10000}",
        "STRICT_PHYSICS=${STRICT_PHYSICS:-1}",
    ]

    for fragment in required_fragments:
        assert fragment in text

    assert "qualification_500GeV" not in text
    assert "production_500GeV" not in text
