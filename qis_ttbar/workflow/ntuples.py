from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd

from ..io.lhe import extract_ttbar_truth, iter_lhe_events
from ..io.hepmc import iter_hepmc_ttbar
from ..io.manifest import SampleRecord
from ..io.tables import write_table
from ..physics.observables import truth_to_row


def build_ntuple_for_sample(
    record: SampleRecord,
    *, input_path: str | Path | None = None,
    input_format: str = "lhe",
    output_base: str | Path,
    max_events: int | None = None,
    basis_order: tuple[str, str, str] = ("k", "r", "n"),
    antitop_analyzer_sign: float = -1.0,
    alpha_plus: float = 1.0,
    alpha_minus: float = 1.0,
    write_parquet: bool = True,
    write_root: bool = True,
    write_csv: bool = True,
) -> dict[str, object]:
    path = Path(input_path) if input_path else record.merged_final_lhe_path
    rows = []
    if input_format == "lhe":
        truths = (extract_ttbar_truth(event, record.initial_state) for event in iter_lhe_events(path, max_events))
    elif input_format == "hepmc3":
        truths = iter_hepmc_ttbar(path, initial_state=record.initial_state, max_events=max_events)
    else:
        raise ValueError(f"unsupported input format: {input_format}")
    for truth in truths:
        row = truth_to_row(
            truth, basis_order=basis_order, antitop_analyzer_sign=antitop_analyzer_sign,
            alpha_plus=alpha_plus, alpha_minus=alpha_minus,
        )
        row.update({
            "campaign_id": record.campaign_id, "sample_id": record.sample_id,
            "polarization": record.polarization,
            "inclusive_cross_section_fb": record.inclusive_cross_section_fb,
            "exclusive_cross_section_fb": record.exclusive_cross_section_fb,
            "forced_decay_weight": record.forced_decay_weight,
            "source_path": str(path), "input_format": input_format,
        })
        rows.append(row)
    frame = pd.DataFrame(rows)
    outputs = write_table(frame, output_base, parquet=write_parquet, root=write_root, csv=write_csv)
    summary = {
        "campaign_id": record.campaign_id, "sample_id": record.sample_id,
        "source": str(path), "input_format": input_format, "events": len(frame),
        "outputs": outputs,
    }
    summary_path = Path(output_base).with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary
