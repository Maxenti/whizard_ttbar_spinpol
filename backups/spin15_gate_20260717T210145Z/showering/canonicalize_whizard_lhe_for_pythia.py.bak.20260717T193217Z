#!/usr/bin/env python3
"""Canonicalize WHIZARD LHE records for PYTHIA8.

WHIZARD may write an extended ISR history containing:

  beam lepton       ISTUP = -9
  post-ISR lepton   ISTUP = -1, mother = beam
  hard system       mothers = post-ISR leptons
  ISR photons       mothers = beam leptons

PYTHIA's LHE hard-system setup expects the canonical LHA representation with
exactly two incoming particles.  This tool:

1. keeps the nominal beam particles and promotes ISTUP -9 -> -1;
2. removes the two post-ISR bridge leptons;
3. rewires all mother indices from the bridge leptons to the beam leptons;
4. preserves all surviving four-vectors, colours, spins, event weights, and
   resonance-decay products exactly;
5. optionally removes WHIZARD's auxiliary ``sqme_prc`` weight elements;
6. validates index ranges and event-level four-momentum closure.

The authoritative input file is never modified.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TextIO


SQME_OPEN_RE = re.compile(
    r"<weight\b[^>]*\bname\s*=\s*([\"'])sqme_prc\1[^>]*>",
    re.IGNORECASE,
)


class CanonicalizationError(RuntimeError):
    """Raised when an event does not satisfy the required transformation contract."""


@dataclass
class Particle:
    tokens: list[str]
    original_index: int

    @property
    def pid(self) -> int:
        return int(self.tokens[0])

    @property
    def status(self) -> int:
        return int(self.tokens[1])

    @status.setter
    def status(self, value: int) -> None:
        self.tokens[1] = str(value)

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

    def render(self) -> str:
        return " " + " ".join(self.tokens)


@dataclass
class EventResult:
    lines: list[str]
    canonicalized: bool
    removed_bridges: int
    promoted_beams: int
    max_abs_closure_gev: float
    max_rel_closure: float


@dataclass
class Summary:
    input_path: str
    output_path: str
    total_events: int = 0
    canonicalized_events: int = 0
    already_canonical_events: int = 0
    removed_bridge_particles: int = 0
    promoted_beam_particles: int = 0
    removed_sqme_prc_tags: int = 0
    max_abs_closure_gev: float = 0.0
    max_rel_closure: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            **self.__dict__,
        }


def parse_particle(line: str, index: int) -> Particle:
    tokens = line.split()
    if len(tokens) < 13:
        raise CanonicalizationError(
            f"particle {index}: expected at least 13 LHE columns, found {len(tokens)}"
        )
    try:
        int(tokens[0])
        int(tokens[1])
        int(tokens[2])
        int(tokens[3])
        int(tokens[4])
        int(tokens[5])
        for field in tokens[6:13]:
            float(field)
    except ValueError as exc:
        raise CanonicalizationError(
            f"particle {index}: malformed numeric field in {line!r}"
        ) from exc
    return Particle(tokens=tokens, original_index=index)


def remap_mother(
    old_index: int,
    *,
    old_to_new: dict[int, int],
    bridge_to_beam: dict[int, int],
) -> int:
    if old_index == 0:
        return 0
    resolved = bridge_to_beam.get(old_index, old_index)
    try:
        return old_to_new[resolved]
    except KeyError as exc:
        raise CanonicalizationError(
            f"mother index {old_index} resolves to removed/unmapped particle {resolved}"
        ) from exc


def closure_metrics(particles: list[Particle]) -> tuple[float, float]:
    incoming = [0.0, 0.0, 0.0, 0.0]
    outgoing = [0.0, 0.0, 0.0, 0.0]

    for particle in particles:
        target = incoming if particle.status == -1 else outgoing if particle.status == 1 else None
        if target is None:
            continue
        for i, component in enumerate(particle.p4):
            target[i] += component

    delta = [incoming[i] - outgoing[i] for i in range(4)]
    max_abs = max(abs(value) for value in delta)
    scale = max(
        1.0,
        max(abs(value) for value in incoming),
        max(abs(value) for value in outgoing),
    )
    return max_abs, max_abs / scale


def validate_canonical_particles(
    particles: list[Particle],
    *,
    event_number: int,
    closure_rel_tolerance: float,
    closure_abs_tolerance_gev: float,
) -> tuple[float, float]:
    if len(particles) < 4:
        raise CanonicalizationError(
            f"event {event_number}: canonical event contains only {len(particles)} particles"
        )

    incoming = [p for p in particles if p.status == -1]
    if len(incoming) != 2:
        raise CanonicalizationError(
            f"event {event_number}: expected exactly two ISTUP=-1 particles, found {len(incoming)}"
        )
    if any(p.status == -9 for p in particles):
        raise CanonicalizationError(
            f"event {event_number}: ISTUP=-9 remains after canonicalization"
        )

    size = len(particles)
    for new_index, particle in enumerate(particles, start=1):
        for label, mother in (("mother1", particle.mother1), ("mother2", particle.mother2)):
            if mother < 0 or mother > size:
                raise CanonicalizationError(
                    f"event {event_number}: particle {new_index} {label}={mother} "
                    f"outside [0,{size}]"
                )
            if mother == new_index:
                raise CanonicalizationError(
                    f"event {event_number}: particle {new_index} is its own mother"
                )

    max_abs, max_rel = closure_metrics(particles)
    if max_abs > closure_abs_tolerance_gev and max_rel > closure_rel_tolerance:
        raise CanonicalizationError(
            f"event {event_number}: four-momentum closure failed: "
            f"max_abs={max_abs:.6e} GeV max_rel={max_rel:.6e}"
        )
    return max_abs, max_rel


def canonicalize_event(
    event_lines: list[str],
    *,
    event_number: int,
    closure_rel_tolerance: float,
    closure_abs_tolerance_gev: float,
) -> EventResult:
    if not event_lines or event_lines[0].strip() != "<event>":
        raise CanonicalizationError(f"event {event_number}: missing <event> opener")
    if event_lines[-1].strip() != "</event>":
        raise CanonicalizationError(f"event {event_number}: missing </event> closer")

    cursor = 1
    while cursor < len(event_lines) - 1 and not event_lines[cursor].strip():
        cursor += 1
    if cursor >= len(event_lines) - 1:
        raise CanonicalizationError(f"event {event_number}: missing event header")

    header_tokens = event_lines[cursor].split()
    if len(header_tokens) < 6:
        raise CanonicalizationError(
            f"event {event_number}: malformed event header {event_lines[cursor]!r}"
        )
    try:
        nup = int(header_tokens[0])
    except ValueError as exc:
        raise CanonicalizationError(
            f"event {event_number}: invalid NUP value {header_tokens[0]!r}"
        ) from exc

    particle_start = cursor + 1
    particle_end = particle_start + nup
    if particle_end > len(event_lines) - 1:
        raise CanonicalizationError(
            f"event {event_number}: NUP={nup} exceeds available particle lines"
        )

    particles = [
        parse_particle(event_lines[particle_start + offset], offset + 1)
        for offset in range(nup)
    ]
    trailing = event_lines[particle_end:-1]

    beams = [p for p in particles if p.status == -9]
    bridges = [p for p in particles if p.status == -1]

    if not beams and len(bridges) == 2:
        max_abs, max_rel = validate_canonical_particles(
            particles,
            event_number=event_number,
            closure_rel_tolerance=closure_rel_tolerance,
            closure_abs_tolerance_gev=closure_abs_tolerance_gev,
        )
        return EventResult(
            lines=event_lines,
            canonicalized=False,
            removed_bridges=0,
            promoted_beams=0,
            max_abs_closure_gev=max_abs,
            max_rel_closure=max_rel,
        )

    if len(beams) != 2 or len(bridges) != 2:
        raise CanonicalizationError(
            f"event {event_number}: unsupported incoming layout: "
            f"ISTUP=-9 count={len(beams)}, ISTUP=-1 count={len(bridges)}"
        )

    beam_indices = {p.original_index for p in beams}
    bridge_to_beam: dict[int, int] = {}

    for bridge in bridges:
        if bridge.mother1 not in beam_indices or bridge.mother2 != 0:
            raise CanonicalizationError(
                f"event {event_number}: bridge particle {bridge.original_index} "
                f"has mothers ({bridge.mother1},{bridge.mother2}), expected one beam mother"
            )
        beam = next(p for p in beams if p.original_index == bridge.mother1)
        if beam.pid != bridge.pid:
            raise CanonicalizationError(
                f"event {event_number}: beam/bridge PID mismatch: "
                f"beam {beam.original_index} pid={beam.pid}, "
                f"bridge {bridge.original_index} pid={bridge.pid}"
            )
        bridge_to_beam[bridge.original_index] = beam.original_index

    if len(set(bridge_to_beam.values())) != 2:
        raise CanonicalizationError(
            f"event {event_number}: bridge particles do not map one-to-one onto beams"
        )

    remove_indices = set(bridge_to_beam)
    survivors = [p for p in particles if p.original_index not in remove_indices]
    old_to_new = {
        particle.original_index: new_index
        for new_index, particle in enumerate(survivors, start=1)
    }

    for particle in survivors:
        if particle.original_index in beam_indices:
            particle.status = -1
            particle.mother1 = 0
            particle.mother2 = 0
        else:
            particle.mother1 = remap_mother(
                particle.mother1,
                old_to_new=old_to_new,
                bridge_to_beam=bridge_to_beam,
            )
            particle.mother2 = remap_mother(
                particle.mother2,
                old_to_new=old_to_new,
                bridge_to_beam=bridge_to_beam,
            )

    max_abs, max_rel = validate_canonical_particles(
        survivors,
        event_number=event_number,
        closure_rel_tolerance=closure_rel_tolerance,
        closure_abs_tolerance_gev=closure_abs_tolerance_gev,
    )

    header_tokens[0] = str(len(survivors))
    rendered = [
        "<event>",
        " " + " ".join(header_tokens),
        *(particle.render() for particle in survivors),
        *trailing,
        "</event>",
    ]
    return EventResult(
        lines=rendered,
        canonicalized=True,
        removed_bridges=len(remove_indices),
        promoted_beams=len(beams),
        max_abs_closure_gev=max_abs,
        max_rel_closure=max_rel,
    )


def strip_sqme_prc(lines: list[str]) -> tuple[list[str], int]:
    output: list[str] = []
    removed = 0
    skipping = False

    for line in lines:
        if not skipping and SQME_OPEN_RE.search(line):
            removed += 1
            if "</weight>" not in line:
                skipping = True
            continue
        if skipping:
            if "</weight>" in line:
                skipping = False
            continue
        output.append(line)

    if skipping:
        raise CanonicalizationError("unterminated sqme_prc <weight> element")
    return output, removed


def write_atomic(path: Path, text_lines: Iterable[str]) -> None:
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
            for line in text_lines:
                stream.write(line)
                stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def canonicalize_file(
    input_path: Path,
    output_path: Path,
    *,
    summary_path: Path | None,
    remove_sqme_prc: bool,
    closure_rel_tolerance: float,
    closure_abs_tolerance_gev: float,
) -> Summary:
    if input_path.resolve() == output_path.resolve():
        raise CanonicalizationError("input and output paths must differ")

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
            result = canonicalize_event(
                event_lines,
                event_number=summary.total_events,
                closure_rel_tolerance=closure_rel_tolerance,
                closure_abs_tolerance_gev=closure_abs_tolerance_gev,
            )
            transformed = result.lines
            if remove_sqme_prc:
                transformed, removed = strip_sqme_prc(transformed)
                summary.removed_sqme_prc_tags += removed

            output_lines.extend(transformed)
            summary.max_abs_closure_gev = max(
                summary.max_abs_closure_gev,
                result.max_abs_closure_gev,
            )
            summary.max_rel_closure = max(
                summary.max_rel_closure,
                result.max_rel_closure,
            )
            if result.canonicalized:
                summary.canonicalized_events += 1
                summary.removed_bridge_particles += result.removed_bridges
                summary.promoted_beam_particles += result.promoted_beams
            else:
                summary.already_canonical_events += 1

            event_lines = []
            in_event = False

    if in_event:
        raise CanonicalizationError("input ended inside an <event> block")
    if summary.total_events == 0:
        raise CanonicalizationError("input contains no <event> blocks")

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
        description="Canonicalize WHIZARD LHE ISR history for PYTHIA8."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument(
        "--keep-sqme-prc",
        action="store_true",
        help="Retain WHIZARD sqme_prc auxiliary weight tags.",
    )
    parser.add_argument(
        "--closure-rel-tolerance",
        type=float,
        default=1.0e-7,
    )
    parser.add_argument(
        "--closure-abs-tolerance-gev",
        type=float,
        default=1.0e-6,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = canonicalize_file(
            args.input,
            args.output,
            summary_path=args.summary,
            remove_sqme_prc=not args.keep_sqme_prc,
            closure_rel_tolerance=args.closure_rel_tolerance,
            closure_abs_tolerance_gev=args.closure_abs_tolerance_gev,
        )
    except (OSError, CanonicalizationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        "CANONICALIZATION SUCCESS "
        f"events={summary.total_events} "
        f"canonicalized={summary.canonicalized_events} "
        f"already_canonical={summary.already_canonical_events} "
        f"removed_bridges={summary.removed_bridge_particles} "
        f"promoted_beams={summary.promoted_beam_particles} "
        f"removed_sqme_prc={summary.removed_sqme_prc_tags} "
        f"max_abs_closure_GeV={summary.max_abs_closure_gev:.6e} "
        f"output={summary.output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
