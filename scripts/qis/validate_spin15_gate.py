#!/usr/bin/env python3
"""Validate the complete 15-observable ttbar polarization/spin gate.

The input is the coefficient table written by plot_spin15_distributions.py.
The validator performs four logically separate checks:

1. Structural completeness and bounded event-level observable ranges.
2. Beam-polarization configuration audit for LR100 and RL100 samples.
3. Preservation of the 15 extracted coefficients from LHE to HepMC3.
4. Physics discrimination:
   - LR100 versus RL100 separation using the six B coefficients;
   - spin-correlated versus isotropic-decay separation using the nine
     connected correlations D_ij = C_ij - B1_i B2_j;
   - e+mu- versus mu+e- decay-flavour consistency.

No hard-coded Standard Model sign is imposed.  The authoritative LHE truth is
used as the reference, and the showered HepMC sample must preserve it.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qis_ttbar.physics.observables import (  # noqa: E402
    SPIN15_COEFFICIENT_NAMES,
    SPIN15_EVENT_COLUMNS,
)

COEFFICIENT_BY_OBSERVABLE = dict(
    zip(SPIN15_EVENT_COLUMNS, SPIN15_COEFFICIENT_NAMES, strict=True)
)
B_OBSERVABLES = ("b1k", "b1r", "b1n", "b2k", "b2r", "b2n")
C_OBSERVABLES = ("ckk", "ckr", "ckn", "crk", "crr", "crn", "cnk", "cnr", "cnn")
AXES = ("k", "r", "n")

SAMPLE_RE = re.compile(
    r"^(?P<initial_state>ee|mumu)_ttbar_"
    r"(?P<decay_channel>epmum|mupem)_"
    r"(?P<polarization>LR100|RL100|unpol)_"
    r"(?P<spin_mode>sc|iso)_ISR_"
    r"(?P<sqrt_s>[0-9]+)GeV$"
)


@dataclass(frozen=True)
class GateThresholds:
    preservation_max_abs: float
    preservation_max_z: float
    polarization_min_z: float
    spin_correlation_min_z: float
    flavour_consistency_max_z: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coefficients", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--production-config",
        action="append",
        default=[],
        type=Path,
        help="Production CSV to audit. Repeat for SC and ISO configurations.",
    )
    parser.add_argument("--lhe-sc-label", default="lhe_sc")
    parser.add_argument("--hepmc-sc-label", default="hepmc_sc")
    parser.add_argument("--lhe-iso-label", default="lhe_iso")
    parser.add_argument("--hepmc-iso-label", default="hepmc_iso")
    parser.add_argument("--preservation-max-abs", type=float, default=0.02)
    parser.add_argument("--preservation-max-z", type=float, default=5.0)
    parser.add_argument("--polarization-min-z", type=float, default=5.0)
    parser.add_argument("--spin-correlation-min-z", type=float, default=5.0)
    parser.add_argument("--flavour-consistency-max-z", type=float, default=5.0)
    parser.add_argument(
        "--strict-physics",
        action="store_true",
        help="Return nonzero when a physics-separation/preservation requirement fails.",
    )
    return parser.parse_args()


def safe_z(delta: float, first_se: float, second_se: float) -> float:
    denominator = math.hypot(first_se, second_se)
    if denominator > 0.0 and math.isfinite(denominator):
        return delta / denominator
    if abs(delta) <= 1.0e-14:
        return 0.0
    return math.copysign(math.inf, delta)


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def sample_identity(row: pd.Series | dict[str, object]) -> tuple[str, str, str, str, int]:
    return (
        str(row["initial_state"]),
        str(row["decay_channel"]),
        str(row["polarization"]),
        str(row["spin_mode"]),
        int(float(row["sqrt_s_GeV"])),
    )


def stage_from_dataset(label: str) -> str:
    lowered = label.lower()
    if "hepmc" in lowered:
        return "hepmc"
    if "lhe" in lowered:
        return "lhe"
    raise ValueError(
        f"cannot infer stage from dataset label {label!r}; include 'lhe' or 'hepmc'"
    )


def spin_from_dataset(label: str) -> str:
    lowered = label.lower()
    if lowered.endswith("_sc") or "_sc_" in lowered:
        return "sc"
    if lowered.endswith("_iso") or "_iso_" in lowered:
        return "iso"
    raise ValueError(
        f"cannot infer spin mode from dataset label {label!r}; include '_sc' or '_iso'"
    )


def audit_production_config(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows: list[dict[str, object]] = []
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "sample_id",
            "enabled",
            "initial_state",
            "decay_channel",
            "polarization",
            "beam1_helicity",
            "beam2_helicity",
            "beam1_pol_fraction",
            "beam2_pol_fraction",
            "spin_correlated",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"{path}: missing columns {sorted(required - set(reader.fieldnames or []))}"
            )
        for source in reader:
            if not parse_bool(source["enabled"]):
                continue
            sample_id = source["sample_id"]
            match = SAMPLE_RE.match(sample_id)
            messages: list[str] = []
            if not match:
                messages.append("sample ID does not match canonical convention")
            else:
                for field in ("initial_state", "decay_channel", "polarization"):
                    if source[field] != match.group(field):
                        messages.append(
                            f"{field}={source[field]!r} disagrees with sample ID "
                            f"{match.group(field)!r}"
                        )
                expected_spin = match.group("spin_mode") == "sc"
                if parse_bool(source["spin_correlated"]) != expected_spin:
                    messages.append(
                        "spin_correlated disagrees with sc/iso sample ID"
                    )

            polarization = source["polarization"]
            h1 = int(source["beam1_helicity"])
            h2 = int(source["beam2_helicity"])
            f1 = float(source["beam1_pol_fraction"])
            f2 = float(source["beam2_pol_fraction"])
            expected_helicities = {
                "LR100": (-1, 1),
                "RL100": (1, -1),
            }.get(polarization)
            if expected_helicities is None:
                messages.append(f"unsupported polarization label {polarization!r}")
            elif (h1, h2) != expected_helicities:
                messages.append(
                    f"helicities {(h1, h2)} do not match {polarization} "
                    f"expectation {expected_helicities}"
                )
            if not math.isclose(f1, 1.0, abs_tol=1.0e-12):
                messages.append(f"beam1_pol_fraction={f1} is not 1.0")
            if not math.isclose(f2, 1.0, abs_tol=1.0e-12):
                messages.append(f"beam2_pol_fraction={f2} is not 1.0")

            rows.append(
                {
                    "config": str(path),
                    "sample_id": sample_id,
                    "polarization": polarization,
                    "beam1_helicity": h1,
                    "beam2_helicity": h2,
                    "beam1_pol_fraction": f1,
                    "beam2_pol_fraction": f2,
                    "spin_correlated": parse_bool(source["spin_correlated"]),
                    "status": "pass" if not messages else "fail",
                    "messages": "; ".join(messages),
                }
            )
    if not rows:
        raise ValueError(f"{path}: no enabled rows")
    return rows


def validate_structure(frame: pd.DataFrame) -> tuple[list[dict[str, object]], list[str]]:
    required = {
        "dataset",
        "sample_id",
        "initial_state",
        "decay_channel",
        "polarization",
        "spin_mode",
        "sqrt_s_GeV",
        "observable",
        "coefficient_name",
        "coefficient",
        "coefficient_se",
        "min",
        "max",
        "in_unit_interval",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"coefficient table missing columns: {missing}")

    rows: list[dict[str, object]] = []
    failures: list[str] = []

    for (dataset, sample_id), group in frame.groupby(["dataset", "sample_id"], sort=True):
        messages: list[str] = []
        observed = set(group["observable"].astype(str))
        missing_observables = sorted(set(SPIN15_EVENT_COLUMNS) - observed)
        extras = sorted(observed - set(SPIN15_EVENT_COLUMNS))
        if missing_observables:
            messages.append(f"missing observables {missing_observables}")
        if extras:
            messages.append(f"unexpected observables {extras}")
        if len(group) != len(SPIN15_EVENT_COLUMNS):
            messages.append(f"row count is {len(group)}, expected 15")

        match = SAMPLE_RE.match(str(sample_id))
        if not match:
            messages.append("sample ID does not match canonical convention")
        else:
            first = group.iloc[0]
            for field in ("initial_state", "decay_channel", "polarization", "spin_mode"):
                if str(first[field]) != match.group(field):
                    messages.append(
                        f"{field}={first[field]!r} disagrees with sample ID"
                    )

        for _, source in group.iterrows():
            observable = str(source["observable"])
            expected_name = COEFFICIENT_BY_OBSERVABLE.get(observable)
            if source["coefficient_name"] != expected_name:
                messages.append(
                    f"{observable}: coefficient name {source['coefficient_name']!r} "
                    f"!= {expected_name!r}"
                )
            numbers = (
                float(source["coefficient"]),
                float(source["coefficient_se"]),
                float(source["min"]),
                float(source["max"]),
            )
            if not all(math.isfinite(value) for value in numbers):
                messages.append(f"{observable}: nonfinite summary value")
            if float(source["coefficient_se"]) < 0.0:
                messages.append(f"{observable}: negative coefficient uncertainty")
            if not parse_bool(source["in_unit_interval"]):
                messages.append(
                    f"{observable}: event range [{source['min']}, {source['max']}] "
                    "is outside [-1,1]"
                )

        status = "pass" if not messages else "fail"
        rows.append(
            {
                "dataset": dataset,
                "sample_id": sample_id,
                "observable_rows": len(group),
                "status": status,
                "messages": "; ".join(messages),
            }
        )
        if messages:
            failures.append(f"{dataset}/{sample_id}: {'; '.join(messages)}")

    return rows, failures


def indexed_coefficients(frame: pd.DataFrame) -> dict[tuple[str, str, str, str, str, int, str], pd.Series]:
    index: dict[tuple[str, str, str, str, str, int, str], pd.Series] = {}
    for _, row in frame.iterrows():
        key = (
            str(row["dataset"]),
            str(row["initial_state"]),
            str(row["decay_channel"]),
            str(row["polarization"]),
            str(row["spin_mode"]),
            int(float(row["sqrt_s_GeV"])),
            str(row["observable"]),
        )
        if key in index:
            raise ValueError(f"duplicate coefficient row for {key}")
        index[key] = row
    return index


def preservation_rows(
    frame: pd.DataFrame,
    *,
    pairs: Iterable[tuple[str, str, str]],
    thresholds: GateThresholds,
) -> list[dict[str, object]]:
    index = indexed_coefficients(frame)
    rows: list[dict[str, object]] = []
    for lhe_label, hepmc_label, spin_mode in pairs:
        lhe_samples = frame[
            (frame["dataset"] == lhe_label) & (frame["spin_mode"] == spin_mode)
        ][["initial_state", "decay_channel", "polarization", "sqrt_s_GeV"]].drop_duplicates()
        for _, sample in lhe_samples.iterrows():
            base = (
                str(sample["initial_state"]),
                str(sample["decay_channel"]),
                str(sample["polarization"]),
                spin_mode,
                int(float(sample["sqrt_s_GeV"])),
            )
            for observable in SPIN15_EVENT_COLUMNS:
                left = index.get((lhe_label, *base, observable))
                right = index.get((hepmc_label, *base, observable))
                if left is None or right is None:
                    rows.append(
                        {
                            "spin_mode": spin_mode,
                            "initial_state": base[0],
                            "decay_channel": base[1],
                            "polarization": base[2],
                            "sqrt_s_GeV": base[4],
                            "observable": observable,
                            "lhe_dataset": lhe_label,
                            "hepmc_dataset": hepmc_label,
                            "status": "fail",
                            "message": "missing LHE or HepMC coefficient",
                        }
                    )
                    continue
                delta = float(right["coefficient"]) - float(left["coefficient"])
                z = safe_z(
                    delta,
                    float(left["coefficient_se"]),
                    float(right["coefficient_se"]),
                )
                abs_delta = abs(delta)
                large_shift = abs_delta > thresholds.preservation_max_abs
                significant_shift = abs(z) > thresholds.preservation_max_z
                if large_shift and significant_shift:
                    status = "fail"
                    message = (
                        "absolute shift and significance thresholds exceeded"
                    )
                elif large_shift:
                    status = "warn"
                    message = "absolute shift threshold exceeded only"
                elif significant_shift:
                    status = "warn"
                    message = "significance threshold exceeded only"
                else:
                    status = "pass"
                    message = ""
                rows.append(
                    {
                        "spin_mode": spin_mode,
                        "initial_state": base[0],
                        "decay_channel": base[1],
                        "polarization": base[2],
                        "sqrt_s_GeV": base[4],
                        "observable": observable,
                        "coefficient_name": COEFFICIENT_BY_OBSERVABLE[observable],
                        "lhe_dataset": lhe_label,
                        "hepmc_dataset": hepmc_label,
                        "lhe_coefficient": float(left["coefficient"]),
                        "lhe_se": float(left["coefficient_se"]),
                        "hepmc_coefficient": float(right["coefficient"]),
                        "hepmc_se": float(right["coefficient_se"]),
                        "delta_hepmc_minus_lhe": delta,
                        "abs_delta": abs_delta,
                        "z": z,
                        "large_shift": large_shift,
                        "significant_shift": significant_shift,
                        "status": status,
                        "message": message,
                    }
                )
    return rows


def polarization_rows(
    frame: pd.DataFrame,
    *,
    thresholds: GateThresholds,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    index = indexed_coefficients(frame)
    details: list[dict[str, object]] = []
    groups: list[dict[str, object]] = []
    keys = frame[["dataset", "initial_state", "decay_channel", "spin_mode", "sqrt_s_GeV"]].drop_duplicates()
    for _, key_row in keys.iterrows():
        dataset = str(key_row["dataset"])
        initial = str(key_row["initial_state"])
        decay = str(key_row["decay_channel"])
        mode = str(key_row["spin_mode"])
        sqrt_s = int(float(key_row["sqrt_s_GeV"]))
        group_details = []
        for observable in B_OBSERVABLES:
            lr = index.get((dataset, initial, decay, "LR100", mode, sqrt_s, observable))
            rl = index.get((dataset, initial, decay, "RL100", mode, sqrt_s, observable))
            if lr is None or rl is None:
                continue
            delta = float(lr["coefficient"]) - float(rl["coefficient"])
            z = safe_z(delta, float(lr["coefficient_se"]), float(rl["coefficient_se"]))
            detail = {
                "dataset": dataset,
                "stage": stage_from_dataset(dataset),
                "initial_state": initial,
                "decay_channel": decay,
                "spin_mode": mode,
                "sqrt_s_GeV": sqrt_s,
                "observable": observable,
                "coefficient_name": COEFFICIENT_BY_OBSERVABLE[observable],
                "lr_coefficient": float(lr["coefficient"]),
                "lr_se": float(lr["coefficient_se"]),
                "rl_coefficient": float(rl["coefficient"]),
                "rl_se": float(rl["coefficient_se"]),
                "delta_lr_minus_rl": delta,
                "z": z,
            }
            details.append(detail)
            group_details.append(detail)
        if not group_details:
            groups.append(
                {
                    "dataset": dataset,
                    "initial_state": initial,
                    "decay_channel": decay,
                    "spin_mode": mode,
                    "sqrt_s_GeV": sqrt_s,
                    "max_abs_z": math.nan,
                    "leading_observable": "",
                    "status": "fail",
                    "message": "missing LR100/RL100 B-coefficient pair",
                }
            )
            continue
        leading = max(group_details, key=lambda row: abs(float(row["z"])))
        max_abs_z = abs(float(leading["z"]))
        if mode == "iso":
            status = "not_applicable"
            message = (
                "LR/RL B-vector separation is not required for isotropic "
                "decay-control samples"
            )
        else:
            status = (
                "pass"
                if max_abs_z >= thresholds.polarization_min_z
                else "fail"
            )
            message = ""
        groups.append(
            {
                "dataset": dataset,
                "stage": stage_from_dataset(dataset),
                "initial_state": initial,
                "decay_channel": decay,
                "spin_mode": mode,
                "sqrt_s_GeV": sqrt_s,
                "max_abs_z": max_abs_z,
                "leading_observable": leading["observable"],
                "leading_delta": leading["delta_lr_minus_rl"],
                "status": status,
                "message": message,
            }
        )
    return details, groups


def sample_coefficient_map(group: pd.DataFrame) -> dict[str, tuple[float, float]]:
    return {
        str(row["observable"]): (
            float(row["coefficient"]),
            float(row["coefficient_se"]),
        )
        for _, row in group.iterrows()
    }


def connected_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    grouping = [
        "dataset",
        "sample_id",
        "initial_state",
        "decay_channel",
        "polarization",
        "spin_mode",
        "sqrt_s_GeV",
    ]
    for keys, group in frame.groupby(grouping, sort=True):
        values = sample_coefficient_map(group)
        if not all(name in values for name in SPIN15_EVENT_COLUMNS):
            continue
        metadata = dict(zip(grouping, keys, strict=True))
        for first in AXES:
            for second in AXES:
                c_name = f"c{first}{second}"
                b1_name = f"b1{first}"
                b2_name = f"b2{second}"
                c, c_se = values[c_name]
                b1, b1_se = values[b1_name]
                b2, b2_se = values[b2_name]
                connected = c - b1 * b2
                # Delta-method uncertainty.  This deliberately neglects the
                # within-sample covariance between C_ij, B1_i, and B2_j; the
                # full tomography bootstrap remains the final precision tool.
                connected_se = math.sqrt(
                    c_se * c_se
                    + (b2 * b1_se) ** 2
                    + (b1 * b2_se) ** 2
                )
                rows.append(
                    {
                        **metadata,
                        "observable": c_name,
                        "connected_name": f"D{first}{second}",
                        "Cij": c,
                        "B1i": b1,
                        "B2j": b2,
                        "connected": connected,
                        "connected_se": connected_se,
                    }
                )
    return pd.DataFrame(rows)


def spin_correlation_rows(
    connected: pd.DataFrame,
    *,
    sc_labels: dict[str, str],
    iso_labels: dict[str, str],
    thresholds: GateThresholds,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    details: list[dict[str, object]] = []
    groups: list[dict[str, object]] = []
    index: dict[tuple[str, str, str, str, int, str], pd.Series] = {}
    for _, row in connected.iterrows():
        key = (
            str(row["dataset"]),
            str(row["initial_state"]),
            str(row["decay_channel"]),
            str(row["polarization"]),
            int(float(row["sqrt_s_GeV"])),
            str(row["observable"]),
        )
        index[key] = row

    for stage in ("lhe", "hepmc"):
        sc_label = sc_labels[stage]
        iso_label = iso_labels[stage]
        sc_samples = connected[connected["dataset"] == sc_label][
            ["initial_state", "decay_channel", "polarization", "sqrt_s_GeV"]
        ].drop_duplicates()
        for _, sample in sc_samples.iterrows():
            initial = str(sample["initial_state"])
            decay = str(sample["decay_channel"])
            polarization = str(sample["polarization"])
            sqrt_s = int(float(sample["sqrt_s_GeV"]))
            group_details = []
            for observable in C_OBSERVABLES:
                sc = index.get((sc_label, initial, decay, polarization, sqrt_s, observable))
                iso = index.get((iso_label, initial, decay, polarization, sqrt_s, observable))
                if sc is None or iso is None:
                    continue
                delta = float(sc["connected"]) - float(iso["connected"])
                z = safe_z(
                    delta,
                    float(sc["connected_se"]),
                    float(iso["connected_se"]),
                )
                detail = {
                    "stage": stage,
                    "sc_dataset": sc_label,
                    "iso_dataset": iso_label,
                    "initial_state": initial,
                    "decay_channel": decay,
                    "polarization": polarization,
                    "sqrt_s_GeV": sqrt_s,
                    "observable": observable,
                    "connected_name": sc["connected_name"],
                    "sc_connected": float(sc["connected"]),
                    "sc_se": float(sc["connected_se"]),
                    "iso_connected": float(iso["connected"]),
                    "iso_se": float(iso["connected_se"]),
                    "delta_sc_minus_iso": delta,
                    "z": z,
                }
                details.append(detail)
                group_details.append(detail)
            if not group_details:
                groups.append(
                    {
                        "stage": stage,
                        "initial_state": initial,
                        "decay_channel": decay,
                        "polarization": polarization,
                        "sqrt_s_GeV": sqrt_s,
                        "max_abs_z": math.nan,
                        "leading_observable": "",
                        "status": "fail",
                        "message": "missing matched SC/ISO connected correlations",
                    }
                )
                continue
            leading = max(group_details, key=lambda row: abs(float(row["z"])))
            max_abs_z = abs(float(leading["z"]))
            groups.append(
                {
                    "stage": stage,
                    "initial_state": initial,
                    "decay_channel": decay,
                    "polarization": polarization,
                    "sqrt_s_GeV": sqrt_s,
                    "max_abs_z": max_abs_z,
                    "leading_observable": leading["observable"],
                    "leading_delta": leading["delta_sc_minus_iso"],
                    "status": "pass" if max_abs_z >= thresholds.spin_correlation_min_z else "fail",
                    "message": "",
                }
            )
    return details, groups


def flavour_consistency_rows(
    frame: pd.DataFrame,
    *,
    thresholds: GateThresholds,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    index = indexed_coefficients(frame)
    details: list[dict[str, object]] = []
    groups: list[dict[str, object]] = []
    keys = frame[["dataset", "initial_state", "polarization", "spin_mode", "sqrt_s_GeV"]].drop_duplicates()
    for _, key_row in keys.iterrows():
        dataset = str(key_row["dataset"])
        initial = str(key_row["initial_state"])
        polarization = str(key_row["polarization"])
        mode = str(key_row["spin_mode"])
        sqrt_s = int(float(key_row["sqrt_s_GeV"]))
        group_details = []
        for observable in SPIN15_EVENT_COLUMNS:
            first = index.get((dataset, initial, "epmum", polarization, mode, sqrt_s, observable))
            second = index.get((dataset, initial, "mupem", polarization, mode, sqrt_s, observable))
            if first is None or second is None:
                continue
            delta = float(first["coefficient"]) - float(second["coefficient"])
            z = safe_z(
                delta,
                float(first["coefficient_se"]),
                float(second["coefficient_se"]),
            )
            detail = {
                "dataset": dataset,
                "initial_state": initial,
                "polarization": polarization,
                "spin_mode": mode,
                "sqrt_s_GeV": sqrt_s,
                "observable": observable,
                "epmum_coefficient": float(first["coefficient"]),
                "epmum_se": float(first["coefficient_se"]),
                "mupem_coefficient": float(second["coefficient"]),
                "mupem_se": float(second["coefficient_se"]),
                "delta_epmum_minus_mupem": delta,
                "z": z,
            }
            details.append(detail)
            group_details.append(detail)
        if not group_details:
            groups.append(
                {
                    "dataset": dataset,
                    "initial_state": initial,
                    "polarization": polarization,
                    "spin_mode": mode,
                    "sqrt_s_GeV": sqrt_s,
                    "max_abs_z": math.nan,
                    "leading_observable": "",
                    "status": "fail",
                    "message": "missing epmum/mupem coefficient pairs",
                }
            )
            continue
        leading = max(group_details, key=lambda row: abs(float(row["z"])))
        max_abs_z = abs(float(leading["z"]))
        groups.append(
            {
                "dataset": dataset,
                "initial_state": initial,
                "polarization": polarization,
                "spin_mode": mode,
                "sqrt_s_GeV": sqrt_s,
                "max_abs_z": max_abs_z,
                "leading_observable": leading["observable"],
                "leading_delta": leading["delta_epmum_minus_mupem"],
                "status": "pass" if max_abs_z <= thresholds.flavour_consistency_max_z else "warn",
                "message": "",
            }
        )
    return details, groups


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def count_status(rows: Iterable[dict[str, object]], status: str) -> int:
    return sum(str(row.get("status", "")) == status for row in rows)


def main() -> int:
    args = parse_args()
    if not args.coefficients.is_file():
        raise FileNotFoundError(args.coefficients)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    thresholds = GateThresholds(
        preservation_max_abs=args.preservation_max_abs,
        preservation_max_z=args.preservation_max_z,
        polarization_min_z=args.polarization_min_z,
        spin_correlation_min_z=args.spin_correlation_min_z,
        flavour_consistency_max_z=args.flavour_consistency_max_z,
    )

    frame = pd.read_csv(args.coefficients)
    structure, structural_failures = validate_structure(frame)

    expected_labels = {
        args.lhe_sc_label: ("lhe", "sc"),
        args.hepmc_sc_label: ("hepmc", "sc"),
        args.lhe_iso_label: ("lhe", "iso"),
        args.hepmc_iso_label: ("hepmc", "iso"),
    }
    dataset_failures: list[str] = []
    for label, (expected_stage, expected_spin) in expected_labels.items():
        if label not in set(frame["dataset"].astype(str)):
            dataset_failures.append(f"missing required dataset {label}")
            continue
        if stage_from_dataset(label) != expected_stage:
            dataset_failures.append(f"dataset {label} has wrong stage convention")
        if spin_from_dataset(label) != expected_spin:
            dataset_failures.append(f"dataset {label} has wrong spin-mode convention")
        modes = set(frame.loc[frame["dataset"] == label, "spin_mode"].astype(str))
        if modes != {expected_spin}:
            dataset_failures.append(
                f"dataset {label} contains spin modes {sorted(modes)}, expected {expected_spin}"
            )

    config_audit: list[dict[str, object]] = []
    for path in args.production_config:
        config_audit.extend(audit_production_config(path))
    config_failures = [
        f"{row['sample_id']}: {row['messages']}"
        for row in config_audit
        if row["status"] == "fail"
    ]

    preservation = preservation_rows(
        frame,
        pairs=(
            (args.lhe_sc_label, args.hepmc_sc_label, "sc"),
            (args.lhe_iso_label, args.hepmc_iso_label, "iso"),
        ),
        thresholds=thresholds,
    )
    preservation_failures = [
        row for row in preservation if row.get("status") == "fail"
    ]
    preservation_warnings = [
        row for row in preservation if row.get("status") == "warn"
    ]

    polarization_details, polarization_groups = polarization_rows(
        frame, thresholds=thresholds
    )
    polarization_failures = [
        row for row in polarization_groups if row.get("status") == "fail"
    ]
    polarization_not_applicable = [
        row
        for row in polarization_groups
        if row.get("status") == "not_applicable"
    ]

    connected = connected_correlations(frame)
    connected_path = args.output_dir / "spin15_connected_correlations.csv"
    connected.to_csv(connected_path, index=False)
    spin_details, spin_groups = spin_correlation_rows(
        connected,
        sc_labels={"lhe": args.lhe_sc_label, "hepmc": args.hepmc_sc_label},
        iso_labels={"lhe": args.lhe_iso_label, "hepmc": args.hepmc_iso_label},
        thresholds=thresholds,
    )
    spin_failures = [row for row in spin_groups if row.get("status") == "fail"]

    flavour_details, flavour_groups = flavour_consistency_rows(
        frame, thresholds=thresholds
    )
    flavour_warnings = [row for row in flavour_groups if row.get("status") == "warn"]
    flavour_failures = [row for row in flavour_groups if row.get("status") == "fail"]

    products = {
        "structure": args.output_dir / "spin15_structure.csv",
        "production_config_audit": args.output_dir / "beam_polarization_config_audit.csv",
        "lhe_hepmc_preservation": args.output_dir / "spin15_lhe_hepmc_preservation.csv",
        "polarization_details": args.output_dir / "spin15_lr_rl_details.csv",
        "polarization_groups": args.output_dir / "spin15_lr_rl_gate.csv",
        "spin_details": args.output_dir / "spin15_sc_iso_details.csv",
        "spin_groups": args.output_dir / "spin15_sc_iso_gate.csv",
        "flavour_details": args.output_dir / "spin15_decay_flavour_details.csv",
        "flavour_groups": args.output_dir / "spin15_decay_flavour_gate.csv",
    }
    write_csv(products["structure"], structure)
    write_csv(products["production_config_audit"], config_audit)
    write_csv(products["lhe_hepmc_preservation"], preservation)
    write_csv(products["polarization_details"], polarization_details)
    write_csv(products["polarization_groups"], polarization_groups)
    write_csv(products["spin_details"], spin_details)
    write_csv(products["spin_groups"], spin_groups)
    write_csv(products["flavour_details"], flavour_details)
    write_csv(products["flavour_groups"], flavour_groups)

    structural_ok = not (
        structural_failures or dataset_failures or config_failures or flavour_failures
    )
    physics_ok = not (
        preservation_failures or polarization_failures or spin_failures
    )
    overall_ok = structural_ok and (physics_ok or not args.strict_physics)

    report_path = args.output_dir / "spin15_gate_report.md"
    with report_path.open("w") as stream:
        stream.write("# Spin-15 production qualification gate\n\n")
        stream.write(f"- Coefficient table: `{args.coefficients}`\n")
        stream.write(f"- Structural status: **{'PASS' if structural_ok else 'FAIL'}**\n")
        stream.write(f"- Physics status: **{'PASS' if physics_ok else 'FAIL'}**\n")
        stream.write(f"- Strict physics mode: `{args.strict_physics}`\n\n")
        stream.write("## Observable contract\n\n")
        stream.write("Six polarization analyzers:\n\n")
        stream.write("`b1k, b1r, b1n, b2k, b2r, b2n`\n\n")
        stream.write("Nine correlation analyzers:\n\n")
        stream.write("`ckk, crr, cnn, ckr, crk, ckn, cnk, crn, cnr`\n\n")
        stream.write("## Gate counts\n\n")
        stream.write(
            "| Check | Groups/rows | Fail | Warn | N/A |\n"
            "|---|---:|---:|---:|---:|\n"
        )
        stream.write(
            f"| Sample structure | {len(structure)} | "
            f"{count_status(structure, 'fail')} | 0 | 0 |\n"
        )
        stream.write(
            f"| Beam configuration audit | {len(config_audit)} | "
            f"{count_status(config_audit, 'fail')} | 0 | 0 |\n"
        )
        stream.write(
            f"| LHE to HepMC coefficients | {len(preservation)} | "
            f"{len(preservation_failures)} | {len(preservation_warnings)} | 0 |\n"
        )
        stream.write(
            f"| LR100 versus RL100 | {len(polarization_groups)} | "
            f"{len(polarization_failures)} | 0 | "
            f"{len(polarization_not_applicable)} |\n"
        )
        stream.write(
            f"| SC versus ISO connected correlations | {len(spin_groups)} | "
            f"{len(spin_failures)} | 0 | 0 |\n"
        )
        stream.write(
            f"| epmum versus mupem consistency | {len(flavour_groups)} | "
            f"{len(flavour_failures)} | {len(flavour_warnings)} | 0 |\n\n"
        )
        stream.write("## Thresholds\n\n")
        stream.write(
            f"- LHE/HepMC maximum absolute coefficient shift: "
            f"{thresholds.preservation_max_abs}\n"
            f"- LHE/HepMC maximum significance: "
            f"{thresholds.preservation_max_z}\n"
            "- LHE/HepMC policy: fail only when both limits are exceeded; "
            "a single-limit exceedance is a warning\n"
            f"- Minimum LR/RL separation for spin-correlated samples: "
            f"{thresholds.polarization_min_z} sigma in at least one B component\n"
            "- LR/RL separation for isotropic controls: not applicable\n"
            f"- Minimum SC/ISO separation: "
            f"{thresholds.spin_correlation_min_z} sigma in at least one connected "
            "correlation component\n"
            f"- Decay-flavour consistency warning threshold: "
            f"{thresholds.flavour_consistency_max_z} sigma\n\n"
        )
        stream.write("## Interpretation\n\n")
        stream.write(
            "No external sign template is imposed. The LHE coefficients define the "
            "generator-truth reference. Beam polarization is verified first by the "
            "configured helicities and then, for spin-correlated samples only, "
            "by LR/RL separation in the B vector. Isotropic-decay controls are "
            "not required to retain LR/RL analyzer separation. LHE/HepMC "
            "coefficient shifts are fatal only when they are both larger than "
            "the absolute tolerance and statistically significant; one-limit "
            "exceedances are retained as warnings. Spin correlation is verified "
            "by comparing connected correlations "
            "D_ij = C_ij - B1_i B2_j between matched spin-correlated and "
            "isotropic-decay samples.\n\n"
        )
        stream.write("## Products\n\n")
        for name, path in products.items():
            stream.write(f"- `{name}`: `{path}`\n")
        stream.write(f"- `connected_correlations`: `{connected_path}`\n")

    payload = {
        "schema_version": 1,
        "status": "pass" if overall_ok else "fail",
        "structural_status": "pass" if structural_ok else "fail",
        "physics_status": "pass" if physics_ok else "fail",
        "strict_physics": args.strict_physics,
        "thresholds": thresholds.__dict__,
        "counts": {
            "coefficient_rows": len(frame),
            "sample_groups": len(structure),
            "structural_failures": len(structural_failures),
            "dataset_failures": len(dataset_failures),
            "config_failures": len(config_failures),
            "preservation_failures": len(preservation_failures),
            "preservation_warnings": len(preservation_warnings),
            "polarization_failures": len(polarization_failures),
            "polarization_not_applicable": len(polarization_not_applicable),
            "spin_correlation_failures": len(spin_failures),
            "flavour_warnings": len(flavour_warnings),
            "flavour_failures": len(flavour_failures),
        },
        "messages": {
            "structural": structural_failures,
            "datasets": dataset_failures,
            "production_config": config_failures,
        },
        "products": {name: str(path) for name, path in products.items()},
        "connected_correlations": str(connected_path),
        "report": str(report_path),
    }
    json_path = args.output_dir / "spin15_gate_summary.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"Structural status: {'PASS' if structural_ok else 'FAIL'}")
    print(f"Physics status:    {'PASS' if physics_ok else 'FAIL'}")
    print(f"Wrote {report_path}")
    print(f"Wrote {json_path}")
    if preservation_warnings:
        print(f"LHE/HepMC preservation warnings: {len(preservation_warnings)}")
    if polarization_not_applicable:
        print(
            "LR/RL isotropic-control groups marked not applicable: "
            f"{len(polarization_not_applicable)}"
        )
    if flavour_warnings:
        print(f"Decay-flavour warnings: {len(flavour_warnings)}")
    if not overall_ok:
        print("SPIN15 QUALIFICATION GATE: FAIL")
        return 1
    print("SPIN15 QUALIFICATION GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
