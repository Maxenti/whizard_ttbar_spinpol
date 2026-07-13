#!/usr/bin/env python3
"""Parse WHIZARD ttbar LHE samples into validated event-level CSV tables.

The parser is tailored to the repository's forced mixed-flavour dilepton mode

    t    -> b    e+  nu_e
    tbar -> bbar mu- anti-nu_mu

while keeping the implementation explicit and auditable.  It reads successful
samples from metadata/sample_manifest.csv, validates the expected LHE record,
checks top-decay four-momentum closure, extracts forced-decay normalization
information from WHIZARD logs, and writes one event table per sample.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, TextIO

FLOAT_RE = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"

REQUIRED_FINAL_PDGS = {
    "b": 5,
    "bbar": -5,
    "lplus": -11,
    "nue": 12,
    "lminus": 13,
    "numubar": -14,
}

VECTOR_NAMES = (
    "beam1",
    "beam2",
    "top",
    "tbar",
    "b",
    "bbar",
    "lplus",
    "lminus",
    "nue",
    "numubar",
)

BASE_FIELDS = [
    "sample_id",
    "initial_state",
    "polarization",
    "spin_mode",
    "sqrt_s_GeV",
    "event_index",
    "idprup",
    "xwgtup",
    "scalup_GeV",
    "aqedup",
    "aqcdup",
    "production_cross_section_fb",
    "exclusive_cross_section_fb",
    "production_event_weight_fb",
    "exclusive_event_weight_fb",
]

VECTOR_FIELDS = [
    f"{name}_{component}"
    for name in VECTOR_NAMES
    for component in ("pdg", "status", "mother1", "mother2", "px", "py", "pz", "E", "m")
]

QUALITY_FIELDS = [
    "top_decay_residual_E_GeV",
    "top_decay_residual_p_GeV",
    "tbar_decay_residual_E_GeV",
    "tbar_decay_residual_p_GeV",
    "event_valid",
    "validation_message",
]

OUTPUT_FIELDS = BASE_FIELDS + VECTOR_FIELDS + QUALITY_FIELDS

SUMMARY_FIELDS = [
    "sample_id",
    "initial_state",
    "polarization",
    "spin_mode",
    "lhe_path",
    "log_path",
    "requested_events",
    "manifest_generated_events",
    "parsed_events",
    "valid_events",
    "invalid_events",
    "lhe_header_cross_section_pb",
    "production_cross_section_fb",
    "lhe_manifest_relative_difference",
    "top_partial_width_GeV",
    "antitop_partial_width_GeV",
    "top_total_width_GeV",
    "antitop_total_width_GeV",
    "top_decay_br",
    "antitop_decay_br",
    "forced_decay_weight",
    "exclusive_cross_section_fb",
    "max_top_decay_residual_E_GeV",
    "max_top_decay_residual_p_GeV",
    "max_tbar_decay_residual_E_GeV",
    "max_tbar_decay_residual_p_GeV",
    "output_csv",
    "status",
    "notes",
]


@dataclass(frozen=True)
class Particle:
    pdg: int
    status: int
    mother1: int
    mother2: int
    color1: int
    color2: int
    px: float
    py: float
    pz: float
    energy: float
    mass: float
    lifetime: float
    spin: float

    def four(self) -> tuple[float, float, float, float]:
        return self.energy, self.px, self.py, self.pz


@dataclass(frozen=True)
class Event:
    nup: int
    idprup: int
    xwgtup: float
    scalup: float
    aqedup: float
    aqcdup: float
    particles: tuple[Particle, ...]


@dataclass(frozen=True)
class LHEHeader:
    beam1_pdg: int | None = None
    beam2_pdg: int | None = None
    beam1_energy_GeV: float | None = None
    beam2_energy_GeV: float | None = None
    cross_section_pb: float | None = None
    cross_section_error_pb: float | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--summary-csv", type=Path, default=None)
    parser.add_argument(
        "--sample",
        action="append",
        default=[],
        help="Sample ID or shell-style glob. Repeatable; default is every successful manifest sample.",
    )
    parser.add_argument("--max-events", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--max-decay-closure-GeV",
        type=float,
        default=1.0e-5,
        help="Maximum absolute energy or momentum closure residual for a valid decay.",
    )
    return parser.parse_args()


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace("D", "E").replace("d", "e"))
    except (ValueError, AttributeError):
        return None


def to_int(value: str | None) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def resolve_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def open_text(path: Path) -> TextIO:
    return gzip.open(path, "rt", errors="replace") if path.name.endswith(".gz") else path.open("rt", errors="replace")


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest does not exist: {path}")
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def sample_selected(sample_id: str, patterns: list[str]) -> bool:
    if not patterns:
        return True
    from fnmatch import fnmatch

    return any(fnmatch(sample_id, pattern) for pattern in patterns)


def parse_particle(line: str) -> Particle:
    fields = line.split()
    if len(fields) < 13:
        raise ValueError(f"Expected at least 13 particle columns, got {len(fields)}: {line}")
    return Particle(
        pdg=int(fields[0]),
        status=int(fields[1]),
        mother1=int(fields[2]),
        mother2=int(fields[3]),
        color1=int(fields[4]),
        color2=int(fields[5]),
        px=float(fields[6].replace("D", "E")),
        py=float(fields[7].replace("D", "E")),
        pz=float(fields[8].replace("D", "E")),
        energy=float(fields[9].replace("D", "E")),
        mass=float(fields[10].replace("D", "E")),
        lifetime=float(fields[11].replace("D", "E")),
        spin=float(fields[12].replace("D", "E")),
    )


def parse_event_block(lines: list[str]) -> Event:
    clean = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not clean:
        raise ValueError("Empty <event> block")
    header = clean[0].split()
    if len(header) < 6:
        raise ValueError(f"Malformed event header: {clean[0]}")
    nup = int(header[0])
    particle_lines = [line for line in clean[1:] if not line.startswith("<")]
    if len(particle_lines) < nup:
        raise ValueError(f"Event declares NUP={nup} but only {len(particle_lines)} particle rows were found")
    particles = tuple(parse_particle(line) for line in particle_lines[:nup])
    return Event(
        nup=nup,
        idprup=int(header[1]),
        xwgtup=float(header[2].replace("D", "E")),
        scalup=float(header[3].replace("D", "E")),
        aqedup=float(header[4].replace("D", "E")),
        aqcdup=float(header[5].replace("D", "E")),
        particles=particles,
    )


def iter_lhe_events(path: Path, max_events: int | None = None) -> Iterator[Event]:
    inside = False
    block: list[str] = []
    produced = 0
    with open_text(path) as stream:
        for raw in stream:
            stripped = raw.strip()
            if stripped == "<event>":
                inside = True
                block = []
                continue
            if stripped == "</event>":
                if not inside:
                    continue
                yield parse_event_block(block)
                produced += 1
                inside = False
                block = []
                if max_events is not None and produced >= max_events:
                    return
                continue
            if inside:
                block.append(raw)


def parse_lhe_header(path: Path) -> LHEHeader:
    in_init = False
    init_lines: list[str] = []
    with open_text(path) as stream:
        for raw in stream:
            line = raw.strip()
            if line == "<init>":
                in_init = True
                continue
            if line == "</init>":
                break
            if in_init and line and not line.startswith("<") and not line.startswith("#"):
                init_lines.append(line)
    if len(init_lines) < 2:
        return LHEHeader()
    beam = init_lines[0].split()
    process = init_lines[1].split()
    if len(beam) < 4 or len(process) < 2:
        return LHEHeader()
    return LHEHeader(
        beam1_pdg=int(beam[0]),
        beam2_pdg=int(beam[1]),
        beam1_energy_GeV=float(beam[2].replace("D", "E")),
        beam2_energy_GeV=float(beam[3].replace("D", "E")),
        cross_section_pb=float(process[0].replace("D", "E")),
        cross_section_error_pb=float(process[1].replace("D", "E")),
    )


def parse_decay_widths(path: Path | None) -> dict[str, float | None]:
    result = {
        "top_partial_width_GeV": None,
        "antitop_partial_width_GeV": None,
        "top_total_width_GeV": None,
        "antitop_total_width_GeV": None,
    }
    if path is None or not path.exists():
        return result

    current: str | None = None
    computed_re = re.compile(rf"Total width\s*=\s*({FLOAT_RE})\s*GeV\s*\(computed\)", re.I)
    preset_re = re.compile(rf"=\s*({FLOAT_RE})\s*GeV\s*\(preset\)", re.I)

    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if "Unstable particle tbar:" in line:
            current = "antitop"
            continue
        if "Unstable particle t:" in line:
            current = "top"
            continue
        if current is None:
            continue
        match = computed_re.search(line)
        if match:
            result[f"{current}_partial_width_GeV"] = float(match.group(1).replace("D", "E"))
            continue
        match = preset_re.search(line)
        if match:
            result[f"{current}_total_width_GeV"] = float(match.group(1).replace("D", "E"))
            current = None
    return result


def particle_by_pdg(event: Event, pdg: int, status: int | None = None) -> tuple[int, Particle] | None:
    for index, particle in enumerate(event.particles, start=1):
        if particle.pdg == pdg and (status is None or particle.status == status):
            return index, particle
    return None


def child_of(event: Event, pdg: int, parent_index: int) -> tuple[int, Particle] | None:
    candidates: list[tuple[int, Particle]] = []
    for index, particle in enumerate(event.particles, start=1):
        if particle.pdg != pdg or particle.status != 1:
            continue
        if particle.mother1 == parent_index or particle.mother2 == parent_index:
            return index, particle
        candidates.append((index, particle))
    return candidates[0] if len(candidates) == 1 else None


def magnitude(x: float, y: float, z: float) -> float:
    return math.sqrt(x * x + y * y + z * z)


def decay_residual(parent: Particle, children: Iterable[Particle]) -> tuple[float, float]:
    children = tuple(children)
    d_e = parent.energy - sum(child.energy for child in children)
    d_px = parent.px - sum(child.px for child in children)
    d_py = parent.py - sum(child.py for child in children)
    d_pz = parent.pz - sum(child.pz for child in children)
    return abs(d_e), magnitude(d_px, d_py, d_pz)


def particle_columns(name: str, particle: Particle) -> dict[str, str]:
    return {
        f"{name}_pdg": str(particle.pdg),
        f"{name}_status": str(particle.status),
        f"{name}_mother1": str(particle.mother1),
        f"{name}_mother2": str(particle.mother2),
        f"{name}_px": f"{particle.px:.17g}",
        f"{name}_py": f"{particle.py:.17g}",
        f"{name}_pz": f"{particle.pz:.17g}",
        f"{name}_E": f"{particle.energy:.17g}",
        f"{name}_m": f"{particle.mass:.17g}",
    }


def identify_event(event: Event) -> tuple[dict[str, Particle] | None, str]:
    beams = [(idx, p) for idx, p in enumerate(event.particles, start=1) if p.status == -1]
    if len(beams) < 2:
        return None, f"expected at least two incoming status=-1 particles, found {len(beams)}"

    top_entry = particle_by_pdg(event, 6, 2)
    tbar_entry = particle_by_pdg(event, -6, 2)
    if top_entry is None or tbar_entry is None:
        return None, "missing status=2 top or antitop"
    top_index, top = top_entry
    tbar_index, tbar = tbar_entry

    selected: dict[str, Particle] = {
        "beam1": beams[0][1],
        "beam2": beams[1][1],
        "top": top,
        "tbar": tbar,
    }
    for name, pdg in REQUIRED_FINAL_PDGS.items():
        parent_index = top_index if name in {"b", "lplus", "nue"} else tbar_index
        entry = child_of(event, pdg, parent_index)
        if entry is None:
            return None, f"missing unique final-state {name} (PDG {pdg}) from expected parent"
        selected[name] = entry[1]
    return selected, ""


def fmt(value: float | int | None) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return f"{value:.17g}"


def process_sample(
    row: dict[str, str],
    root: Path,
    output_dir: Path,
    max_events: int | None,
    overwrite: bool,
    closure_limit: float,
) -> dict[str, str]:
    sample_id = row.get("sample_id", "")
    lhe = resolve_path(root, row.get("lhe_path"))
    log = resolve_path(root, row.get("log_path"))
    output = output_dir / f"{sample_id}_events.csv"

    summary = {field: "" for field in SUMMARY_FIELDS}
    summary.update({
        "sample_id": sample_id,
        "initial_state": row.get("initial_state", ""),
        "polarization": row.get("polarization", ""),
        "spin_mode": row.get("spin_mode", ""),
        "lhe_path": str(lhe) if lhe else "",
        "log_path": str(log) if log else "",
        "requested_events": row.get("requested_events", ""),
        "manifest_generated_events": row.get("generated_events", ""),
        "output_csv": str(output),
    })

    if lhe is None or not lhe.exists():
        summary["status"] = "FAIL"
        summary["notes"] = "LHE file not found"
        return summary
    if output.exists() and not overwrite:
        summary["status"] = "SKIP"
        summary["notes"] = "output exists; use --overwrite to regenerate"
        return summary

    header = parse_lhe_header(lhe)
    widths = parse_decay_widths(log)
    production_xsec = to_float(row.get("cross_section_fb"))
    generated_manifest = to_int(row.get("generated_events"))
    top_partial = widths["top_partial_width_GeV"]
    antitop_partial = widths["antitop_partial_width_GeV"]
    top_total = widths["top_total_width_GeV"]
    antitop_total = widths["antitop_total_width_GeV"]
    top_br = top_partial / top_total if top_partial is not None and top_total not in (None, 0.0) else None
    antitop_br = antitop_partial / antitop_total if antitop_partial is not None and antitop_total not in (None, 0.0) else None
    forced_weight = top_br * antitop_br if top_br is not None and antitop_br is not None else None
    exclusive_xsec = production_xsec * forced_weight if production_xsec is not None and forced_weight is not None else None

    parsed = valid = invalid = 0
    max_residuals = [0.0, 0.0, 0.0, 0.0]
    output.parent.mkdir(parents=True, exist_ok=True)

    # Use the manifest count for event-weight normalization unless a max-event
    # debug truncation is requested.  This keeps the stored per-event weight
    # tied to the full generated sample rather than the parser subset.
    denominator = generated_manifest if generated_manifest and generated_manifest > 0 else None
    production_event_weight = production_xsec / denominator if production_xsec is not None and denominator else None
    exclusive_event_weight = exclusive_xsec / denominator if exclusive_xsec is not None and denominator else None

    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for event_index, event in enumerate(iter_lhe_events(lhe, max_events=max_events), start=1):
            parsed += 1
            selected, message = identify_event(event)
            out = {field: "" for field in OUTPUT_FIELDS}
            out.update({
                "sample_id": sample_id,
                "initial_state": row.get("initial_state", ""),
                "polarization": row.get("polarization", ""),
                "spin_mode": row.get("spin_mode", ""),
                "sqrt_s_GeV": row.get("sqrt_s_GeV", ""),
                "event_index": str(event_index),
                "idprup": str(event.idprup),
                "xwgtup": fmt(event.xwgtup),
                "scalup_GeV": fmt(event.scalup),
                "aqedup": fmt(event.aqedup),
                "aqcdup": fmt(event.aqcdup),
                "production_cross_section_fb": fmt(production_xsec),
                "exclusive_cross_section_fb": fmt(exclusive_xsec),
                "production_event_weight_fb": fmt(production_event_weight),
                "exclusive_event_weight_fb": fmt(exclusive_event_weight),
            })

            event_valid = selected is not None
            if selected is not None:
                for name, particle in selected.items():
                    out.update(particle_columns(name, particle))
                top_e, top_p = decay_residual(selected["top"], (selected["b"], selected["lplus"], selected["nue"]))
                tbar_e, tbar_p = decay_residual(selected["tbar"], (selected["bbar"], selected["lminus"], selected["numubar"]))
                residuals = (top_e, top_p, tbar_e, tbar_p)
                max_residuals = [max(old, new) for old, new in zip(max_residuals, residuals)]
                out.update({
                    "top_decay_residual_E_GeV": fmt(top_e),
                    "top_decay_residual_p_GeV": fmt(top_p),
                    "tbar_decay_residual_E_GeV": fmt(tbar_e),
                    "tbar_decay_residual_p_GeV": fmt(tbar_p),
                })
                if max(residuals) > closure_limit:
                    event_valid = False
                    message = f"decay closure residual exceeds {closure_limit:.6g} GeV"

            out["event_valid"] = "1" if event_valid else "0"
            out["validation_message"] = message
            writer.writerow(out)
            if event_valid:
                valid += 1
            else:
                invalid += 1

    lhe_manifest_rel = None
    if header.cross_section_pb is not None and production_xsec not in (None, 0.0):
        lhe_fb = 1000.0 * header.cross_section_pb
        lhe_manifest_rel = abs(lhe_fb - production_xsec) / abs(production_xsec)

    notes: list[str] = []
    expected = min(generated_manifest, max_events) if generated_manifest is not None and max_events is not None else generated_manifest
    status = "PASS"
    if expected is not None and parsed != expected:
        status = "FAIL"
        notes.append(f"parsed {parsed} events; expected {expected}")
    if invalid:
        status = "FAIL"
        notes.append(f"{invalid} invalid events")
    if lhe_manifest_rel is not None and lhe_manifest_rel > 1.0e-6:
        status = "FAIL"
        notes.append(f"LHE/manifest cross-section relative difference={lhe_manifest_rel:.6g}")
    if forced_weight is None:
        notes.append("forced-decay normalization unavailable from log")

    summary.update({
        "parsed_events": str(parsed),
        "valid_events": str(valid),
        "invalid_events": str(invalid),
        "lhe_header_cross_section_pb": fmt(header.cross_section_pb),
        "production_cross_section_fb": fmt(production_xsec),
        "lhe_manifest_relative_difference": fmt(lhe_manifest_rel),
        "top_partial_width_GeV": fmt(top_partial),
        "antitop_partial_width_GeV": fmt(antitop_partial),
        "top_total_width_GeV": fmt(top_total),
        "antitop_total_width_GeV": fmt(antitop_total),
        "top_decay_br": fmt(top_br),
        "antitop_decay_br": fmt(antitop_br),
        "forced_decay_weight": fmt(forced_weight),
        "exclusive_cross_section_fb": fmt(exclusive_xsec),
        "max_top_decay_residual_E_GeV": fmt(max_residuals[0]),
        "max_top_decay_residual_p_GeV": fmt(max_residuals[1]),
        "max_tbar_decay_residual_E_GeV": fmt(max_residuals[2]),
        "max_tbar_decay_residual_p_GeV": fmt(max_residuals[3]),
        "status": status,
        "notes": "; ".join(notes),
    })
    return summary


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    manifest = (args.manifest or root / "metadata" / "sample_manifest.csv").resolve()
    output_dir = (args.output_dir or root / "validation" / "angular_tables" / "events").resolve()
    summary_csv = (args.summary_csv or root / "validation" / "angular_summaries" / "lhe_parse_summary.csv").resolve()

    rows = load_manifest(manifest)
    selected = [
        row
        for row in rows
        if row.get("status") == "success" and sample_selected(row.get("sample_id", ""), args.sample)
    ]
    if not selected:
        print("ERROR: no successful manifest samples matched the requested selection", file=sys.stderr)
        return 2

    summaries: list[dict[str, str]] = []
    for row in selected:
        sample_id = row.get("sample_id", "")
        print(f"Parsing {sample_id} ...", flush=True)
        summary = process_sample(
            row,
            root,
            output_dir,
            args.max_events,
            args.overwrite,
            args.max_decay_closure_GeV,
        )
        summaries.append(summary)
        print(
            f"  {summary['status']}: parsed={summary['parsed_events'] or '-'} "
            f"valid={summary['valid_events'] or '-'} output={summary['output_csv']}"
        )

    write_summary(summary_csv, summaries)
    failures = sum(row["status"] == "FAIL" for row in summaries)
    print(f"Wrote {summary_csv}")
    print(f"Processed {len(summaries)} sample(s); failures={failures}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
