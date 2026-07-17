from pathlib import Path

import numpy as np
import pytest

from qis_ttbar.io.lhe import extract_ttbar_truth, iter_lhe_events
from qis_ttbar.physics.observables import (
    SPIN15_COEFFICIENT_NAMES,
    SPIN15_EVENT_COLUMNS,
    event_observables,
)

DATA = Path(__file__).parent / "data/smoke_lhe"
FILES = sorted(DATA.glob("*.lhe"))


EXPECTED_EVENT_COLUMNS = (
    "b1k", "b1r", "b1n",
    "b2k", "b2r", "b2n",
    "ckk", "crr", "cnn",
    "ckr", "crk", "ckn", "cnk", "crn", "cnr",
)

EXPECTED_COEFFICIENT_NAMES = (
    "B1k", "B1r", "B1n",
    "B2k", "B2r", "B2n",
    "Ckk", "Crr", "Cnn",
    "Ckr", "Crk", "Ckn", "Cnk", "Crn", "Cnr",
)


def test_spin15_contract_order():
    assert SPIN15_EVENT_COLUMNS == EXPECTED_EVENT_COLUMNS
    assert SPIN15_COEFFICIENT_NAMES == EXPECTED_COEFFICIENT_NAMES
    assert len(SPIN15_EVENT_COLUMNS) == 15
    assert len(set(SPIN15_EVENT_COLUMNS)) == 15


@pytest.mark.parametrize("path", FILES)
def test_spin15_aliases_match_legacy_coordinates(path):
    initial_state = "mumu" if path.name.startswith("mumu") else "ee"
    event = next(iter_lhe_events(path, max_events=1))
    truth = extract_ttbar_truth(event, initial_state)
    observables = event_observables(truth)

    for axis in ("k", "r", "n"):
        assert observables[f"b1{axis}"] == pytest.approx(
            observables[f"uplus_{axis}"], abs=1.0e-14
        )
        assert observables[f"b2{axis}"] == pytest.approx(
            observables[f"uminus_{axis}"], abs=1.0e-14
        )

    for first in ("k", "r", "n"):
        for second in ("k", "r", "n"):
            expected = observables[f"b1{first}"] * observables[f"b2{second}"]
            assert observables[f"c{first}{second}"] == pytest.approx(
                expected, abs=1.0e-14
            )
            assert observables[f"c{first}{second}"] == pytest.approx(
                observables[f"uproduct_{first}{second}"], abs=1.0e-14
            )

    values = np.asarray([observables[name] for name in SPIN15_EVENT_COLUMNS])
    assert np.all(np.isfinite(values))
    assert np.all(values >= -1.0 - 1.0e-12)
    assert np.all(values <= 1.0 + 1.0e-12)


def test_spin15_aliases_are_basis_order_independent():
    path = FILES[0]
    event = next(iter_lhe_events(path, max_events=1))
    truth = extract_ttbar_truth(event, "ee")

    reference = event_observables(truth, basis_order=("k", "r", "n"))
    reordered = event_observables(truth, basis_order=("n", "k", "r"))

    for name in SPIN15_EVENT_COLUMNS:
        assert reordered[name] == pytest.approx(reference[name], abs=1.0e-13)
