from pathlib import Path
from qis_ttbar.config import load_config

ROOT=Path(__file__).resolve().parents[2]

def test_all_configs_load():
    assert load_config(ROOT/"configs/qis/level_a_500GeV_ISR_sc_v1.yaml").level=="A"
    assert load_config(ROOT/"configs/qis/level_b_detector.yaml").level=="B"
    assert load_config(ROOT/"configs/qis/level_c_research.yaml").level=="C"
