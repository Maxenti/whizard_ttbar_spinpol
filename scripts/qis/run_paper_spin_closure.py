#!/usr/bin/env python3
"""Run synthetic injection or same-sample moment-vs-shape closure."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.closure import joint_bootstrap_moment_shape_closure, synthetic_moment_shape_closure
from qis_ttbar.paper_spin.contracts import COEFFICIENT_NAMES
from qis_ttbar.paper_spin.io import load_analyzer_sample, load_config
from qis_ttbar.paper_spin.synthetic import run_default_closure_suite, synthetic_states


def default_json(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    raise TypeError(type(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    synthetic = sub.add_parser("synthetic")
    synthetic.add_argument("--events", type=int, default=200000)
    synthetic.add_argument("--seed", type=int, default=20260721)
    synthetic.add_argument("--shape-events", type=int, default=50000)
    synthetic.add_argument("--output", required=True)

    data = sub.add_parser("data")
    data.add_argument("--input", required=True)
    data.add_argument("--config", required=True)
    data.add_argument("--replicas", type=int, default=200)
    data.add_argument("--replica-start", type=int, default=0)
    data.add_argument("--replica-stop", type=int)
    data.add_argument("--seed", type=int, default=20260721)
    data.add_argument("--output", required=True)
    data.add_argument("--max-iterations", type=int, default=1200)

    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.mode == "synthetic":
        closures = run_default_closure_suite(args.events, args.seed)
        definitions = synthetic_states()
        shape_closures = [
            {
                "name": name,
                **asdict(
                    synthetic_moment_shape_closure(
                        coefficients,
                        events=args.shape_events,
                        seed=args.seed + 50021 * index,
                    )
                ),
            }
            for index, (name, coefficients) in enumerate(definitions.items())
        ]
        payload = {
            "coefficient_names": COEFFICIENT_NAMES,
            "moment_injection_closure": [asdict(result) for result in closures],
            "moment_shape_closure": shape_closures,
            "definitions": definitions,
        }
    else:
        config = load_config(args.config)
        sample = load_analyzer_sample(args.input, config)
        result = joint_bootstrap_moment_shape_closure(
            sample,
            replicas=args.replicas,
            seed=args.seed,
            replica_start=args.replica_start,
            replica_stop=args.replica_stop,
            shape_max_iterations=args.max_iterations,
        )
        payload = {
            "coefficient_names": COEFFICIENT_NAMES,
            "result": asdict(result),
        }
    output.write_text(json.dumps(payload, indent=2, default=default_json) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
