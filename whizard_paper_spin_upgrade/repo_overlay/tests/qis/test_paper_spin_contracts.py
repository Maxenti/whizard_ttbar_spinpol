import numpy as np
import pandas as pd

from qis_ttbar.paper_spin.contracts import (
    COEFFICIENT_NAMES,
    coefficient_vector_to_parts,
    parts_to_coefficient_vector,
)
from qis_ttbar.paper_spin.io import frame_to_analyzers, load_config


def test_coefficient_contract_roundtrip():
    vector = np.arange(15, dtype=float) / 20.0
    b1, b2, c = coefficient_vector_to_parts(vector)
    assert np.allclose(parts_to_coefficient_vector(b1, b2, c), vector)
    assert len(COEFFICIENT_NAMES) == 15
    assert len(set(COEFFICIENT_NAMES)) == 15


def test_legacy_negative_lepton_map_is_explicit():
    frame = pd.DataFrame(
        {
            "b1k": [1.0], "b1r": [0.0], "b1n": [0.0],
            "b2k": [0.0], "b2r": [1.0], "b2n": [0.0],
            "event_id": [7],
        }
    )
    sample = frame_to_analyzers(frame, "memory", load_config(None))
    assert np.allclose(sample.plus[0], [1.0, 0.0, 0.0])
    assert np.allclose(sample.minus[0], [0.0, -1.0, 0.0])
    assert sample.event_keys[0] == 7
