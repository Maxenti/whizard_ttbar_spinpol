#!/usr/bin/env python3
"""Calculate independent gamma/Z tree-level lepton-collider predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from qis_ttbar.paper_spin.analytic_tree import TreeLevelSM, load_sm_parameters
from qis_ttbar.paper_spin.contracts import COEFFICIENT_NAMES
from qis_ttbar.paper_spin.density import all_density_measures


def default_json(value):
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {"real": value.real.tolist(), "imag": value.imag.tolist()}
        return value.tolist()
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    raise TypeError(type(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sm-parameters", required=True)
    parser.add_argument("--sqrt-s", type=float, default=500.0)
    parser.add_argument("--initial-states", nargs="+", default=["ee", "mumu"])
    parser.add_argument("--polarizations", nargs="+", default=["LR100", "RL100"])
    parser.add_argument("--quadrature-points", type=int, default=256)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    model = TreeLevelSM(load_sm_parameters(args.sm_parameters))
    records = []
    for initial_state in args.initial_states:
        for polarization in args.polarizations:
            prediction = model.integrated_density(
                args.sqrt_s,
                initial_state,
                polarization,
                args.quadrature_points,
            )
            records.append(
                {
                    "initial_state": initial_state,
                    "polarization": polarization,
                    "sqrt_s_GeV": args.sqrt_s,
                    "cross_section_fb": prediction["cross_section_fb"],
                    "coefficient_names": COEFFICIENT_NAMES,
                    "coefficient_vector": prediction["coefficient_vector"],
                    "density_measures": all_density_measures(prediction["rho"]),
                    "rho": prediction["rho"],
                    "parameters": prediction["parameters"],
                }
            )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"predictions": records}, indent=2, default=default_json) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
