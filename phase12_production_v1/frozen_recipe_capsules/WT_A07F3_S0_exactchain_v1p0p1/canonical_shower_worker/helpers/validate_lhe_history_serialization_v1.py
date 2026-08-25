#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--input",
        required=True,
        type=Path,
    )

    p.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    return p.parse_args()


def iter_events(path: Path):
    inside = False
    got_header = False
    remaining = 0
    particles = []

    with path.open(errors="replace") as f:
        for line in f:
            s = line.strip()

            if s == "<event>":
                inside = True
                got_header = False
                particles = []
                continue

            if not inside:
                continue

            if not got_header:
                if not s or s.startswith("#"):
                    continue

                remaining = int(
                    s.split()[0]
                )

                got_header = True
                continue

            if remaining:
                if not s or s.startswith("#"):
                    continue

                particles.append(
                    s.split()
                )

                remaining -= 1
                continue

            if s == "</event>":
                yield particles
                inside = False


def mothers(tokens):
    values = {
        int(tokens[2]),
        int(tokens[3]),
    }

    values.discard(0)

    return tuple(
        sorted(values)
    )


def expected_order(particles):
    roots = []

    groups = collections.defaultdict(
        list
    )

    for i, p in enumerate(
        particles,
        start=1,
    ):
        ms = mothers(p)

        if not ms:
            roots.append(i)
        else:
            groups[ms].append(i)

    roots.sort()

    for children in groups.values():
        children.sort()

    order = list(roots)
    placed = set(order)

    remaining = dict(groups)

    while remaining:
        ready = [
            ms
            for ms in remaining
            if set(ms).issubset(
                placed
            )
        ]

        if not ready:
            raise RuntimeError(
                "no valid serialization order"
            )

        ready.sort(
            key=lambda ms: (
                min(
                    remaining[ms]
                ),
                ms,
            )
        )

        chosen = ready[0]
        children = remaining.pop(
            chosen
        )

        order.extend(children)
        placed.update(children)

    return order


def validate_topology(particles):
    children = collections.defaultdict(
        list
    )

    n = len(particles)

    for child, p in enumerate(
        particles,
        start=1,
    ):
        for mother in mothers(p):
            if not (
                1 <= mother < child <= n
            ):
                raise RuntimeError(
                    f"invalid mother/child "
                    f"{mother}->{child}"
                )

            children[mother].append(
                child
            )

    for parent, ds in children.items():
        ds = sorted(
            set(ds)
        )

        expected = list(
            range(
                ds[0],
                ds[-1] + 1,
            )
        )

        if ds != expected:
            raise RuntimeError(
                f"parent {parent} "
                f"non-contiguous daughters {ds}"
            )


def main():
    args = parse_args()

    input_events = iter_events(
        args.input
    )

    output_events = iter_events(
        args.output
    )

    total = 0
    particles_checked = 0
    moved_particles = 0
    max_displacement = 0

    while True:
        try:
            old = next(
                input_events
            )
            old_done = False
        except StopIteration:
            old = None
            old_done = True

        try:
            new = next(
                output_events
            )
            new_done = False
        except StopIteration:
            new = None
            new_done = True

        if old_done and new_done:
            break

        if old_done != new_done:
            raise RuntimeError(
                "input/output event counts differ"
            )

        assert old is not None
        assert new is not None

        total += 1

        if len(old) != len(new):
            raise RuntimeError(
                f"event {total}: NUP changed"
            )

        order = expected_order(
            old
        )

        old_to_new = {
            old_i: new_i
            for new_i, old_i in enumerate(
                order,
                start=1,
            )
        }

        for new_i, old_i in enumerate(
            order,
            start=1,
        ):
            old_tokens = old[
                old_i - 1
            ]

            new_tokens = new[
                new_i - 1
            ]

            if len(old_tokens) != len(
                new_tokens
            ):
                raise RuntimeError(
                    f"event {total}: token "
                    f"count changed"
                )

            expected = list(
                old_tokens
            )

            m1 = int(
                expected[2]
            )

            m2 = int(
                expected[3]
            )

            if m1:
                expected[2] = str(
                    old_to_new[m1]
                )

            if m2:
                expected[3] = str(
                    old_to_new[m2]
                )

            if expected != new_tokens:
                raise RuntimeError(
                    f"event {total}: "
                    f"particle mismatch "
                    f"old_index={old_i} "
                    f"new_index={new_i}"
                )

            particles_checked += 1

            displacement = abs(
                new_i - old_i
            )

            if displacement:
                moved_particles += 1

            max_displacement = max(
                max_displacement,
                displacement,
            )

        validate_topology(
            new
        )

    print(
        f"EVENTS_CHECKED={total}"
    )

    print(
        f"PARTICLES_CHECKED="
        f"{particles_checked}"
    )

    print(
        f"MOVED_PARTICLES="
        f"{moved_particles}"
    )

    print(
        f"MAX_PARTICLE_DISPLACEMENT="
        f"{max_displacement}"
    )

    print(
        "PARTICLE_CONTENT_PRESERVATION=PASS"
    )

    print(
        "MOTHER_INDEX_REMAP=PASS"
    )

    print(
        "MOTHER_BEFORE_CHILD=PASS"
    )

    print(
        "DAUGHTER_CONTIGUITY=PASS"
    )

    print(
        "HISTORY_SERIALIZATION_VALIDATION=PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
