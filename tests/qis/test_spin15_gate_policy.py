from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "qis" / "validate_spin15_gate.py"
SPEC = importlib.util.spec_from_file_location("validate_spin15_gate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def thresholds():
    return MODULE.GateThresholds(
        preservation_max_abs=0.02,
        preservation_max_z=5.0,
        polarization_min_z=5.0,
        spin_correlation_min_z=5.0,
        flavour_consistency_max_z=5.0,
    )


def coefficient_row(
    *,
    dataset: str,
    spin_mode: str,
    polarization: str,
    observable: str,
    coefficient: float,
    coefficient_se: float,
):
    return {
        "dataset": dataset,
        "initial_state": "ee",
        "decay_channel": "epmum",
        "polarization": polarization,
        "spin_mode": spin_mode,
        "sqrt_s_GeV": 500,
        "observable": observable,
        "coefficient": coefficient,
        "coefficient_se": coefficient_se,
    }


def test_preservation_requires_large_and_significant_shift_to_fail():
    rows = []
    for observable in MODULE.SPIN15_EVENT_COLUMNS:
        lhe = 0.0
        hepmc = 0.0
        lhe_se = 0.01
        hepmc_se = 0.01
        if observable == "b1k":
            hepmc = 0.03  # large but only ~2.1 sigma
        elif observable == "b1r":
            hepmc = 0.01
            lhe_se = hepmc_se = 0.0005  # significant but small
        elif observable == "b1n":
            hepmc = 0.03
            lhe_se = hepmc_se = 0.0005  # large and significant
        rows.append(
            coefficient_row(
                dataset="lhe_sc",
                spin_mode="sc",
                polarization="LR100",
                observable=observable,
                coefficient=lhe,
                coefficient_se=lhe_se,
            )
        )
        rows.append(
            coefficient_row(
                dataset="hepmc_sc",
                spin_mode="sc",
                polarization="LR100",
                observable=observable,
                coefficient=hepmc,
                coefficient_se=hepmc_se,
            )
        )

    result = MODULE.preservation_rows(
        pd.DataFrame(rows),
        pairs=(("lhe_sc", "hepmc_sc", "sc"),),
        thresholds=thresholds(),
    )
    by_observable = {row["observable"]: row for row in result}

    assert by_observable["b1k"]["status"] == "warn"
    assert by_observable["b1k"]["large_shift"] is True
    assert by_observable["b1k"]["significant_shift"] is False
    assert by_observable["b1r"]["status"] == "warn"
    assert by_observable["b1r"]["large_shift"] is False
    assert by_observable["b1r"]["significant_shift"] is True
    assert by_observable["b1n"]["status"] == "fail"
    assert by_observable["b1n"]["large_shift"] is True
    assert by_observable["b1n"]["significant_shift"] is True
    assert by_observable["b2r"]["status"] == "pass"


def test_lr_rl_separation_is_not_applicable_to_isotropic_controls():
    rows = []
    for dataset, mode in (("lhe_sc", "sc"), ("lhe_iso", "iso")):
        for observable in MODULE.B_OBSERVABLES:
            rows.append(
                coefficient_row(
                    dataset=dataset,
                    spin_mode=mode,
                    polarization="LR100",
                    observable=observable,
                    coefficient=0.6 if mode == "sc" else 0.01,
                    coefficient_se=0.01,
                )
            )
            rows.append(
                coefficient_row(
                    dataset=dataset,
                    spin_mode=mode,
                    polarization="RL100",
                    observable=observable,
                    coefficient=-0.6 if mode == "sc" else -0.01,
                    coefficient_se=0.01,
                )
            )

    _, groups = MODULE.polarization_rows(
        pd.DataFrame(rows),
        thresholds=thresholds(),
    )
    by_mode = {row["spin_mode"]: row for row in groups}

    assert by_mode["sc"]["status"] == "pass"
    assert by_mode["iso"]["status"] == "not_applicable"
