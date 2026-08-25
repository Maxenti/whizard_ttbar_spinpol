#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


FINAL_INTEGRATION_RE = re.compile(
    r"""
    ^\s*
    (?P<iteration>\d+)
    \s+
    (?P<calls>\d+)
    \s+
    (?P<integral>[+-]?\d+\.\d+E[+-]\d+)
    \s+
    (?P<error>[+-]?\d+\.\d+E[+-]\d+)
    \s+
    (?P<error_percent>[+-]?\d+\.\d+)
    \s+
    (?P<accuracy>[+-]?\d+\.\d+)
    \s+
    (?P<efficiency>[+-]?\d+\.\d+)
    \s+
    (?P<chi2>[+-]?\d+\.\d+)
    \s+
    (?P<n_iterations>\d+)
    \s*$
    """,
    re.VERBOSE,
)

UNWEIGHTING_RE = re.compile(
    r"actual unweighting efficiency\s*=\s*"
    r"(?P<value>[+-]?\d+(?:\.\d+)?)\s*%"
)

EXCESS_RE = re.compile(
    r"Encountered events with excess weight:\s*"
    r"(?P<count>\d+)\s+events\s+"
    r"\(\s*(?P<percent>[+-]?\d+(?:\.\d+)?)\s*%\)"
)

MAX_EXCESS_RE = re.compile(
    r"Maximum excess weight\s*=\s*"
    r"(?P<value>[+-]?\d+(?:\.\d+)?E[+-]\d+)"
)

AVG_EXCESS_RE = re.compile(
    r"Average excess weight\s*=\s*"
    r"(?P<value>[+-]?\d+(?:\.\d+)?E[+-]\d+)"
)

SEED_RE = re.compile(
    r"^whizard_seed=(?P<seed>\d+)\s*$",
    re.MULTILINE,
)

EVENTS_RE = re.compile(
    r"^events=(?P<events>\d+)\s*$",
    re.MULTILINE,
)

COMPLETION_RE = re.compile(
    r"^Completed\s+"
    r"(?P<sample>[^/]+)/"
    r"(?P<subprocess>[^/]+)/"
    r"shard_(?P<shard>\d+)\s*$",
    re.MULTILINE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract WHIZARD integration and event-generation quality "
            "metrics from full6f Condor stdout logs."
        )
    )

    parser.add_argument(
        "--logs",
        type=Path,
        nargs="+",
        required=True,
        help="One or more directories containing Condor stdout files.",
    )

    parser.add_argument(
        "--output-csv",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-json",
        type=Path,
        required=True,
    )

    return parser.parse_args()


def parse_log(path: Path) -> dict[str, Any]:
    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    row: dict[str, Any] = {
        "log_path": str(path),
        "log_name": path.name,
        "complete": False,
        "sample_id": None,
        "subprocess_id": None,
        "shard_index": None,
        "whizard_seed": None,
        "events": None,
        "integral_fb": None,
        "integration_error_fb": None,
        "integration_error_percent": None,
        "integration_accuracy": None,
        "integration_efficiency_percent": None,
        "integration_chi2": None,
        "integration_calls": None,
        "unweighting_efficiency_percent": None,
        "excess_weight_events": None,
        "excess_weight_percent": None,
        "maximum_excess_weight": None,
        "average_excess_weight": None,
        "whizard_finished": (
            "WHIZARD run finished." in text
        ),
    }

    completion = COMPLETION_RE.search(text)

    if completion:
        row["complete"] = True
        row["sample_id"] = completion.group("sample")
        row["subprocess_id"] = completion.group("subprocess")
        row["shard_index"] = int(completion.group("shard"))

    seed = SEED_RE.search(text)

    if seed:
        row["whizard_seed"] = int(seed.group("seed"))

    events = EVENTS_RE.search(text)

    if events:
        row["events"] = int(events.group("events"))

    integration_matches = [
        match
        for line in text.splitlines()
        if (match := FINAL_INTEGRATION_RE.match(line))
    ]

    if integration_matches:
        match = integration_matches[-1]

        row["integral_fb"] = float(match.group("integral"))
        row["integration_error_fb"] = float(
            match.group("error")
        )
        row["integration_error_percent"] = float(
            match.group("error_percent")
        )
        row["integration_accuracy"] = float(
            match.group("accuracy")
        )
        row["integration_efficiency_percent"] = float(
            match.group("efficiency")
        )
        row["integration_chi2"] = float(
            match.group("chi2")
        )
        row["integration_calls"] = int(
            match.group("calls")
        )

    match = UNWEIGHTING_RE.search(text)

    if match:
        row["unweighting_efficiency_percent"] = float(
            match.group("value")
        )

    match = EXCESS_RE.search(text)

    if match:
        row["excess_weight_events"] = int(
            match.group("count")
        )
        row["excess_weight_percent"] = float(
            match.group("percent")
        )

    match = MAX_EXCESS_RE.search(text)

    if match:
        row["maximum_excess_weight"] = float(
            match.group("value")
        )

    match = AVG_EXCESS_RE.search(text)

    if match:
        row["average_excess_weight"] = float(
            match.group("value")
        )

    return row


