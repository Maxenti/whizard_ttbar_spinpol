#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "log",
        type=Path,
    )

    p.add_argument(
        "--events",
        type=int,
        default=None,
    )

    return p.parse_args()


def main():
    args = parse_args()

    text = args.log.read_text(
        errors="replace"
    )

    live_warnings = re.findall(
        r"(?m)^\s*PYTHIA Warning in (.+)$",
        text,
    )

    live_errors = re.findall(
        r"(?m)^\s*PYTHIA Error in (.+)$",
        text,
    )

    # PYTHIA's final warning/error statistics table contains the
    # authoritative multiplicity. The live log may print a message
    # only once even when it occurred many times.
    summary_re = re.compile(
        r"(?m)^\s*\|\s*"
        r"(\d+)\s+"
        r"((?:Warning|Error) in .+?)"
        r"\s+\|\s*$"
    )

    summary = collections.Counter()

    for count, message in summary_re.findall(text):
        summary[message.strip()] += int(count)

    warning_total = sum(
        count
        for message, count in summary.items()
        if message.startswith("Warning in ")
    )

    error_total = sum(
        count
        for message, count in summary.items()
        if message.startswith("Error in ")
    )

    mec_message = (
        "Warning in SimpleTimeShower::findMEcorr: "
        "ME weight above PS one"
    )

    mec_count = summary.get(
        mec_message,
        0,
    )

    print(f"LOG={args.log}")
    print(f"LIVE_WARNING_LINES={len(live_warnings)}")
    print(f"LIVE_ERROR_LINES={len(live_errors)}")
    print(f"SUMMARY_WARNING_OCCURRENCES={warning_total}")
    print(f"SUMMARY_ERROR_OCCURRENCES={error_total}")
    print(f"MEC_ABOVE_PS_OCCURRENCES={mec_count}")

    if args.events is not None:
        print(f"EVENTS={args.events}")

        if args.events > 0:
            print(
                "MEC_ABOVE_PS_PER_EVENT="
                f"{mec_count/args.events:.8f}"
            )

    print()
    print("SUMMARY_MESSAGES")

    if not summary:
        print("none")
    else:
        for message, count in sorted(
            summary.items(),
            key=lambda x: (-x[1], x[0]),
        ):
            print(f"{count:8d}  {message}")


if __name__ == "__main__":
    main()
