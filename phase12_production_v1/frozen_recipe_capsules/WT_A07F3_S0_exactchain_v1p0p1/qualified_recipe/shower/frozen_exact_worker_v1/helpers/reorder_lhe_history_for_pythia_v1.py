#!/usr/bin/env python3

"""
History-preserving LHE particle-row serializer for PYTHIA.

Purpose
-------
WHIZARD resonance_history output can represent a physically valid resonance
graph using particle-row ordering in which a parent's direct children are not
contiguous.

LHA/PYTHIA genealogy requires each parent's direct daughters to be
representable as a contiguous first/last daughter interval.

This tool changes ONLY:

    1. particle-row ordering;
    2. mother indices MOTHUP(1:2), remapped to the new row numbers.

It does NOT:

    - add particles;
    - remove particles;
    - alter IDUP;
    - alter ISTUP;
    - alter ICOLUP;
    - alter PUP;
    - alter VTIMUP;
    - alter SPINUP;
    - alter event weights;
    - alter the selected resonance graph.

The output is rejected unless all direct-daughter sets are contiguous and
every mother precedes every child after serialization.
"""

from __future__ import annotations

import argparse
import collections
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Particle:
    old_index: int
    tokens: list[str]

    @property
    def pid(self) -> int:
        return int(self.tokens[0])

    @property
    def status(self) -> int:
        return int(self.tokens[1])

    @property
    def m1(self) -> int:
        return int(self.tokens[2])

    @property
    def m2(self) -> int:
        return int(self.tokens[3])

    @property
    def mothers(self) -> tuple[int, ...]:
        values = {
            self.m1,
            self.m2,
        }

        values.discard(0)

        return tuple(sorted(values))


@dataclass
class EventBlock:
    opening: str
    prefix_lines: list[str]
    header_line: str
    particles: list[Particle]
    suffix_lines: list[str]
    closing: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reorder an LHE resonance history into a strict "
            "PYTHIA-compatible daughter-range serialization."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--summary",
        required=True,
        type=Path,
    )

    return parser.parse_args()


def is_data_line(line: str) -> bool:
    s = line.strip()

    return bool(
        s
        and not s.startswith("#")
        and not s.startswith("<")
    )


def read_event(
    lines: list[str],
    start: int,
) -> tuple[EventBlock, int]:

    if lines[start].strip() != "<event>":
        raise ValueError(
            f"internal parser error at line {start + 1}"
        )

    opening = lines[start]

    i = start + 1

    prefix_lines: list[str] = []

    while i < len(lines) and not is_data_line(lines[i]):
        if lines[i].strip() == "</event>":
            raise ValueError(
                "event closed before its event header"
            )

        prefix_lines.append(lines[i])
        i += 1

    if i >= len(lines):
        raise ValueError(
            "unterminated event"
        )

    header_line = lines[i]

    header_tokens = header_line.split()

    if not header_tokens:
        raise ValueError(
            "empty event header"
        )

    nup = int(header_tokens[0])

    i += 1

    particles: list[Particle] = []
    interstitial: list[str] = []

    while i < len(lines) and len(particles) < nup:
        s = lines[i].strip()

        if s == "</event>":
            raise ValueError(
                f"event declares NUP={nup} but contains "
                f"only {len(particles)} particle rows"
            )

        if not is_data_line(lines[i]):
            interstitial.append(lines[i])
            i += 1
            continue

        tokens = lines[i].split()

        if len(tokens) < 13:
            raise ValueError(
                "particle row has fewer than 13 LHE columns: "
                f"{lines[i].rstrip()}"
            )

        particles.append(
            Particle(
                old_index=len(particles) + 1,
                tokens=tokens,
            )
        )

        i += 1

    suffix_lines = list(interstitial)

    while i < len(lines):
        if lines[i].strip() == "</event>":
            closing = lines[i]

            return (
                EventBlock(
                    opening=opening,
                    prefix_lines=prefix_lines,
                    header_line=header_line,
                    particles=particles,
                    suffix_lines=suffix_lines,
                    closing=closing,
                ),
                i + 1,
            )

        suffix_lines.append(lines[i])
        i += 1

    raise ValueError(
        "unterminated event"
    )


