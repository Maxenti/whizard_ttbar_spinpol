#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def digest(path: Path) -> str:

    h = hashlib.sha256()

    with path.open("rb") as stream:

        while True:

            block = stream.read(
         * 1024
            )

            if not block:
                break

            h.update(block)

    return h.hexdigest()


def verify_tsv(path: Path) -> int:

    with path.open() as stream:

        rows = list(
            csv.DictReader(
                stream,
                delimiter="\t",
            )
        )

    failures = 0

    for row in rows:

        source = Path(
            row["path"]
        )

        expected = (
            row["sha256"]
        )

        if not source.is_file():

            print(
                f"MISSING {source}"
            )

            failures += 1
            continue

        actual = digest(
            source
        )

        if actual != expected:

            print(
                f"FAIL {source}"
            )

            print(
                f"  expected={expected}"
            )

            print(
                f"  actual  ={actual}"
            )

            failures += 1

        else:

            print(
                f"PASS {source}"
            )

    return failures


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "closeout_dir",
        type=Path,
    )

    args = parser.parse_args()

    root = (
        args.closeout_dir.resolve()
    )

    failures = 0

    for name in [
        "HARD_LHE_SHARDS_SHA256.tsv",
        "FINAL_HEPMC_SHARDS_SHA256.tsv",
    ]:

        path = (
            root
            / "manifests"
            / name
        )

        if not path.is_file():
            raise SystemExit(
                f"missing manifest: {path}"
            )

        failures += verify_tsv(
            path
        )

    parent_summary = (
        root
        / "manifests"
        / "PARENT_LHE_SUMMARY.txt"
    )

    values = {}

    for line in parent_summary.read_text().splitlines():

        if "=" not in line:
            continue

        key, value = (
            line.split(
                "=",
                1,
            )
        )

        values[key] = value

    parent = Path(
        values["path"]
    )

    expected = (
        values["sha256"]
    )

    actual = digest(
        parent
    )

    if actual != expected:

        print(
            f"FAIL {parent}"
        )

        failures += 1

    else:

        print(
            f"PASS {parent}"
        )

    if failures:

        raise SystemExit(
            f"FROZEN_DATA_VERIFY=FAIL failures={failures}"
        )

    print(
        "FROZEN_DATA_VERIFY=PASS"
    )


if __name__ == "__main__":
    main()
