#!/usr/bin/env python3
"""Validate one generated 365 GeV ISR LHE sample from the 16-sample matrix."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def load_row(table: Path, sample_id: str) -> dict[str, str]:
    delimiter = "\t" if table.suffix.lower() == ".tsv" else ","
    with table.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter=delimiter))
    matches = [row for row in rows if row.get("sample_id") == sample_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {sample_id}; found {len(matches)}")
    return matches[0]


def _component(vector: Any, *names: str) -> float:
    for name in names:
        if hasattr(vector, name):
            value = getattr(vector, name)
            if callable(value):
                value = value()
            return float(value)
    raise AttributeError(
        f"{type(vector).__module__}.{type(vector).__name__} lacks components {names}"
    )


def p4(vector: Any) -> tuple[float, float, float, float]:
    return (
        _component(vector, "energy", "e"),
        _component(vector, "px"),
        _component(vector, "py"),
        _component(vector, "pz"),
    )


def add(*vectors: Any) -> tuple[float, float, float, float]:
    values = [p4(vector) for vector in vectors]
    return tuple(sum(value[index] for value in values) for index in range(4))  # type: ignore[return-value]


def subtract(first: Any, *others: Any) -> tuple[float, float, float, float]:
    result = list(p4(first))
    for other in others:
        values = p4(other)
        for index in range(4):
            result[index] -= values[index]
    return tuple(result)  # type: ignore[return-value]


def invariant_mass(values: tuple[float, float, float, float]) -> float:
    e, px, py, pz = values
    mass2 = e * e - px * px - py * py - pz * pz
    return math.sqrt(max(0.0, mass2))


def norm4(values: tuple[float, float, float, float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def quantile(sorted_values: list[float], probability: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return sorted_values[low]
    fraction = position - low
    return sorted_values[low] * (1.0 - fraction) + sorted_values[high] * fraction


def record(checks: list[dict[str, Any]], name: str, passed: bool, message: str) -> None:
    checks.append(
        {
            "check": name,
            "status": "pass" if passed else "fail",
            "message": message,
        }
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    result.add_argument("--campaign-root", type=Path, required=True)
    result.add_argument("--sample-id", required=True)
    result.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_lhe_matrix.yaml"),
    )
    result.add_argument("--lhe", type=Path)
    result.add_argument("--output", type=Path)
    result.add_argument("--strict", action="store_true")
    return result


def resolve(repo: Path, path: Path) -> Path:
    return path.expanduser().resolve() if path.is_absolute() else (repo / path).resolve()


def main() -> int:
    args = parser().parse_args()
    repo = args.repo_root.expanduser().resolve()
    campaign_root = resolve(repo, args.campaign_root)
    config_path = resolve(repo, args.config)
    config = load_yaml(config_path)
    validation = config["validation"]

    row = load_row(campaign_root / "campaign_samples.tsv", args.sample_id)
    run_dir = Path(row["run_dir"])
    lhe_path = args.lhe.expanduser().resolve() if args.lhe else Path(row["expected_lhe_path"])
    output_path = args.output.expanduser().resolve() if args.output else run_dir / "sample_validation.json"

    if not lhe_path.is_file() or lhe_path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty LHE: {lhe_path}")

    sys.path.insert(0, str(repo))
    from qis_ttbar.io.lhe import extract_ttbar_truth, iter_lhe_events, parse_lhe_header

    initial_state = row["initial_state"]
    decay_channel = row["decay_channel"]
    expected_events = int(row["events"])
    nominal_energy = float(config["nominal_sqrt_s_GeV"])
    nominal_top_mass = float(validation["nominal_top_mass_GeV"])
    threshold = 2.0 * nominal_top_mass

    header = parse_lhe_header(lhe_path)
    mtt_values: list[float] = []
    beta_values: list[float] = []
    top_masses: list[float] = []
    antitop_masses: list[float] = []
    weights: list[float] = []
    closure_values: list[float] = []
    decay_mismatches = 0
    truth_failures = 0

    for event in iter_lhe_events(lhe_path):
        try:
            truth = extract_ttbar_truth(event, initial_state)
        except Exception:
            truth_failures += 1
            continue

        if truth.decay_channel != decay_channel:
            decay_mismatches += 1

        pair = add(truth.top, truth.antitop)
        current_mtt = invariant_mass(pair)
        beta2 = 1.0 - (threshold * threshold) / (current_mtt * current_mtt)
        beta = math.sqrt(max(0.0, beta2))

        mtt_values.append(current_mtt)
        beta_values.append(beta)
        top_masses.append(invariant_mass(p4(truth.top)))
        antitop_masses.append(invariant_mass(p4(truth.antitop)))
        closure_values.extend(
            [
                norm4(subtract(truth.top, truth.b, truth.lepton_plus, truth.neutrino)),
                norm4(
                    subtract(
                        truth.antitop,
                        truth.bbar,
                        truth.lepton_minus,
                        truth.antineutrino,
                    )
                ),
            ]
        )
        weights.append(float(event.weight))

    if not mtt_values:
        raise ValueError(f"No valid ttbar truth events found in {lhe_path}")

    finite_weights = [weight for weight in weights if math.isfinite(weight)]
    nonfinite_weights = len(weights) - len(finite_weights)
    negative_weights = sum(weight < 0.0 for weight in finite_weights)
    sorted_mtt = sorted(mtt_values)
    sorted_beta = sorted(beta_values)
    probabilities = [float(value) for value in validation["record_quantiles"]]

    cross_section = float(header.cross_section_pb)
    cross_section_error = float(header.cross_section_error_pb)
    relative_cross_section_error = (
        abs(cross_section_error / cross_section) if cross_section != 0.0 else math.inf
    )

    expected_beams = (11, -11) if initial_state == "ee" else (13, -13)
    header_energy = float(header.beam1_energy_GeV + header.beam2_energy_GeV)
    maximum_closure = max(closure_values)
    maximum_top_mass_deviation = max(
        max(abs(value - nominal_top_mass) for value in top_masses),
        max(abs(value - nominal_top_mass) for value in antitop_masses),
    )

    checks: list[dict[str, Any]] = []
    record(
        checks,
        "beam_particles",
        (int(header.beam1_pdg), int(header.beam2_pdg)) == expected_beams,
        f"beam PDGs={(header.beam1_pdg, header.beam2_pdg)}, expected={expected_beams}",
    )
    record(
        checks,
        "nominal_energy",
        math.isclose(
            header_energy,
            nominal_energy,
            rel_tol=0.0,
            abs_tol=float(validation["nominal_energy_tolerance_GeV"]),
        ),
        f"LHE beam-energy sum={header_energy:.12g} GeV",
    )
    record(
        checks,
        "exact_event_count",
        len(mtt_values) == expected_events and int(header.declared_events) == expected_events,
        f"parsed={len(mtt_values)}, declared={header.declared_events}, expected={expected_events}",
    )
    record(checks, "truth_extraction", truth_failures == 0, f"truth failures={truth_failures}")
    record(checks, "decay_channel", decay_mismatches == 0, f"decay mismatches={decay_mismatches}")
    record(
        checks,
        "finite_weights",
        nonfinite_weights <= int(validation["maximum_nonfinite_weights"]),
        f"nonfinite weights={nonfinite_weights}",
    )
    record(
        checks,
        "nonnegative_weights",
        negative_weights <= int(validation["maximum_negative_weights"]),
        f"negative weights={negative_weights}",
    )
    record(
        checks,
        "positive_cross_section",
        math.isfinite(cross_section) and cross_section > 0.0,
        f"cross section={cross_section:.12g} pb",
    )
    record(
        checks,
        "cross_section_precision",
        math.isfinite(relative_cross_section_error)
        and relative_cross_section_error
        <= float(validation["maximum_relative_cross_section_error"]),
        f"relative integration error={relative_cross_section_error:.6g}",
    )
    record(
        checks,
        "top_decay_closure",
        maximum_closure
        <= float(validation["maximum_top_decay_closure_residual_GeV"]),
        f"maximum closure residual={maximum_closure:.6g} GeV",
    )
    record(
        checks,
        "on_shell_top_mass",
        maximum_top_mass_deviation <= 1.0e-5,
        f"maximum |m-173.1|={maximum_top_mass_deviation:.6g} GeV",
    )
    record(
        checks,
        "mtt_above_threshold",
        min(mtt_values)
        >= threshold - float(validation["threshold_tolerance_GeV"]),
        f"minimum mtt={min(mtt_values):.6f} GeV; threshold={threshold:.6f} GeV",
    )
    record(
        checks,
        "mtt_not_above_nominal",
        max(mtt_values)
        <= nominal_energy + float(validation["maximum_mtt_above_nominal_GeV"]),
        f"maximum mtt={max(mtt_values):.6f} GeV; nominal={nominal_energy:.6f} GeV",
    )
    if bool(validation.get("require_isr_energy_spread", True)):
        record(
            checks,
            "isr_energy_spread",
            min(mtt_values)
            < nominal_energy - float(validation["minimum_isr_energy_loss_GeV"]),
            f"minimum mtt={min(mtt_values):.6f} GeV",
        )

    payload = {
        "schema_version": 1,
        "campaign_id": json.loads((campaign_root / "campaign_manifest.json").read_text())[
            "campaign_id"
        ],
        "sample_id": args.sample_id,
        "sample": row,
        "lhe_path": str(lhe_path),
        "lhe_size_bytes": lhe_path.stat().st_size,
        "header": {
            "beam1_pdg": int(header.beam1_pdg),
            "beam2_pdg": int(header.beam2_pdg),
            "beam1_energy_GeV": float(header.beam1_energy_GeV),
            "beam2_energy_GeV": float(header.beam2_energy_GeV),
            "nominal_energy_GeV": header_energy,
            "cross_section_pb": cross_section,
            "cross_section_error_pb": cross_section_error,
            "relative_cross_section_error": relative_cross_section_error,
            "declared_events": int(header.declared_events),
        },
        "events_audited": len(mtt_values),
        "mtt_GeV": {
            "minimum": min(mtt_values),
            "maximum": max(mtt_values),
            "mean": statistics.fmean(mtt_values),
            "quantiles": {
                f"q{probability:g}": quantile(sorted_mtt, probability)
                for probability in probabilities
            },
        },
        "beta_t_nominal_mass": {
            "minimum": min(beta_values),
            "maximum": max(beta_values),
            "mean": statistics.fmean(beta_values),
            "quantiles": {
                f"q{probability:g}": quantile(sorted_beta, probability)
                for probability in probabilities
            },
        },
        "top_mass_GeV": {
            "minimum": min(top_masses),
            "maximum": max(top_masses),
            "mean": statistics.fmean(top_masses),
        },
        "antitop_mass_GeV": {
            "minimum": min(antitop_masses),
            "maximum": max(antitop_masses),
            "mean": statistics.fmean(antitop_masses),
        },
        "maximum_top_decay_closure_residual_GeV": maximum_closure,
        "truth_extraction_failures": truth_failures,
        "decay_channel_mismatches": decay_mismatches,
        "nonfinite_weights": nonfinite_weights,
        "negative_weights": negative_weights,
        "nominal_threshold_GeV": threshold,
        "fraction_below_350_GeV": sum(value < 350.0 for value in mtt_values)
        / len(mtt_values),
        "checks": checks,
    }
    payload["status"] = (
        "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    )

    output_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    return 1 if args.strict and payload["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