def build_groups(
    particles: list[Particle],
) -> tuple[
    list[int],
    dict[tuple[int, ...], list[int]],
]:
    roots: list[int] = []

    groups: dict[
        tuple[int, ...],
        list[int],
    ] = collections.defaultdict(list)

    for particle in particles:
        if not particle.mothers:
            roots.append(
                particle.old_index
            )
        else:
            groups[
                particle.mothers
            ].append(
                particle.old_index
            )

    roots.sort()

    for children in groups.values():
        children.sort()

    return roots, dict(groups)


def build_greedy_order(
    particles: list[Particle],
) -> list[int]:

    roots, groups = build_groups(
        particles
    )

    if not roots:
        raise ValueError(
            "event has no root particles"
        )

    order = list(roots)
    placed = set(order)

    remaining = dict(groups)

    while remaining:
        ready = [
            mothers
            for mothers in remaining
            if set(mothers).issubset(
                placed
            )
        ]

        if not ready:
            raise ValueError(
                "no serialization progress possible; "
                "graph contains an unresolved dependency "
                "or cycle"
            )

        # Preserve WHIZARD order as much as possible.
        #
        # Among currently legal sibling blocks, place whichever
        # block occurred earliest in the original event record.
        ready.sort(
            key=lambda mothers: (
                min(
                    remaining[mothers]
                ),
                mothers,
            )
        )

        chosen = ready[0]

        children = remaining.pop(
            chosen
        )

        order.extend(children)
        placed.update(children)

    n = len(particles)

    if (
        len(order) != n
        or len(set(order)) != n
        or set(order) != set(
            range(1, n + 1)
        )
    ):
        raise ValueError(
            "serializer did not construct a particle permutation"
        )

    return order


def remap_particle(
    particle: Particle,
    old_to_new: dict[int, int],
) -> list[str]:

    tokens = list(
        particle.tokens
    )

    m1 = particle.m1
    m2 = particle.m2

    if m1:
        if m1 not in old_to_new:
            raise ValueError(
                f"unmapped mother index {m1}"
            )

        tokens[2] = str(
            old_to_new[m1]
        )

    if m2:
        if m2 not in old_to_new:
            raise ValueError(
                f"unmapped mother index {m2}"
            )

        tokens[3] = str(
            old_to_new[m2]
        )

    return tokens


def validate_output_particles(
    particles: list[list[str]],
) -> None:

    n = len(particles)

    children: dict[
        int,
        list[int],
    ] = collections.defaultdict(list)

    for child_index, tokens in enumerate(
        particles,
        start=1,
    ):
        m1 = int(tokens[2])
        m2 = int(tokens[3])

        mothers = {
            m1,
            m2,
        }

        mothers.discard(0)

        for mother in mothers:
            if mother < 1 or mother > n:
                raise ValueError(
                    f"child {child_index}: mother {mother} "
                    f"outside [1,{n}]"
                )

            if mother >= child_index:
                raise ValueError(
                    f"child {child_index}: mother {mother} "
                    "does not precede child"
                )

            children[
                mother
            ].append(
                child_index
            )

    for parent, direct_children in children.items():
        actual = sorted(
            set(direct_children)
        )

        expected = list(
            range(
                actual[0],
                actual[-1] + 1,
            )
        )

        if actual != expected:
            raise ValueError(
                f"parent {parent} has non-contiguous daughters "
                f"{actual}; implied range would be {expected}"
            )


