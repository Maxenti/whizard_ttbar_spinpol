from pathlib import Path

import pytest
import yaml

from qis_ttbar.config import load_config
from qis_ttbar.exceptions import ConfigurationError

ROOT = Path(__file__).resolve().parents[2]


def test_all_configs_load():
    assert load_config(ROOT / "configs/qis/level_a_500GeV_ISR_sc_v1.yaml").level == "A"
    assert load_config(ROOT / "configs/qis/level_b_detector.yaml").level == "B"
    assert load_config(ROOT / "configs/qis/level_c_research.yaml").level == "C"


def _write_level_a_config(tmp_path: Path, schema_version: object) -> Path:
    payload = {
        "schema_version": schema_version,
        "level": "A",
        "campaign": {"output_root": str(tmp_path / "output")},
        "physics": {"basis_order": ["k", "r", "n"]},
        "statistics": {
            "bootstrap_replicas_test": 1,
            "bootstrap_replicas_production": 1,
        },
    }
    path = tmp_path / f"schema_{schema_version}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


def test_schema_2_analysis_config_loads(tmp_path: Path):
    config = load_config(_write_level_a_config(tmp_path, 2))
    assert config.schema_version == 2
    assert config.level == "A"


def test_unsupported_schema_version_fails(tmp_path: Path):
    with pytest.raises(ConfigurationError, match=r"unsupported schema_version 3"):
        load_config(_write_level_a_config(tmp_path, 3))


def test_non_integer_schema_version_fails(tmp_path: Path):
    with pytest.raises(ConfigurationError, match=r"schema_version must be an integer"):
        load_config(_write_level_a_config(tmp_path, "not-an-integer"))
