#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

import pyhepmc


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--lhe",
        required=True,
        type=Path,
    )

    p.add_argument(
        "--hepmc",
        required=True,
        type=Path,
    )

    return p.parse_args()


def iter_lhe_patterns(path: Path):
    inside = False
    header_seen = False
    remaining = 0
    pids = []

    with path.open(errors="replace") as f:
        for line in f:
            s = line.strip()

            if s == "<event>":
                inside = True
                header_seen = False
                pids = []
                continue

            if not inside:
                continue

            if not header_seen:
                if not s or s.startswith("#"):
                    continue

                remaining = int(s.split()[0])
                header_seen = True
                continue

            if remaining:
                if not s or s.startswith("#"):
                    continue

                pids.append(
                    int(s.split()[0])
                )

                remaining -= 1
                continue

            if s == "</event>":
                yield (
                    int(6 in pids),
                    int(-6 in pids),
                    int(24 in pids),
                    int(-24 in pids),
                )

                inside = False


def main():
    args = parse_args()

    lhe_patterns = list(
        iter_lhe_patterns(args.lhe)
    )

    hepmc_events = 0
    mismatch_count = 0
    first_mismatches = []

    with pyhepmc.open(args.hepmc) as stream:
        for index, event in enumerate(stream):
            hepmc_events += 1

            if index >= len(lhe_patterns):
                raise SystemExit(
                    "ERROR: HepMC contains more events than LHE"
                )

            pids = [
                p.pid
                for p in event.particles
            ]

            hepmc_pattern = (
                int(6 in pids),
                int(-6 in pids),
                int(24 in pids),
                int(-24 in pids),
            )

            lhe_pattern = lhe_patterns[index]

            if hepmc_pattern != lhe_pattern:
                mismatch_count += 1

                if len(first_mismatches) < 20:
                    first_mismatches.append(
                        (
                            index,
                            lhe_pattern,
                            hepmc_pattern,
                        )
                    )

    print(f"LHE_EVENTS={len(lhe_patterns)}")
    print(f"HEPMC_EVENTS={hepmc_events}")
    print(
        f"HISTORY_PRESENCE_MISMATCHES="
        f"{mismatch_count}"
    )

    if first_mismatches:
        print()
        print("FIRST_MISMATCHES")

        for item in first_mismatches:
            print(item)

    if (
        len(lhe_patterns) == hepmc_events
        and mismatch_count == 0
    ):
        print()
        print(
            "HISTORY_PRESENCE_DIAGNOSTIC=PASS"
        )
        return

    print()
    print(
        "HISTORY_PRESENCE_DIAGNOSTIC=REVIEW"
    )


if __name__ == "__main__":
    main()
