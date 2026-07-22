#!/usr/bin/env python3
"""Validate 365 GeV campaign configs and an optional WHIZARD LHE smoke sample."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

import yaml


EXPECTED_TRANSFORMS = {
    "plus_component_transform": [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, -1.0],
    ],
    "minus_component_transform": [
        [-1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, 0.0, -1.0],
    ],
}


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def finite(value: float) -> bool:
    return math.isfinite(float(value))


def _p4_component(vector: Any, *names: str) -> float:
    """Read one four-vector component across repository vector conventions.

    The canonical ``qis_ttbar.models.FourVector`` uses ``e`` for energy, while
    some analysis-local vector classes use ``energy``.  Keep the threshold
    validator compatible with both without changing the frozen event model.
    """

    for name in names:
        if not hasattr(vector, name):
            continue
        value = getattr(vector, name)
        if callable(value):
            value = value()
        return float(value)

    available = sorted(
        name for name in dir(vector)
        if not name.startswith("_")
    )
    raise AttributeError(
        f"{type(vector).__module__}.{type(vector).__name__} does not provide "
        f"any of the required components {names}; available public "
        f"attributes={available}"
    )


def p4_values(vector: Any) -> tuple[float, float, float, float]:
    return (
        _p4_component(vector, "energy", "e"),
        _p4_component(vector, "px"),
        _p4_component(vector, "py"),
        _p4_component(vector, "pz"),
    )


def add_p4(*vectors: Any) -> tuple[float, float, float, float]:
    values = [p4_values(vector) for vector in vectors]
    return tuple(sum(item[index] for item in values) for index in range(4))  # type: ignore[return-value]


def subtract_p4(first: Any, *others: Any) -> tuple[float, float, float, float]:
    result = list(p4_values(first))
    for other in others:
        values = p4_values(other)
        for index in range(4):
            result[index] -= values[index]
    return tuple(result)  # type: ignore[return-value]


def mass(values: tuple[float, float, float, float]) -> float:
    energy, px, py, pz = values
    mass2 = energy * energy - px * px - py * py - pz * pz
    return math.sqrt(max(0.0, mass2))


def euclidean4(values: tuple[float, float, float, float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return sorted_values[low]
    fraction = position - low
    return sorted_values[low] * (1.0 - fraction) + sorted_values[high] * fraction


def config_checks(
    paper: dict[str, Any], pilot: dict[str, Any], sm: dict[str, Any]
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, message: str, **details: Any) -> None:
        checks.append(
            {
                "check": name,
                "status": "pass" if passed else "fail",
                "message": message,
                **details,
            }
        )

    energy = float(pilot.get("nominal_sqrt_s_GeV", float("nan")))
    record(
        "pilot_nominal_energy",
        math.isclose(energy, 365.0, abs_tol=1.0e-12),
        f"nominal sqrt(s)={energy:g} GeV",
    )

    sample = pilot.get("sample", {})
    record(
        "pilot_sample_contract",
        sample.get("initial_state") == "ee"
        and sample.get("decay_channel") == "epmum"
        and sample.get("polarization") == "LR100"
        and sample.get("spin_mode") == "sc"
        and bool(sample.get("isr")),
        "canonical smoke sample is ee/epmum/LR100/SC with ISR",
    )

    convention = paper.get("convention", {})
    record(
        "frozen_convention_name",
        convention.get("name") == "lepton_collider_paper_v1",
        f"convention={convention.get('name')}",
    )
    record(
        "four_vector_analyzers",
        convention.get("analyzer_source") == "four_vectors"
        and bool(convention.get("four_vector_reconstruction_reviewed")),
        "four-vector analyzer source remains reviewed",
    )

    for key, expected in EXPECTED_TRANSFORMS.items():
        record(
            f"frozen_{key}",
            convention.get(key) == expected,
            f"{key} matches frozen 500 GeV convention",
        )

    record(
        "raw_analyzer_signs",
        float(convention.get("raw_plus_sign", 0.0)) == 1.0
        and float(convention.get("raw_minus_sign", 0.0)) == 1.0,
        "raw analyzer signs are +1,+1",
    )

    derived = convention.get("derived_kinematics", {})
    record(
        "canonical_costheta",
        bool(derived.get("reviewed"))
        and derived.get("costheta_column") == "paper_cos_theta_t",
        "paper_cos_theta_t is the reviewed production angle",
    )

    mass_top = float(sm.get("mass_top_GeV", float("nan")))
    threshold = 2.0 * mass_top
    gap = energy - threshold
    record(
        "threshold_gap_positive",
        finite(gap) and gap > 0.0,
        f"sqrt(s)-2m_top={gap:.6f} GeV",
        nominal_threshold_GeV=threshold,
        nominal_gap_GeV=gap,
    )

    record(
        "generator_parameter_match",
        bool(sm.get("generator_match_reviewed"))
        and math.isclose(
            float(sm.get("alpha_em_inverse", 0.0)),
            132.5049458125,
            rel_tol=0.0,
            abs_tol=1.0e-10,
        )
        and math.isclose(mass_top, 173.1, rel_tol=0.0, abs_tol=1.0e-12),
        "SM parameters match the frozen WHIZARD 3.1.5 generator scheme",
    )

    record(
        "threshold_scope_lock",
        sm.get("threshold_resummation_included") is False
        and sm.get("nonresonant_backgrounds_included") is False,
        "continuum sample does not claim threshold resummation or nonresonant backgrounds",
    )

    validation = paper.get("validation", {})
    record(
        "full_matrix_contract",
        int(validation.get("expected_samples", -1)) == 32
        and int(validation.get("lhe_hepmc_expected_paired_groups", -1)) == 16,
        "full campaign expects 32 ntuples and 16 LHE/HepMC pairs",
    )

    variables = {
        item.get("name"): item
        for item in paper.get("differential", {}).get("variables", [])
        if isinstance(item, dict)
    }
    mtt = variables.get("mtt_GeV", {})
    edges = [float(value) for value in mtt.get("edges", [])]
    record(
        "pilot_threshold_binning",
        len(edges) >= 3
        and all(right > left for left, right in zip(edges, edges[1:]))
        and edges[0] <= threshold
        and edges[-1] >= energy,
        f"initial mtt binning spans {edges[0] if edges else None} to {edges[-1] if edges else None} GeV",
        edges=edges,
    )
    return checks


def audit_lhe(
    path: Path,
    repo_root: Path,
    pilot: dict[str, Any],
    sm: dict[str, Any],
    max_events: int | None,
) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(repo_root))
    from qis_ttbar.io.lhe import extract_ttbar_truth, iter_lhe_events, parse_lhe_header

    sample = pilot["sample"]
    validation = pilot["validation"]
    threshold_config = pilot["threshold_audit"]
    initial_state = str(sample["initial_state"])
    required_decay = str(validation["require_decay_channel"])
    nominal_energy = float(pilot["nominal_sqrt_s_GeV"])
    nominal_top_mass = float(threshold_config["nominal_top_mass_GeV"])
    threshold = 2.0 * nominal_top_mass

    header = parse_lhe_header(path)
    mtt_values: list[float] = []
    beta_values: list[float] = []
    top_masses: list[float] = []
    antitop_masses: list[float] = []
    weights: list[float] = []
    closure_values: list[float] = []
    decay_mismatches = 0
    nonfinite_weights = 0

    for event in iter_lhe_events(path, max_events=max_events):
        truth = extract_ttbar_truth(event, initial_state)
        if truth.decay_channel != required_decay:
            decay_mismatches += 1

        pair = add_p4(truth.top, truth.antitop)
        current_mtt = mass(pair)
        current_beta2 = 1.0 - (threshold * threshold) / (current_mtt * current_mtt)
        current_beta = math.sqrt(max(0.0, current_beta2))

        top_mass = mass(p4_values(truth.top))
        antitop_mass = mass(p4_values(truth.antitop))
        top_closure = euclidean4(
            subtract_p4(truth.top, truth.b, truth.lepton_plus, truth.neutrino)
        )
        antitop_closure = euclidean4(
            subtract_p4(
                truth.antitop,
                truth.bbar,
                truth.lepton_minus,
                truth.antineutrino,
            )
        )

        weight = float(event.weight)
        if not finite(weight):
            nonfinite_weights += 1

        mtt_values.append(current_mtt)
        beta_values.append(current_beta)
        top_masses.append(top_mass)
        antitop_masses.append(antitop_mass)
        weights.append(weight)
        closure_values.extend([top_closure, antitop_closure])

    if not mtt_values:
        raise ValueError(f"No events found in {path}")

    probabilities = [float(value) for value in threshold_config["record_quantiles"]]
    sorted_mtt = sorted(mtt_values)
    sorted_beta = sorted(beta_values)
    summary = {
        "lhe_path": str(path),
        "events_audited": len(mtt_values),
        "header": {
            "beam1_pdg": header.beam1_pdg,
            "beam2_pdg": header.beam2_pdg,
            "beam1_energy_GeV": header.beam1_energy_GeV,
            "beam2_energy_GeV": header.beam2_energy_GeV,
            "nominal_energy_GeV": header.beam1_energy_GeV + header.beam2_energy_GeV,
            "cross_section_pb": header.cross_section_pb,
            "cross_section_error_pb": header.cross_section_error_pb,
            "declared_events": header.declared_events,
        },
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
        "maximum_top_decay_closure_residual_GeV": max(closure_values),
        "decay_channel_mismatches": decay_mismatches,
        "nonfinite_weights": nonfinite_weights,
        "negative_weights": sum(weight < 0.0 for weight in weights if finite(weight)),
        "nominal_threshold_GeV": threshold,
        "fraction_below_350_GeV": sum(value < 350.0 for value in mtt_values)
        / len(mtt_values),
    }

    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, message: str) -> None:
        checks.append(
            {"check": name, "status": "pass" if passed else "fail", "message": message}
        )

    header_energy = header.beam1_energy_GeV + header.beam2_energy_GeV
    energy_tolerance = float(validation["nominal_energy_tolerance_GeV"])
    record(
        "lhe_header_energy",
        math.isclose(header_energy, nominal_energy, abs_tol=energy_tolerance),
        f"LHE beam-energy sum={header_energy:.12g} GeV",
    )
    minimum_events = int(validation["minimum_generated_events"])
    record(
        "event_count",
        len(mtt_values) >= minimum_events,
        f"audited events={len(mtt_values)}, required={minimum_events}",
    )
    record(
        "decay_channel",
        decay_mismatches == 0,
        f"decay mismatches={decay_mismatches}",
    )
    record(
        "finite_weights",
        nonfinite_weights <= int(validation["maximum_nonfinite_weights"]),
        f"nonfinite weights={nonfinite_weights}",
    )
    record(
        "nonnegative_weights",
        summary["negative_weights"] == 0,
        f"negative weights={summary['negative_weights']}",
    )
    record(
        "top_decay_closure",
        max(closure_values)
        <= float(validation["maximum_top_decay_closure_residual_GeV"]),
        f"maximum closure residual={max(closure_values):.6g} GeV",
    )
    record(
        "mtt_above_threshold",
        min(mtt_values) >= threshold - float(validation["threshold_tolerance_GeV"]),
        f"minimum mtt={min(mtt_values):.6f} GeV; threshold={threshold:.6f} GeV",
    )
    record(
        "mtt_not_above_nominal",
        max(mtt_values)
        <= nominal_energy + float(validation["maximum_mtt_above_nominal_GeV"]),
        f"maximum mtt={max(mtt_values):.6f} GeV; nominal={nominal_energy:.6f} GeV",
    )
    summary["checks"] = checks
    summary["status"] = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--paper-config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV.yaml"),
    )
    parser.add_argument(
        "--pilot-config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_pilot.yaml"),
    )
    parser.add_argument(
        "--sm-config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_sm_parameters.yaml"),
    )
    parser.add_argument("--lhe", type=Path)
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser


def resolve(repo: Path, path: Path) -> Path:
    return path.expanduser().resolve() if path.is_absolute() else (repo / path).resolve()


def main() -> int:
    args = build_parser().parse_args()
    repo = args.repo_root.expanduser().resolve()
    paper_path = resolve(repo, args.paper_config)
    pilot_path = resolve(repo, args.pilot_config)
    sm_path = resolve(repo, args.sm_config)

    paper = load_yaml(paper_path)
    pilot = load_yaml(pilot_path)
    sm = load_yaml(sm_path)
    checks = config_checks(paper, pilot, sm)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "paper_config": str(paper_path),
        "pilot_config": str(pilot_path),
        "sm_config": str(sm_path),
        "config_checks": checks,
    }

    config_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    payload["config_status"] = config_status

    if args.lhe is not None:
        lhe_path = resolve(repo, args.lhe)
        payload["lhe_audit"] = audit_lhe(lhe_path, repo, pilot, sm, args.max_events)

    statuses = [config_status]
    if "lhe_audit" in payload:
        statuses.append(payload["lhe_audit"]["status"])
    payload["status"] = "pass" if all(status == "pass" for status in statuses) else "fail"

    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        output = resolve(repo, args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered)
    print(rendered, end="")
    return 1 if args.strict and payload["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
