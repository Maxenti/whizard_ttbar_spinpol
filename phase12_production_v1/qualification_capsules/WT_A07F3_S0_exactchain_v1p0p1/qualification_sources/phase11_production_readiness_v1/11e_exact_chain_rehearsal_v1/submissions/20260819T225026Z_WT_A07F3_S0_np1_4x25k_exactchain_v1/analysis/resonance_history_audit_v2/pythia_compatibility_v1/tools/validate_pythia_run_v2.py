#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

import pyhepmc


KNOWN_RECOVERABLE_ERRORS = {
    (
        "Error in MiniStringFragmentation::fragment: "
        "no 1- or 2-body state found above mass threshold"
    ),
    (
        "Error in LundFragmentation::fragment: "
        "ministring fragmentation failed"
    ),
    (
        "Error in Pythia::next: "
        "hadronLevel failed; try again"
    ),
}


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--metadata",
        required=True,
        type=Path,
    )

    p.add_argument(
        "--hepmc",
        required=True,
        type=Path,
    )

    p.add_argument(
        "--log",
        required=True,
        type=Path,
    )

    p.add_argument(
        "--events",
        required=True,
        type=int,
    )

    return p.parse_args()


def parse_summary(text: str):
    row_re = re.compile(
        r"(?m)^\s*\|\s*"
        r"(\d+)\s+"
        r"((?:Warning|Error) in .+?)"
        r"\s+\|\s*$"
    )

    result = collections.Counter()

    for count, message in row_re.findall(text):
        result[message.strip()] += int(count)

    return result


def main():
    args = parse_args()

    metadata = json.loads(
        args.metadata.read_text()
    )

    log = args.log.read_text(
        errors="replace"
    )

    summary = parse_summary(log)

    hepmc_events = 0
    bad_weight_events = 0

    with pyhepmc.open(args.hepmc) as stream:
        for event in stream:
            hepmc_events += 1

            if len(event.weights) != 1:
                bad_weight_events += 1

    error_summary = {
        message: count
        for message, count in summary.items()
        if message.startswith("Error in ")
    }

    warning_summary = {
        message: count
        for message, count in summary.items()
        if message.startswith("Warning in ")
    }

    unknown_errors = {
        message: count
        for message, count in error_summary.items()
        if message not in KNOWN_RECOVERABLE_ERRORS
    }

    recoverable_errors = {
        message: count
        for message, count in error_summary.items()
        if message in KNOWN_RECOVERABLE_ERRORS
    }

    abort_lines = re.findall(
        r"(?mi)^\s*PYTHIA Abort in .+$",
        log,
    )

    hadron_retry_message = (
        "Error in Pythia::next: "
        "hadronLevel failed; try again"
    )

    hadron_retries = error_summary.get(
        hadron_retry_message,
        0,
    )

    mec_message = (
        "Warning in SimpleTimeShower::findMEcorr: "
        "ME weight above PS one"
    )

    mec_count = warning_summary.get(
        mec_message,
        0,
    )

    N = args.events

    print(f"EXPECTED_EVENTS={N}")
    print(f"STATUS={metadata.get('status')}")
    print(f"RETURN_CODE={metadata.get('return_code')}")
    print(f"REQUESTED={metadata.get('requested_events')}")
    print(f"ATTEMPTED={metadata.get('attempted_events')}")
    print(f"ACCEPTED={metadata.get('accepted_events')}")
    print(f"FAILED_EVENTS={metadata.get('failed_events')}")
    print(f"HEPMC_EVENTS={hepmc_events}")
    print(f"BAD_WEIGHT_EVENTS={bad_weight_events}")

    print()
    print(
        f"RECOVERABLE_ERROR_MESSAGES="
        f"{len(recoverable_errors)}"
    )

    print(
        f"RECOVERABLE_ERROR_OCCURRENCES="
        f"{sum(recoverable_errors.values())}"
    )

    print(
        f"RECOVERED_HADRON_RETRIES="
        f"{hadron_retries}"
    )

    print(
        f"RECOVERED_HADRON_RETRY_RATE="
        f"{hadron_retries / N:.8e}"
    )

    print(
        f"UNKNOWN_ERROR_MESSAGES="
        f"{len(unknown_errors)}"
    )

    print(
        f"UNKNOWN_ERROR_OCCURRENCES="
        f"{sum(unknown_errors.values())}"
    )

    print(
        f"PYTHIA_ABORT_LINES="
        f"{len(abort_lines)}"
    )

    print()
    print(
        f"MEC_ABOVE_PS_OCCURRENCES="
        f"{mec_count}"
    )

    print(
        f"MEC_ABOVE_PS_RATE="
        f"{mec_count / N:.8f}"
    )

    print()
    print("ERROR_SUMMARY")

    if not error_summary:
        print("none")
    else:
        for message, count in sorted(
            error_summary.items(),
            key=lambda x: (-x[1], x[0]),
        ):
            classification = (
                "RECOVERABLE"
                if message in KNOWN_RECOVERABLE_ERRORS
                else "UNKNOWN"
            )

            print(
                f"{count:8d} "
                f"{classification:12s} "
                f"{message}"
            )

    structural_ok = (
        metadata.get("status") == "success"
        and int(metadata.get("return_code", -1)) == 0
        and int(metadata.get("requested_events", -1)) == N
        and int(metadata.get("attempted_events", -1)) == N
        and int(metadata.get("accepted_events", -1)) == N
        and int(metadata.get("failed_events", -1)) == 0
        and hepmc_events == N
        and bad_weight_events == 0
        and not unknown_errors
        and not abort_lines
    )

    print()

    if not structural_ok:
        print(
            "PYTHIA_PRODUCTION_COMPAT_GATE=FAIL"
        )
        raise SystemExit(1)

    if hadron_retries:
        print(
            "PYTHIA_PRODUCTION_COMPAT_GATE="
            "PASS_WITH_RECOVERABLE_ERRORS"
        )
    else:
        print(
            "PYTHIA_PRODUCTION_COMPAT_GATE=PASS"
        )


if __name__ == "__main__":
    main()
