#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
from pathlib import Path
from typing import Iterator


SHARD_RE = re.compile(r"shard_(?P<index>\d+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit XWGTUP event weights in full-six-fermion "
            "WHIZARD LHE shards."
        )
    )

    parser.add_argument(
        "--lhe-root",
        required=True,
        type=Path,
        help="Root containing sample/subprocess/*.lhe files.",
    )

    parser.add_argument(
        "--output-csv",
        required=True,
        type=Path,
    )

    return parser.parse_args()


def parse_float(token: str) -> float:
    return float(
        token.replace("D", "E").replace("d", "e")
    )


def iter_event_weights(path: Path) -> Iterator[float]:
    waiting_for_header = False

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as handle:
        for raw_line in handle:
            line = raw_line.strip()

            if line.startswith("<event"):
                waiting_for_header = True
                continue

            if not waiting_for_header:
                continue

            if not line or line.startswith("#"):
                continue

            if line.startswith("<"):
                raise RuntimeError(
                    f"Missing event header before XML tag in {path}: "
                    f"{line}"
                )

            fields = line.split()

            if len(fields) < 3:
                raise RuntimeError(
                    f"Malformed LHE event header in {path}: {line}"
                )

            yield parse_float(fields[2])
            waiting_for_header = False


def quantile(
    sorted_values: list[float],
    probability: float,
) -> float:
    if not sorted_values:
        return float("nan")

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return sorted_values[lower]

    fraction = position - lower

    return (
        sorted_values[lower] * (1.0 - fraction)
        + sorted_values[upper] * fraction
    )


def safe_ratio(
    numerator: float,
    denominator: float,
) -> float:
    if denominator == 0:
        return float("inf")

    return numerator / denominator


def shard_index(path: Path) -> int:
    match = SHARD_RE.search(path.name)

    if match is None:
        return -1

    return int(match.group("index"))


def audit_file(path: Path) -> dict[str, object]:
    weights = list(iter_event_weights(path))

    if not weights:
        raise RuntimeError(f"No LHE events found in {path}")

    finite_weights = [
        weight
        for weight in weights
        if math.isfinite(weight)
    ]

    nonfinite_count = len(weights) - len(finite_weights)

    if not finite_weights:
        raise RuntimeError(
            f"No finite event weights found in {path}"
        )

    absolute = sorted(abs(weight) for weight in finite_weights)

    sum_w = math.fsum(finite_weights)
    sum_abs_w = math.fsum(absolute)
    sum_w2 = math.fsum(weight * weight for weight in finite_weights)

    median_abs = statistics.median(absolute)
    p95_abs = quantile(absolute, 0.95)
    p99_abs = quantile(absolute, 0.99)
    max_abs = absolute[-1]

    ess_signed = (
        (sum_w * sum_w) / sum_w2
        if sum_w2 > 0
        else 0.0
    )

    ess_absolute = (
        (sum_abs_w * sum_abs_w) / sum_w2
        if sum_w2 > 0
        else 0.0
    )

    n_events = len(weights)

    return {
        "sample_id": path.parent.parent.name,
        "subprocess_id": path.parent.name,
        "shard_index": shard_index(path),
        "lhe_path": str(path),
        "n_events": n_events,
        "nonfinite_count": nonfinite_count,
        "negative_count": sum(
            weight < 0
            for weight in finite_weights
        ),
        "zero_count": sum(
            weight == 0
            for weight in finite_weights
        ),
        "sum_w": sum_w,
        "sum_abs_w": sum_abs_w,
        "sum_w2": sum_w2,
        "min_w": min(finite_weights),
        "max_w": max(finite_weights),
        "median_abs_w": median_abs,
        "p95_abs_w": p95_abs,
        "p99_abs_w": p99_abs,
        "max_abs_w": max_abs,
        "p99_over_median": safe_ratio(
            p99_abs,
            median_abs,
        ),
        "max_over_median": safe_ratio(
            max_abs,
            median_abs,
        ),
        "ess_signed": ess_signed,
        "ess_absolute": ess_absolute,
        "ess_signed_fraction": ess_signed / n_events,
        "ess_absolute_fraction": ess_absolute / n_events,
        "largest_abs_weight_fraction": safe_ratio(
            max_abs,
            sum_abs_w,
        ),
        "unique_weight_count": len(set(finite_weights)),
    }


def main() -> int:
    args = parse_args()

    paths = sorted(args.lhe_root.rglob("*.lhe"))

    if not paths:
        raise SystemExit(
            f"ERROR: no .lhe files found below {args.lhe_root}"
        )

    rows: list[dict[str, object]] = []

    for index, path in enumerate(paths, start=1):
        print(
            f"[{index:03d}/{len(paths):03d}] {path}",
            flush=True,
        )

        rows.append(audit_file(path))

    rows.sort(
        key=lambda row: (
            str(row["sample_id"]),
            int(row["shard_index"]),
        )
    )

    args.output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = list(rows[0].keys())

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

    print()
    print(f"WROTE={args.output_csv}")
    print(f"LHE_FILES={len(rows)}")
    print(
        f"EVENTS={sum(int(row['n_events']) for row in rows)}"
    )

    print()
    print("=== Worst max/median event-weight ratios ===")

    for row in sorted(
        rows,
        key=lambda item: float(item["max_over_median"]),
        reverse=True,
    )[:20]:
        print(
            f"{row['sample_id']} "
            f"shard_{int(row['shard_index']):04d} "
            f"n={row['n_events']} "
            f"max/median={float(row['max_over_median']):.9g} "
            f"p99/median={float(row['p99_over_median']):.9g} "
            f"ESS/N={float(row['ess_absolute_fraction']):.6g} "
            f"largest_fraction="
            f"{float(row['largest_abs_weight_fraction']):.6g}"
        )

    print()
    print("=== Lowest absolute-weight ESS fractions ===")

    for row in sorted(
        rows,
        key=lambda item: float(
            item["ess_absolute_fraction"]
        ),
    )[:20]:
        print(
            f"{row['sample_id']} "
            f"shard_{int(row['shard_index']):04d} "
            f"n={row['n_events']} "
            f"ESS/N={float(row['ess_absolute_fraction']):.6g} "
            f"max/median={float(row['max_over_median']):.9g} "
            f"largest_fraction="
            f"{float(row['largest_abs_weight_fraction']):.6g} "
            f"negative={row['negative_count']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
