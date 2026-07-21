#!/usr/bin/env python3
"""Create deterministic HTCondor itemdata for joint moment/shape closure."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from qis_ttbar.paper_spin.io import discover_ntuples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualification-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--itemdata", required=True)
    parser.add_argument("--replicas", type=int, default=200)
    parser.add_argument("--replicas-per-job", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260721)
    parser.add_argument("--sample-filter")
    args = parser.parse_args()

    descriptors = discover_ntuples(args.qualification_root)
    if args.sample_filter:
        import re
        pattern = re.compile(args.sample_filter)
        descriptors = [d for d in descriptors if pattern.search(d.sample_id)]

    rows = []
    for descriptor in descriptors:
        for start in range(0, args.replicas, args.replicas_per_job):
            stop = min(args.replicas, start + args.replicas_per_job)
            output = (
                Path(args.output_root)
                / descriptor.dataset
                / descriptor.sample_id
                / f"closure_{start:05d}_{stop:05d}.json"
            )
            rows.append(
                {
                    "input": descriptor.source_path,
                    "config": Path(args.config).resolve(),
                    "replicas": args.replicas,
                    "replica_start": start,
                    "replica_stop": stop,
                    "seed": args.seed,
                    "output": output,
                    "dataset": descriptor.dataset,
                    "sample_id": descriptor.sample_id,
                }
            )

    itemdata = Path(args.itemdata)
    itemdata.parent.mkdir(parents=True, exist_ok=True)
    with itemdata.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {itemdata}: {len(rows)} jobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
