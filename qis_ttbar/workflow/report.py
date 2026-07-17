from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def write_campaign_report(output: str | Path, *, campaign_id: str, sample_summaries: Iterable[dict[str, object]], validation: dict[str, object] | None = None) -> None:
    output = Path(output)
    rows = list(sample_summaries)
    lines = [
        f"# QIS campaign report: {campaign_id}", "",
        "## Scope", "",
        "WHIZARD hard-process events with beam polarization and correlated top decays are processed through a reproducible tomography/QIS workflow.", "",
        "## Samples", "",
        "| Sample | Events | Input format | Source |", "|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row.get('sample_id','')}` | {row.get('events',0)} | {row.get('input_format','')} | `{row.get('source','')}` |")
    if validation is not None:
        lines += ["", "## Validation", "", "```json", json.dumps(validation, indent=2, sort_keys=True), "```"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")
