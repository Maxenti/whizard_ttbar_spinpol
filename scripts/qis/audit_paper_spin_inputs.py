#!/usr/bin/env python3
"""Audit generator inputs and ntuple kinematics before strict analytic closure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

PATTERNS = {
    "mass_top": re.compile(r"(?i)\b(?:m_top|mass_top|mtop|m\(t\))\b\s*(?:=|:)\s*([0-9.eE+-]+)"),
    "width_top": re.compile(r"(?i)\b(?:w_top|width_top|wtop|w\(t\))\b\s*(?:=|:)\s*([0-9.eE+-]+)"),
    "mass_z": re.compile(r"(?i)\b(?:m_z|mass_z|mz|m\(z\))\b\s*(?:=|:)\s*([0-9.eE+-]+)"),
    "width_z": re.compile(r"(?i)\b(?:w_z|width_z|wz|w\(z\))\b\s*(?:=|:)\s*([0-9.eE+-]+)"),
    "alpha": re.compile(r"(?i)\b(?:alpha_em|alpha_qed|al_em|alpha)\b\s*(?:=|:)\s*([0-9.eE+-]+)"),
    "sin2thetaW": re.compile(r"(?i)\b(?:sin2_theta_w|sin2thetaw|sw2)\b\s*(?:=|:)\s*([0-9.eE+-]+)"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--qualification-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repo = Path(args.repo)
    qualification = Path(args.qualification_root)

    candidates = []
    for path in repo.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".sin", ".f90", ".txt", ".log", ".yaml", ".yml", ".json", ".md"}:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                candidates.append(
                    {
                        "parameter": name,
                        "value_text": match.group(1),
                        "source": str(path),
                        "context": text[max(0, match.start()-80):match.end()+80].replace("\n", " "),
                    }
                )

    ntuple_reports = []
    for parquet in sorted((qualification / "ntuples").glob("*/*.parquet")):
        frame = pd.read_parquet(parquet)
        columns = list(frame.columns)
        interesting = [
            column for column in columns
            if any(token in column.lower() for token in ("mtt", "theta", "costheta", "weight", "event", "beam", "top"))
        ]
        report = {
            "path": str(parquet),
            "rows": len(frame),
            "columns": columns,
            "interesting_columns": interesting,
        }
        for column in interesting:
            if pd.api.types.is_numeric_dtype(frame[column]):
                values = pd.to_numeric(frame[column], errors="coerce")
                report.setdefault("numeric_summary", {})[column] = {
                    "finite": int(values.notna().sum()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "mean": float(values.mean()),
                }
        ntuple_reports.append(report)

    payload = {
        "generator_parameter_candidates": candidates,
        "ntuples": ntuple_reports,
        "manual_review_required": [
            "Confirm the exact WHIZARD electroweak input scheme, not only matching rounded numbers.",
            "Confirm whether the top-angle column uses the incoming positive or negative lepton direction.",
            "Confirm whether mtt is evaluated before or after ISR/recoil at each stage.",
            "Record the reviewed columns and signs in paper_spin_500GeV.yaml.",
            "Set generator_match_reviewed and kinematics_map_reviewed true only after this audit.",
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
