#!/usr/bin/env python3
"""Insert explicit W resonances into canonical WHIZARD ttbar LHE records.

Input contract
--------------
The input must already satisfy the canonical-v2 PYTHIA contract:

  incoming lepton pair        ISTUP = -1, indices 1 and 2
  t, tbar                     ISTUP = 2, mothers 1 and 2
  explicit ISR photons        ISTUP = 1, mothers 1 and 2
  direct top decay products   ISTUP = 1, mother = t or tbar

For each event this tool rewrites

  t    -> b l+ nu
  tbar -> bbar l- nubar

as

  t    -> b W+
  W+   -> l+ nu

  tbar -> bbar W-
  W-   -> l- nubar

without changing any original particle four-vector, colour tag, weight,
cross section, or event-header field.  The synthetic W four-vector is exactly
the sum of its charged-lepton and neutrino daughters.

The authoritative WHIZARD LHE and the canonical-v2 LHE are never modified.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class TopologyError(RuntimeError):
    """Raised when an event does not match the supported ttbar decay contract."""


@dataclass
class Particle:
    tokens: list[str]
    source_index: int

    @property
    def pid(self) -> int:
        return int(self.tokens[0])

    @property
    def status(self) -> int:
        return int(self.tokens[1])

    @property
    def mother1(self) -> int:
        return int(self.tokens[2])

    @mother1.setter
    def mother1(self, value: int) -> None:
        self.tokens[2] = str(value)

    @property
    def mother2(self) -> int:
        return int(self.tokens[3])

    @mother2.setter
    def mother2(self, value: int) -> None:
        self.tokens[3] = str(value)

    @property
    def p4(self) -> tuple[float, float, float, float]:
        return tuple(float(self.tokens[i]) for i in (6, 7, 8, 9))  # type: ignore[return-value]

    def copy(self) -> "Particle":
        return Particle(self.tokens.copy(), self.source_index)

    def render(self) -> str:
        return " " + " ".join(self.tokens)


@dataclass
class EventResult:
    lines: list[str]
    inserted_w_resonances: int
    max_vertex_abs_closure_gev: float
    max_vertex_rel_closure: float
    min_w_mass_gev: float
    max_w_mass_gev: float


@dataclass
class Summary:
    input_path: str
    output_path: str
    total_events: int = 0
    explicit_w_events: int = 0
    inserted_w_resonances: int = 0
    max_vertex_abs_closure_gev: float = 0.0
    max_vertex_rel_closure: float = 0.0
    min_w_mass_gev: float = math.inf
    max_w_mass_gev: float = 0.0

    def to_dict(self) -> dict[str, object]:
        data = {
            "schema_version": 1,
            "topology_policy": "canonical_v2_plus_explicit_w_v3",
            **self.__dict__,
        }
        if math.isinf(self.min_w_mass_gev):
            data["min_w_mass_gev"] = None
        return data


def parse_particle(line: str, index: int) -> Particle:
    tokens = line.split()
    if len(tokens) < 13:
        raise TopologyError(
            f"particle {index}: expected at least 13 LHE columns, found {len(tokens)}"
        )
    try:
        for position in range(6):
            int(tokens[position])
        for position in range(6, 13):
            float(tokens[position])
    except ValueError as exc:
        raise TopologyError(
            f"particle {index}: malformed LHE particle row {line!r}"
        ) from exc
    return Particle(tokens=tokens, source_index=index)


def add_p4(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    return tuple(first[i] + second[i] for i in range(4))  # type: ignore[return-value]


def subtract_p4(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    return tuple(first[i] - second[i] for i in range(4))  # type: ignore[return-value]


def p4_norm_metrics(
    residual: tuple[float, float, float, float],
    reference: tuple[float, float, float, float],
) -> tuple[float, float]:
    maximum = max(abs(component) for component in residual)
    scale = max(1.0, *(abs(component) for component in reference))
    return maximum, maximum / scale


def invariant_mass(p4: tuple[float, float, float, float]) -> float:
    px, py, pz, energy = p4
    mass2 = energy * energy - px * px - py * py - pz * pz
    tolerance = 1.0e-8 * max(1.0, energy * energy)
    if mass2 < -tolerance:
        raise TopologyError(
            f"synthetic W has negative mass squared: {mass2:.12e} GeV^2"
        )
    return math.sqrt(max(0.0, mass2))


def format_lhe_float(value: float) -> str:
    return f"{value:.16E}"


def make_w_particle(
    *,
    pid: int,
    mother_index: int,
    p4: tuple[float, float, float, float],
    synthetic_index: int,
) -> Particle:
    mass = invariant_mass(p4)
    px, py, pz, energy = p4
    return Particle(
        tokens=[
            str(pid),
            "2",
            str(mother_index),
            "0",
            "0",
            "0",
            format_lhe_float(px),
            format_lhe_float(py),
            format_lhe_float(pz),
            format_lhe_float(energy),
            format_lhe_float(mass),
            "0.0000000000000000E+00",
            "9.0000000000000000E+00",
        ],
        source_index=synthetic_index,
    )


def parent_set(particle: Particle) -> set[int]:
    return {
        mother
        for mother in (particle.mother1, particle.mother2)
        if mother != 0
    }


def validate_contiguous_daughters(
    particles: list[Particle],
    *,
    event_number: int,
) -> None:
    children: dict[int, list[int]] = {
        index: [] for index in range(1, len(particles) + 1)
    }
    for child_index, particle in enumerate(particles, start=1):
        for mother in parent_set(particle):
            if mother < 1 or mother > len(particles):
                raise TopologyError(
                    f"event {event_number}: child {child_index} has invalid mother {mother}"
                )
            children[mother].append(child_index)

    for mother, daughter_indices in children.items():
        if not daughter_indices:
            continue
        unique = sorted(set(daughter_indices))
        expected = list(range(unique[0], unique[-1] + 1))
        if unique != expected:
            raise TopologyError(
                f"event {event_number}: mother {mother} has non-contiguous "
                f"daughters {unique}; implied range would be {expected}"
            )


def classify_top_children(
    particles: list[Particle],
    *,
    top_index: int,
    top_pid: int,
    event_number: int,
) -> tuple[Particle, Particle, Particle]:
    children = [
        particle
        for particle in particles
        if parent_set(particle) == {top_index}
    ]
    if len(children) != 3:
        raise TopologyError(
            f"event {event_number}: top index {top_index} pid={top_pid} "
            f"has {len(children)} direct children, expected 3"
        )

    expected_b_pid = 5 if top_pid == 6 else -5
    expected_charged_sign = -1 if top_pid == 6 else 1
    expected_neutrino_sign = 1 if top_pid == 6 else -1

    b_candidates = [child for child in children if child.pid == expected_b_pid]
    charged_candidates = [
        child
        for child in children
        if abs(child.pid) in (11, 13)
        and (1 if child.pid > 0 else -1) == expected_charged_sign
    ]
    neutrino_candidates = [
        child
        for child in children
        if abs(child.pid) in (12, 14)
        and (1 if child.pid > 0 else -1) == expected_neutrino_sign
    ]

    if not (
        len(b_candidates) == 1
        and len(charged_candidates) == 1
        and len(neutrino_candidates) == 1
    ):
        raise TopologyError(
            f"event {event_number}: unsupported top-decay children for "
            f"top index {top_index}: {[child.pid for child in children]}"
        )

    charged = charged_candidates[0]
    neutrino = neutrino_candidates[0]

    expected_neutrino_abs = abs(charged.pid) + 1
    if abs(neutrino.pid) != expected_neutrino_abs:
        raise TopologyError(
            f"event {event_number}: charged lepton pid={charged.pid} and "
            f"neutrino pid={neutrino.pid} have inconsistent flavour"
        )

    return b_candidates[0], charged, neutrino


def transform_event(
    event_lines: list[str],
    *,
    event_number: int,
    vertex_rel_tolerance: float,
    vertex_abs_tolerance_gev: float,
) -> EventResult:
    if not event_lines or event_lines[0].strip() != "<event>":
        raise TopologyError(f"event {event_number}: missing <event> opener")
    if event_lines[-1].strip() != "</event>":
        raise TopologyError(f"event {event_number}: missing </event> closer")

    cursor = 1
    while cursor < len(event_lines) - 1 and not event_lines[cursor].strip():
        cursor += 1
    if cursor >= len(event_lines) - 1:
        raise TopologyError(f"event {event_number}: missing event header")

    header_tokens = event_lines[cursor].split()
    if len(header_tokens) < 6:
        raise TopologyError(f"event {event_number}: malformed event header")
    try:
        nup = int(header_tokens[0])
    except ValueError as exc:
        raise TopologyError(
            f"event {event_number}: invalid NUP={header_tokens[0]!r}"
        ) from exc

    particle_start = cursor + 1
    particle_end = particle_start + nup
    if particle_end > len(event_lines) - 1:
        raise TopologyError(
            f"event {event_number}: NUP={nup} exceeds particle rows"
        )

    particles = [
        parse_particle(event_lines[particle_start + offset], offset + 1)
        for offset in range(nup)
    ]
    trailing = event_lines[particle_end:-1]

    incoming = [
        (index, particle)
        for index, particle in enumerate(particles, start=1)
        if particle.status == -1
    ]
    if len(incoming) != 2 or [index for index, _ in incoming] != [1, 2]:
        raise TopologyError(
            f"event {event_number}: expected incoming particles at indices 1 and 2"
        )

    top_entries = [
        (index, particle)
        for index, particle in enumerate(particles, start=1)
        if abs(particle.pid) == 6
        and particle.status == 2
        and parent_set(particle) == {1, 2}
    ]
    if len(top_entries) != 2 or {particle.pid for _, particle in top_entries} != {6, -6}:
        raise TopologyError(
            f"event {event_number}: expected one t and one tbar hard resonance"
        )
    top_entries.sort(key=lambda item: 0 if item[1].pid == 6 else 1)

    hard_photons = [
        particle
        for particle in particles
        if particle.pid == 22
        and particle.status == 1
        and parent_set(particle) == {1, 2}
    ]

    classified: dict[int, tuple[Particle, Particle, Particle]] = {}
    accounted_indices = {1, 2}
    accounted_indices.update(index for index, _ in top_entries)

    for top_index, top in top_entries:
        decay = classify_top_children(
            particles,
            top_index=top_index,
            top_pid=top.pid,
            event_number=event_number,
        )
        classified[top_index] = decay
        accounted_indices.update(child.source_index for child in decay)

    accounted_indices.update(photon.source_index for photon in hard_photons)
    all_indices = set(range(1, len(particles) + 1))
    if accounted_indices != all_indices:
        extras = sorted(all_indices - accounted_indices)
        raise TopologyError(
            f"event {event_number}: unsupported extra particles at indices {extras}"
        )

    output: list[Particle] = []

    for _, particle in incoming:
        copied = particle.copy()
        copied.mother1 = 0
        copied.mother2 = 0
        output.append(copied)

    top_new_indices: dict[int, int] = {}
    for old_index, particle in top_entries:
        copied = particle.copy()
        copied.mother1 = 1
        copied.mother2 = 2
        output.append(copied)
        top_new_indices[old_index] = len(output)

    for particle in hard_photons:
        copied = particle.copy()
        copied.mother1 = 1
        copied.mother2 = 2
        output.append(copied)

    max_abs = 0.0
    max_rel = 0.0
    w_masses: list[float] = []
    synthetic_index = -1

    for old_top_index, top in top_entries:
        b, charged, neutrino = classified[old_top_index]
        top_new_index = top_new_indices[old_top_index]

        b_copy = b.copy()
        b_copy.mother1 = top_new_index
        b_copy.mother2 = 0
        output.append(b_copy)

        w_p4 = add_p4(charged.p4, neutrino.p4)
        w_pid = 24 if top.pid == 6 else -24
        w_new_index = len(output) + 1
        w_particle = make_w_particle(
            pid=w_pid,
            mother_index=top_new_index,
            p4=w_p4,
            synthetic_index=synthetic_index,
        )
        synthetic_index -= 1
        output.append(w_particle)
        w_masses.append(invariant_mass(w_p4))

        charged_copy = charged.copy()
        charged_copy.mother1 = w_new_index
        charged_copy.mother2 = 0
        output.append(charged_copy)

        neutrino_copy = neutrino.copy()
        neutrino_copy.mother1 = w_new_index
        neutrino_copy.mother2 = 0
        output.append(neutrino_copy)

        top_decay_sum = add_p4(b.p4, w_p4)
        top_residual = subtract_p4(top.p4, top_decay_sum)
        top_abs, top_rel = p4_norm_metrics(top_residual, top.p4)

        w_decay_sum = add_p4(charged.p4, neutrino.p4)
        w_residual = subtract_p4(w_p4, w_decay_sum)
        w_abs, w_rel = p4_norm_metrics(w_residual, w_p4)

        max_abs = max(max_abs, top_abs, w_abs)
        max_rel = max(max_rel, top_rel, w_rel)

    if max_abs > vertex_abs_tolerance_gev and max_rel > vertex_rel_tolerance:
        raise TopologyError(
            f"event {event_number}: decay-vertex closure failed: "
            f"max_abs={max_abs:.6e} GeV max_rel={max_rel:.6e}"
        )

    validate_contiguous_daughters(output, event_number=event_number)

    header_tokens[0] = str(len(output))
    rendered = [
        "<event>",
        " " + " ".join(header_tokens),
        *(particle.render() for particle in output),
        *trailing,
        "</event>",
    ]

    return EventResult(
        lines=rendered,
        inserted_w_resonances=2,
        max_vertex_abs_closure_gev=max_abs,
        max_vertex_rel_closure=max_rel,
        min_w_mass_gev=min(w_masses),
        max_w_mass_gev=max(w_masses),
    )


def write_atomic(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            for line in lines:
                stream.write(line)
                stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def transform_file(
    input_path: Path,
    output_path: Path,
    *,
    summary_path: Path | None,
    vertex_rel_tolerance: float,
    vertex_abs_tolerance_gev: float,
) -> Summary:
    if input_path.resolve() == output_path.resolve():
        raise TopologyError("input and output paths must differ")

    summary = Summary(
        input_path=str(input_path.resolve()),
        output_path=str(output_path.resolve()),
    )
    output_lines: list[str] = []
    in_event = False
    event_lines: list[str] = []

    with input_path.open("r", encoding="utf-8", errors="strict") as source:
        for raw in source:
            line = raw.rstrip("\r\n")
            if not in_event:
                if line.strip() == "<event>":
                    in_event = True
                    event_lines = [line]
                else:
                    output_lines.append(line)
                continue

            event_lines.append(line)
            if line.strip() != "</event>":
                continue

            summary.total_events += 1
            result = transform_event(
                event_lines,
                event_number=summary.total_events,
                vertex_rel_tolerance=vertex_rel_tolerance,
                vertex_abs_tolerance_gev=vertex_abs_tolerance_gev,
            )
            output_lines.extend(result.lines)
            summary.explicit_w_events += 1
            summary.inserted_w_resonances += result.inserted_w_resonances
            summary.max_vertex_abs_closure_gev = max(
                summary.max_vertex_abs_closure_gev,
                result.max_vertex_abs_closure_gev,
            )
            summary.max_vertex_rel_closure = max(
                summary.max_vertex_rel_closure,
                result.max_vertex_rel_closure,
            )
            summary.min_w_mass_gev = min(
                summary.min_w_mass_gev,
                result.min_w_mass_gev,
            )
            summary.max_w_mass_gev = max(
                summary.max_w_mass_gev,
                result.max_w_mass_gev,
            )

            event_lines = []
            in_event = False

    if in_event:
        raise TopologyError("input ended inside an <event> block")
    if summary.total_events == 0:
        raise TopologyError("input contains no events")

    write_atomic(output_path, output_lines)

    if summary_path is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Insert explicit W resonances into canonical-v2 WHIZARD ttbar LHE."
        )
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument(
        "--vertex-rel-tolerance",
        type=float,
        default=1.0e-7,
    )
    parser.add_argument(
        "--vertex-abs-tolerance-gev",
        type=float,
        default=1.0e-5,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = transform_file(
            args.input,
            args.output,
            summary_path=args.summary,
            vertex_rel_tolerance=args.vertex_rel_tolerance,
            vertex_abs_tolerance_gev=args.vertex_abs_tolerance_gev,
        )
    except (OSError, TopologyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        "EXPLICIT-W TOPOLOGY SUCCESS "
        f"events={summary.total_events} "
        f"inserted_w={summary.inserted_w_resonances} "
        f"max_vertex_abs_closure_GeV="
        f"{summary.max_vertex_abs_closure_gev:.6e} "
        f"max_vertex_rel_closure="
        f"{summary.max_vertex_rel_closure:.6e} "
        f"w_mass_range_GeV="
        f"[{summary.min_w_mass_gev:.6f},{summary.max_w_mass_gev:.6f}] "
        f"output={summary.output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
