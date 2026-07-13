#!/usr/bin/env python3
"""Construct production, dilepton, and helicity-basis observables.

Input tables are produced by parse_lhe_ttbar.py.  The helicity construction is
performed by first boosting all relevant four-vectors into the ttbar rest frame
and then boosting each charged lepton into its parent-top rest frame.  This
remains well-defined when ISR or a nontrivial beam-energy spectrum is added in
future campaigns.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

VECTOR_NAMES = (
    "beam1", "beam2", "top", "tbar", "b", "bbar", "lplus", "lminus", "nue", "numubar"
)

OUTPUT_FIELDS = [
    "sample_id",
    "initial_state",
    "polarization",
    "spin_mode",
    "sqrt_s_GeV",
    "event_index",
    "production_event_weight_fb",
    "exclusive_event_weight_fb",
    "m_tt_GeV",
    "tt_pt_GeV",
    "tt_rapidity",
    "top_energy_ttcm_GeV",
    "top_p_ttcm_GeV",
    "top_pt_GeV",
    "top_rapidity",
    "cos_theta_t",
    "antitop_pt_GeV",
    "antitop_rapidity",
    "m_ll_GeV",
    "delta_phi_ll",
    "delta_eta_ll",
    "delta_R_ll",
    "cos_opening_ll",
    "cos_opening_ll_ttcm",
    "lplus_energy_lab_GeV",
    "lminus_energy_lab_GeV",
    "lplus_energy_ttcm_GeV",
    "lminus_energy_ttcm_GeV",
    "lplus_energy_toprest_GeV",
    "lminus_energy_tbarrest_GeV",
    "cos_theta_star_plus",
    "cos_theta_star_minus",
    "cos_theta_star_product",
    "cos_theta_star_sum",
    "omega_ll",
    "top_mass_reco_GeV",
    "antitop_mass_reco_GeV",
    "event_finite",
    "validation_message",
]

OBSERVABLES = [
    field for field in OUTPUT_FIELDS
    if field not in {
        "sample_id", "initial_state", "polarization", "spin_mode", "sqrt_s_GeV",
        "event_index", "event_finite", "validation_message"
    }
]

SUMMARY_FIELDS = [
    "sample_id",
    "input_csv",
    "output_csv",
    "input_events",
    "output_events",
    "finite_events",
    "nonfinite_events",
    "max_abs_cos_theta_t",
    "max_abs_cos_theta_star_plus",
    "max_abs_cos_theta_star_minus",
    "mean_cos_theta_star_plus",
    "mean_cos_theta_star_minus",
    "mean_cos_theta_star_product",
    "status",
    "notes",
]


@dataclass(frozen=True)
class FourVector:
    energy: float
    px: float
    py: float
    pz: float

    def __add__(self, other: "FourVector") -> "FourVector":
        return FourVector(
            self.energy + other.energy,
            self.px + other.px,
            self.py + other.py,
            self.pz + other.pz,
        )

    @property
    def p2(self) -> float:
        return self.px * self.px + self.py * self.py + self.pz * self.pz

    @property
    def p(self) -> float:
        return math.sqrt(max(0.0, self.p2))

    @property
    def pt(self) -> float:
        return math.hypot(self.px, self.py)

    @property
    def mass2(self) -> float:
        return self.energy * self.energy - self.p2

    @property
    def mass(self) -> float:
        return math.sqrt(max(0.0, self.mass2))

    @property
    def beta(self) -> tuple[float, float, float]:
        if self.energy <= 0.0:
            raise ValueError("Cannot form beta from non-positive energy")
        return self.px / self.energy, self.py / self.energy, self.pz / self.energy

    @property
    def rapidity(self) -> float:
        plus = self.energy + self.pz
        minus = self.energy - self.pz
        if plus <= 0.0 or minus <= 0.0:
            return math.copysign(math.inf, self.pz)
        return 0.5 * math.log(plus / minus)

    @property
    def eta(self) -> float:
        p = self.p
        plus = p + self.pz
        minus = p - self.pz
        if plus <= 0.0 or minus <= 0.0:
            return math.copysign(math.inf, self.pz)
        return 0.5 * math.log(plus / minus)

    @property
    def phi(self) -> float:
        return math.atan2(self.py, self.px)

    def boost_to_frame(self, beta: tuple[float, float, float]) -> "FourVector":
        """Boost to a frame moving with velocity beta.

        E' = gamma (E - beta.p), so passing a system's own p/E sends that
        system to rest.
        """
        bx, by, bz = beta
        b2 = bx * bx + by * by + bz * bz
        if b2 < 1.0e-30:
            return self
        if b2 >= 1.0:
            raise ValueError(f"Unphysical boost beta^2={b2:.17g}")
        gamma = 1.0 / math.sqrt(1.0 - b2)
        bp = bx * self.px + by * self.py + bz * self.pz
        factor = ((gamma - 1.0) * bp / b2) - gamma * self.energy
        return FourVector(
            gamma * (self.energy - bp),
            self.px + factor * bx,
            self.py + factor * by,
            self.pz + factor * bz,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--summary-csv", type=Path, default=None)
    parser.add_argument("--sample", action="append", default=[], help="Sample ID/glob; repeatable")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def sample_selected(sample_id: str, patterns: list[str]) -> bool:
    if not patterns:
        return True
    from fnmatch import fnmatch

    return any(fnmatch(sample_id, pattern) for pattern in patterns)


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        raise ValueError(f"missing required field {key}")
    return float(value)


def vector(row: dict[str, str], name: str) -> FourVector:
    return FourVector(
        energy=as_float(row, f"{name}_E"),
        px=as_float(row, f"{name}_px"),
        py=as_float(row, f"{name}_py"),
        pz=as_float(row, f"{name}_pz"),
    )


def dot3(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def unit(v: FourVector) -> tuple[float, float, float]:
    norm = v.p
    if norm <= 0.0:
        raise ValueError("Cannot normalize zero three-momentum")
    return v.px / norm, v.py / norm, v.pz / norm


def clamp_cos(value: float, tolerance: float = 1.0e-10) -> float:
    if value > 1.0 and value <= 1.0 + tolerance:
        return 1.0
    if value < -1.0 and value >= -1.0 - tolerance:
        return -1.0
    return value


def delta_phi(phi1: float, phi2: float) -> float:
    value = math.atan2(math.sin(phi1 - phi2), math.cos(phi1 - phi2))
    return abs(value)


def opening_cos(a: FourVector, b: FourVector) -> float:
    if a.p <= 0.0 or b.p <= 0.0:
        raise ValueError("Opening angle requires nonzero momenta")
    return clamp_cos((a.px * b.px + a.py * b.py + a.pz * b.pz) / (a.p * b.p))


def finite_values(values: Iterable[float]) -> bool:
    return all(math.isfinite(value) for value in values)


def calculate(row: dict[str, str]) -> dict[str, str]:
    beam1 = vector(row, "beam1")
    top = vector(row, "top")
    tbar = vector(row, "tbar")
    lplus = vector(row, "lplus")
    lminus = vector(row, "lminus")

    tt = top + tbar
    beta_tt = tt.beta
    beam1_cm = beam1.boost_to_frame(beta_tt)
    top_cm = top.boost_to_frame(beta_tt)
    tbar_cm = tbar.boost_to_frame(beta_tt)
    lplus_cm = lplus.boost_to_frame(beta_tt)
    lminus_cm = lminus.boost_to_frame(beta_tt)

    axis_top = unit(top_cm)
    axis_tbar = unit(tbar_cm)
    beam_axis = unit(beam1_cm)

    lplus_top_rest = lplus_cm.boost_to_frame(top_cm.beta)
    lminus_tbar_rest = lminus_cm.boost_to_frame(tbar_cm.beta)

    cos_plus = clamp_cos(dot3(unit(lplus_top_rest), axis_top))
    cos_minus = clamp_cos(dot3(unit(lminus_tbar_rest), axis_tbar))
    cos_top = clamp_cos(dot3(axis_top, beam_axis))

    dphi = delta_phi(lplus.phi, lminus.phi)
    deta = lplus.eta - lminus.eta
    dr = math.hypot(deta, dphi)
    ll = lplus + lminus

    values = {
        "m_tt_GeV": tt.mass,
        "tt_pt_GeV": tt.pt,
        "tt_rapidity": tt.rapidity,
        "top_energy_ttcm_GeV": top_cm.energy,
        "top_p_ttcm_GeV": top_cm.p,
        "top_pt_GeV": top.pt,
        "top_rapidity": top.rapidity,
        "cos_theta_t": cos_top,
        "antitop_pt_GeV": tbar.pt,
        "antitop_rapidity": tbar.rapidity,
        "m_ll_GeV": ll.mass,
        "delta_phi_ll": dphi,
        "delta_eta_ll": deta,
        "delta_R_ll": dr,
        "cos_opening_ll": opening_cos(lplus, lminus),
        "cos_opening_ll_ttcm": opening_cos(lplus_cm, lminus_cm),
        "lplus_energy_lab_GeV": lplus.energy,
        "lminus_energy_lab_GeV": lminus.energy,
        "lplus_energy_ttcm_GeV": lplus_cm.energy,
        "lminus_energy_ttcm_GeV": lminus_cm.energy,
        "lplus_energy_toprest_GeV": lplus_top_rest.energy,
        "lminus_energy_tbarrest_GeV": lminus_tbar_rest.energy,
        "cos_theta_star_plus": cos_plus,
        "cos_theta_star_minus": cos_minus,
        "cos_theta_star_product": cos_plus * cos_minus,
        "cos_theta_star_sum": cos_plus + cos_minus,
        "omega_ll": cos_plus * cos_minus,
        "top_mass_reco_GeV": top.mass,
        "antitop_mass_reco_GeV": tbar.mass,
    }

    out = {field: "" for field in OUTPUT_FIELDS}
    for key in (
        "sample_id", "initial_state", "polarization", "spin_mode", "sqrt_s_GeV",
        "event_index", "production_event_weight_fb", "exclusive_event_weight_fb"
    ):
        out[key] = row.get(key, "")
    for key, value in values.items():
        out[key] = f"{value:.17g}"
    is_finite = finite_values(values.values())
    out["event_finite"] = "1" if is_finite else "0"
    out["validation_message"] = "" if is_finite else "one or more observables are non-finite"
    return out


def summarize(sample_id: str, input_csv: Path, output_csv: Path, rows: list[dict[str, str]], input_count: int, errors: int) -> dict[str, str]:
    def vals(key: str) -> list[float]:
        return [float(row[key]) for row in rows if row.get("event_finite") == "1" and row.get(key, "")]

    plus = vals("cos_theta_star_plus")
    minus = vals("cos_theta_star_minus")
    product = vals("cos_theta_star_product")
    top_cos = vals("cos_theta_t")
    finite = len(rows) - errors
    status = "PASS" if errors == 0 and len(rows) == input_count else "FAIL"
    notes = []
    if errors:
        notes.append(f"{errors} events failed observable construction")
    if len(rows) != input_count:
        notes.append(f"input rows={input_count}, output rows={len(rows)}")
    return {
        "sample_id": sample_id,
        "input_csv": str(input_csv),
        "output_csv": str(output_csv),
        "input_events": str(input_count),
        "output_events": str(len(rows)),
        "finite_events": str(finite),
        "nonfinite_events": str(errors),
        "max_abs_cos_theta_t": f"{max(map(abs, top_cos)):.17g}" if top_cos else "",
        "max_abs_cos_theta_star_plus": f"{max(map(abs, plus)):.17g}" if plus else "",
        "max_abs_cos_theta_star_minus": f"{max(map(abs, minus)):.17g}" if minus else "",
        "mean_cos_theta_star_plus": f"{statistics.fmean(plus):.17g}" if plus else "",
        "mean_cos_theta_star_minus": f"{statistics.fmean(minus):.17g}" if minus else "",
        "mean_cos_theta_star_product": f"{statistics.fmean(product):.17g}" if product else "",
        "status": status,
        "notes": "; ".join(notes),
    }


def process_file(input_csv: Path, output_csv: Path, overwrite: bool) -> dict[str, str]:
    sample_id = input_csv.name.removesuffix("_events.csv")
    if output_csv.exists() and not overwrite:
        return {
            "sample_id": sample_id,
            "input_csv": str(input_csv),
            "output_csv": str(output_csv),
            "input_events": "",
            "output_events": "",
            "finite_events": "",
            "nonfinite_events": "",
            "max_abs_cos_theta_t": "",
            "max_abs_cos_theta_star_plus": "",
            "max_abs_cos_theta_star_minus": "",
            "mean_cos_theta_star_plus": "",
            "mean_cos_theta_star_minus": "",
            "mean_cos_theta_star_product": "",
            "status": "SKIP",
            "notes": "output exists; use --overwrite",
        }

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_rows: list[dict[str, str]] = []
    input_count = errors = 0
    with input_csv.open(newline="") as source, output_csv.open("w", newline="") as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in reader:
            input_count += 1
            if row.get("event_valid") != "1":
                errors += 1
                continue
            try:
                out = calculate(row)
            except (ValueError, ZeroDivisionError, OverflowError) as exc:
                errors += 1
                out = {field: "" for field in OUTPUT_FIELDS}
                for key in ("sample_id", "initial_state", "polarization", "spin_mode", "sqrt_s_GeV", "event_index"):
                    out[key] = row.get(key, "")
                out["event_finite"] = "0"
                out["validation_message"] = str(exc)
            writer.writerow(out)
            output_rows.append(out)

    return summarize(sample_id, input_csv, output_csv, output_rows, input_count, errors)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    input_dir = (args.input_dir or root / "validation" / "angular_tables" / "events").resolve()
    output_dir = (args.output_dir or root / "validation" / "angular_tables" / "observables").resolve()
    summary_csv = (args.summary_csv or root / "validation" / "angular_summaries" / "spin_observable_summary.csv").resolve()

    inputs = sorted(input_dir.glob("*_events.csv"))
    inputs = [path for path in inputs if sample_selected(path.name.removesuffix("_events.csv"), args.sample)]
    if not inputs:
        print(f"ERROR: no parsed event tables found in {input_dir}", file=sys.stderr)
        return 2

    summaries = []
    for input_csv in inputs:
        sample_id = input_csv.name.removesuffix("_events.csv")
        output_csv = output_dir / f"{sample_id}_spin_observables.csv"
        print(f"Building observables for {sample_id} ...", flush=True)
        summary = process_file(input_csv, output_csv, args.overwrite)
        summaries.append(summary)
        print(
            f"  {summary['status']}: output={summary['output_events'] or '-'} "
            f"nonfinite={summary['nonfinite_events'] or '-'}"
        )

    write_summary(summary_csv, summaries)
    failures = sum(row["status"] == "FAIL" for row in summaries)
    print(f"Wrote {summary_csv}")
    print(f"Processed {len(summaries)} sample(s); failures={failures}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
