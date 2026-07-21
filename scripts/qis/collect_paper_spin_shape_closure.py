#!/usr/bin/env python3
"""Merge disjoint joint-bootstrap closure slices exactly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.contracts import COEFFICIENT_NAMES


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sources = sorted(Path(args.input_dir).rglob("closure_*.json"))
    if not sources:
        raise SystemExit("No closure JSON files found")

    groups: dict[tuple[str, str], list[dict]] = {}
    for source in sources:
        payload = json.loads(source.read_text())
        result = payload["result"]
        key = (source.parent.parent.name, source.parent.name)
        groups.setdefault(key, []).append(result)

    output_records = []
    for (dataset, sample_id), slices in sorted(groups.items()):
        slices.sort(key=lambda item: item["metadata"]["replica_start"])
        deltas = np.concatenate(
            [np.asarray(item["delta_replicas"], dtype=float) for item in slices],
            axis=0,
        )
        starts = [int(item["metadata"]["replica_start"]) for item in slices]
        stops = [int(item["metadata"]["replica_stop"]) for item in slices]
        for previous, current in zip(stops[:-1], starts[1:], strict=True):
            if previous != current:
                raise RuntimeError(
                    f"Replica gap/overlap for {dataset}/{sample_id}: {previous} -> {current}"
                )
        central = slices[0]
        central_delta = np.asarray(central["delta_shape_minus_moment"], dtype=float)
        covariance = np.cov(deltas, rowvar=False, ddof=1)
        errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
        pulls = np.divide(
            central_delta,
            errors,
            out=np.full_like(central_delta, np.nan),
            where=errors > 0.0,
        )
        output_records.append(
            {
                "dataset": dataset,
                "sample_id": sample_id,
                "coefficient_names": COEFFICIENT_NAMES,
                "moment_coefficients": central["moment_coefficients"],
                "shape_coefficients": central["shape_coefficients"],
                "delta_shape_minus_moment": central_delta.tolist(),
                "delta_covariance": covariance.tolist(),
                "delta_standard_errors": errors.tolist(),
                "pulls": pulls.tolist(),
                "max_abs_pull": float(np.nanmax(np.abs(pulls))),
                "replicas": int(len(deltas)),
                "replica_start": min(starts),
                "replica_stop": max(stops),
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"samples": output_records}, indent=2) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