def serialize_event(
    event: EventBlock,
) -> tuple[
    list[str],
    dict[str, int],
]:

    particles = event.particles

    original_order = list(
        range(
            1,
            len(particles) + 1,
        )
    )

    order = build_greedy_order(
        particles
    )

    old_to_new = {
        old: new
        for new, old in enumerate(
            order,
            start=1,
        )
    }

    reordered_tokens: list[
        list[str]
    ] = []

    moved_particles = 0
    max_displacement = 0

    for new_index, old_index in enumerate(
        order,
        start=1,
    ):
        particle = particles[
            old_index - 1
        ]

        tokens = remap_particle(
            particle,
            old_to_new,
        )

        reordered_tokens.append(
            tokens
        )

        displacement = abs(
            new_index - old_index
        )

        if displacement:
            moved_particles += 1

        max_displacement = max(
            max_displacement,
            displacement,
        )

    validate_output_particles(
        reordered_tokens
    )

    # Verify that every non-mother token is bit-for-bit identical
    # to the source particle that occupies this new row.
    for new_index, old_index in enumerate(
        order,
        start=1,
    ):
        old_tokens = particles[
            old_index - 1
        ].tokens

        new_tokens = reordered_tokens[
            new_index - 1
        ]

        for column in range(
            len(old_tokens)
        ):
            if column in (2, 3):
                continue

            if old_tokens[column] != new_tokens[column]:
                raise ValueError(
                    "non-mother particle data changed during "
                    f"serialization: old={old_index} "
                    f"new={new_index} column={column}"
                )

    output_lines = [
        event.opening,
        *event.prefix_lines,
        event.header_line,
    ]

    for tokens in reordered_tokens:
        output_lines.append(
            " ".join(tokens) + "\n"
        )

    output_lines.extend(
        event.suffix_lines
    )

    output_lines.append(
        event.closing
    )

    return (
        output_lines,
        {
            "particles": len(particles),
            "moved_particles": moved_particles,
            "max_displacement": max_displacement,
            "reordered": int(
                order != original_order
            ),
        },
    )


def main() -> int:
    args = parse_args()

    input_path = args.input.resolve()
    output_path = args.output.resolve()
    summary_path = args.summary.resolve()

    lines = input_path.read_text(
        errors="replace"
    ).splitlines(
        keepends=True
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_lines: list[str] = []

    total_events = 0
    reordered_events = 0
    total_particles = 0
    total_moved_particles = 0
    max_displacement = 0

    i = 0

    while i < len(lines):
        if lines[i].strip() != "<event>":
            output_lines.append(
                lines[i]
            )
            i += 1
            continue

        event, next_i = read_event(
            lines,
            i,
        )

        serialized, stats = serialize_event(
            event
        )

        output_lines.extend(
            serialized
        )

        total_events += 1
        reordered_events += stats[
            "reordered"
        ]

        total_particles += stats[
            "particles"
        ]

        total_moved_particles += stats[
            "moved_particles"
        ]

        max_displacement = max(
            max_displacement,
            stats[
                "max_displacement"
            ],
        )

        i = next_i

    output_path.write_text(
        "".join(output_lines)
    )

    summary = {
        "schema_version": 1,
        "tool": (
            "reorder_lhe_history_for_pythia_v1"
        ),
        "input_path": str(
            input_path
        ),
        "output_path": str(
            output_path
        ),
        "total_events": total_events,
        "total_particles": total_particles,
        "reordered_events": reordered_events,
        "already_valid_events": (
            total_events
            - reordered_events
        ),
        "total_moved_particles": (
            total_moved_particles
        ),
        "max_particle_displacement": (
            max_displacement
        ),
        "particles_added": 0,
        "particles_removed": 0,
        "resonances_added": 0,
        "resonances_removed": 0,
    }

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        "HISTORY SERIALIZATION SUCCESS "
        f"events={total_events} "
        f"reordered={reordered_events} "
        f"moved_particles={total_moved_particles} "
        f"max_displacement={max_displacement} "
        f"output={output_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