def main() -> int:
    args = parse_args()

    files: list[Path] = []

    for directory in args.logs:
        if directory.is_dir():
            files.extend(sorted(directory.glob("*.out")))

    files = sorted(set(files))

    rows = [parse_log(path) for path in files]

    fieldnames = list(rows[0]) if rows else []

    args.output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.output_csv.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)

    summary: dict[str, Any] = {
        "log_files": len(rows),
        "complete_logs": sum(
            bool(row["complete"])
            for row in rows
        ),
        "incomplete_logs": sum(
            not bool(row["complete"])
            for row in rows
        ),
        "samples": {},
    }

    samples = sorted(
        {
            row["sample_id"]
            for row in rows
            if row["sample_id"] is not None
        }
    )

    for sample in samples:
        sample_rows = [
            row
            for row in rows
            if row["sample_id"] == sample
        ]

        complete_rows = [
            row
            for row in sample_rows
            if row["complete"]
        ]

        summary["samples"][sample] = {
            "logs": len(sample_rows),
            "complete": len(complete_rows),
            "events": sum(
                int(row["events"] or 0)
                for row in complete_rows
            ),
            "mean_integral_fb": (
                sum(
                    float(row["integral_fb"])
                    for row in complete_rows
                    if row["integral_fb"] is not None
                )
                /
                sum(
                    row["integral_fb"] is not None
                    for row in complete_rows
                )
                if any(
                    row["integral_fb"] is not None
                    for row in complete_rows
                )
                else None
            ),
            "maximum_integration_error_percent": max(
                (
                    float(
                        row["integration_error_percent"]
                    )
                    for row in complete_rows
                    if row[
                        "integration_error_percent"
                    ] is not None
                ),
                default=None,
            ),
            "minimum_unweighting_efficiency_percent": min(
                (
                    float(
                        row[
                            "unweighting_efficiency_percent"
                        ]
                    )
                    for row in complete_rows
                    if row[
                        "unweighting_efficiency_percent"
                    ] is not None
                ),
                default=None,
            ),
            "maximum_excess_weight": max(
                (
                    float(
                        row["maximum_excess_weight"]
                    )
                    for row in complete_rows
                    if row[
                        "maximum_excess_weight"
                    ] is not None
                ),
                default=None,
            ),
            "maximum_excess_weight_percent": max(
                (
                    float(
                        row["excess_weight_percent"]
                    )
                    for row in complete_rows
                    if row[
                        "excess_weight_percent"
                    ] is not None
                ),
                default=None,
            ),
        }

    args.output_json.write_text(
        json.dumps(
            {
                "summary": summary,
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"LOG_FILES={summary['log_files']}")
    print(f"COMPLETE_LOGS={summary['complete_logs']}")
    print(f"INCOMPLETE_LOGS={summary['incomplete_logs']}")

    for sample, payload in summary["samples"].items():
        print(
            f"{sample}: "
            f"complete={payload['complete']} "
            f"events={payload['events']} "
            f"mean_xsec_fb={payload['mean_integral_fb']} "
            f"max_int_err_pct="
            f"{payload['maximum_integration_error_percent']} "
            f"min_unweight_eff_pct="
            f"{payload['minimum_unweighting_efficiency_percent']} "
            f"max_excess_weight="
            f"{payload['maximum_excess_weight']}"
        )

    print(f"WROTE_CSV={args.output_csv}")
    print(f"WROTE_JSON={args.output_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
