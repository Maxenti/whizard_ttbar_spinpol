from pathlib import Path
import pytest
from qis_ttbar.io.lhe import iter_lhe_events, parse_lhe_header, extract_ttbar_truth
from qis_ttbar.physics.observables import event_observables

DATA = Path(__file__).parent / "data/smoke_lhe"
FILES = sorted(DATA.glob("*.lhe"))


@pytest.mark.parametrize("path", FILES)
def test_smoke_lhe_parse(path):
    header = parse_lhe_header(path)
    assert header.declared_events == 200
    events = list(iter_lhe_events(path, max_events=5))
    assert len(events) == 5
    initial = "mumu" if path.name.startswith("mumu") else "ee"
    for event in events:
        truth = extract_ttbar_truth(event, initial)
        obs = event_observables(truth)
        assert truth.decay_channel in {"epmum", "mupem"}
        assert obs["mtt_GeV"] > 2 * 170
        assert obs["top_decay_closure_valid"]
