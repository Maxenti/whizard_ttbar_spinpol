#!/usr/bin/env python3
"""Run additive paper-grade spin tomography over a validated qualification tree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qis_ttbar.paper_spin.pipeline import run_pipeline
from qis_ttbar.paper_spin.report import generate_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualification-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--sample-filter")
    parser.add_argument("--skip-report", action="store_true")
    args = parser.parse_args()

    manifest = run_pipeline(
        args.qualification_root,
        args.output_root,
        args.config,
        args.sample_filter,
    )
    report = None
    if not args.skip_report:
        report = generate_report(args.output_root)
    print(json.dumps({"manifest": manifest, "report": report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
