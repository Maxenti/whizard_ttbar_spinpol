#!/usr/bin/env python3

from __future__ import annotations

import collections
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Particle:
    tokens: list[str]
    old_index: int

    @property
    def pid(self) -> int:
        return int(self.tokens[0])

    @property
    def status(self) -> int:
        return int(self.tokens[1])

    @property
    def mothers(self) -> tuple[int, ...]:
        vals = {
            int(self.tokens[2]),
            int(self.tokens[3]),
        }

        vals.discard(0)

        return tuple(sorted(vals))


def iter_events(path: Path):
    inside = False
    header_seen = False
    remaining = 0
    particles: list[Particle] = []
    event_number = 0

    with path.open(errors="replace") as stream:
        for line in stream:
            s = line.strip()

            if s == "<event>":
                inside = True
                header_seen = False
                remaining = 0
                particles = []
                event_number += 1
                continue

            if not inside:
                continue

            if not header_seen:
                if not s or s.startswith("#"):
                    continue

                remaining = int(s.split()[0])
                header_seen = True
                continue

            if remaining:
                if not s or s.startswith("#"):
                    continue

                tokens = s.split()

                particles.append(
                    Particle(
                        tokens=tokens,
                        old_index=len(particles) + 1,
                    )
                )

                remaining -= 1
                continue

            if s == "</event>":
                yield event_number, particles
                inside = False


def validate_candidate(
    particles: list[Particle],
    order: list[int],
) -> tuple[bool, str]:

    n = len(particles)

    if len(order) != n:
        return False, "wrong_order_length"

    if len(set(order)) != n:
        return False, "duplicate_particle_in_order"

    if set(order) != set(range(1, n + 1)):
        return False, "order_not_permutation"

    old_to_new = {
        old: new
        for new, old in enumerate(
            order,
            start=1,
        )
    }

    children_by_parent: dict[int, list[int]] = collections.defaultdict(list)

    for child_old in order:
        p = particles[child_old - 1]
        child_new = old_to_new[child_old]

        for mother_old in p.mothers:
            if mother_old not in old_to_new:
                return False, "unmapped_mother"

            mother_new = old_to_new[mother_old]

            if mother_new >= child_new:
                return (
                    False,
                    f"mother_not_before_child:"
                    f"{mother_old}->{child_old}",
                )

            children_by_parent[mother_new].append(
                child_new
            )

    for parent_new, children in children_by_parent.items():
        ordered = sorted(set(children))

        expected = list(
            range(
                ordered[0],
                ordered[-1] + 1,
            )
        )

        if ordered != expected:
            return (
                False,
                "noncontiguous_parent:"
                f"{parent_new}:"
                f"{ordered}",
            )

    return True, "ok"


def build_groups(
    particles: list[Particle],
):
    roots: list[int] = []

    groups: dict[
        tuple[int, ...],
        list[int],
    ] = collections.defaultdict(list)

    for p in particles:
        if not p.mothers:
            roots.append(
                p.old_index
            )
        else:
            groups[
                p.mothers
            ].append(
                p.old_index
            )

    for children in groups.values():
        children.sort()

    roots.sort()

    return roots, dict(groups)


def greedy_order(
    particles: list[Particle],
) -> list[int] | None:

    roots, groups = build_groups(
        particles
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
            return None

        # Preserve WHIZARD order as much as possible:
        # select the sibling group whose first original child appeared first.
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

    return order


def fallback_search(
    particles: list[Particle],
    *,
    max_states: int = 20000,
) -> tuple[list[int] | None, int]:

    roots, groups = build_groups(
        particles
    )

    initial_order = list(roots)
    initial_placed = frozenset(
        roots
    )

    group_items = {
        mothers: tuple(children)
        for mothers, children in groups.items()
    }

    states = 0

    def rec(
        order: list[int],
        placed: frozenset[int],
        remaining: frozenset[tuple[int, ...]],
    ) -> list[int] | None:
        nonlocal states

        states += 1

        if states > max_states:
            return None

        if not remaining:
            ok, _ = validate_candidate(
                particles,
                order,
            )

            return (
                list(order)
                if ok
                else None
            )

        ready = [
            mothers
            for mothers in remaining
            if set(mothers).issubset(
                placed
            )
        ]

        ready.sort(
            key=lambda mothers: (
                min(
                    group_items[mothers]
                ),
                mothers,
            )
        )

        for mothers in ready:
            children = group_items[
                mothers
            ]

            result = rec(
                order + list(children),
                placed.union(children),
                remaining.difference(
                    {mothers}
                ),
            )

            if result is not None:
                return result

        return None

    result = rec(
        initial_order,
        initial_placed,
        frozenset(group_items),
    )

    return result, states


def history_pattern(
    particles: list[Particle],
) -> str:
    pids = [
        p.pid
        for p in particles
    ]

    return (
        f"t{pids.count(6)}_"
        f"tb{pids.count(-6)}_"
        f"Wp{pids.count(24)}_"
        f"Wm{pids.count(-24)}"
    )


def main(paths: list[str]) -> int:

    total_events = 0
    feasible_events = 0
    greedy_pass = 0
    fallback_pass = 0
    failed_events = 0

    already_valid_original_order = 0
    reordered_events = 0

    max_particle_displacement = 0
    total_moved_particles = 0

    root_count_hist = collections.Counter()
    group_count_hist = collections.Counter()
    pattern_total = collections.Counter()
    pattern_pass = collections.Counter()
    failure_reason = collections.Counter()

    first_failures = []

    max_fallback_states = 0

    for raw_path in paths:
        path = Path(raw_path)

        print(
            f"SCANNING {path}",
            file=sys.stderr,
        )

        local = 0

        for event_number, particles in iter_events(path):
            total_events += 1
            local += 1

            pattern = history_pattern(
                particles
            )

            pattern_total[pattern] += 1

            roots, groups = build_groups(
                particles
            )

            root_count_hist[
                len(roots)
            ] += 1

            group_count_hist[
                len(groups)
            ] += 1

            original = list(
                range(
                    1,
                    len(particles) + 1,
                )
            )

            original_ok, _ = validate_candidate(
                particles,
                original,
            )

            if original_ok:
                already_valid_original_order += 1

            candidate = greedy_order(
                particles
            )

            ok = False
            reason = "greedy_no_order"

            if candidate is not None:
                ok, reason = validate_candidate(
                    particles,
                    candidate,
                )

            if ok:
                greedy_pass += 1
            else:
                candidate, states = fallback_search(
                    particles
                )

                max_fallback_states = max(
                    max_fallback_states,
                    states,
                )

                if candidate is not None:
                    ok, reason = validate_candidate(
                        particles,
                        candidate,
                    )

                if ok:
                    fallback_pass += 1

            if not ok or candidate is None:
                failed_events += 1
                failure_reason[reason] += 1

                if len(first_failures) < 20:
                    first_failures.append(
                        (
                            str(path),
                            event_number,
                            pattern,
                            len(particles),
                            len(roots),
                            len(groups),
                            reason,
                        )
                    )

                continue

            feasible_events += 1
            pattern_pass[pattern] += 1

            if candidate != original:
                reordered_events += 1

            old_to_new = {
                old: new
                for new, old in enumerate(
                    candidate,
                    start=1,
                )
            }

            moved = 0

            for old in original:
                displacement = abs(
                    old_to_new[old] - old
                )

                max_particle_displacement = max(
                    max_particle_displacement,
                    displacement,
                )

                if displacement:
                    moved += 1

            total_moved_particles += moved

        print(
            f"  events={local}",
            file=sys.stderr,
        )

    print()
    print("=" * 100)
    print("HISTORY-PRESERVING LHE REORDER FEASIBILITY")
    print("=" * 100)

    print(f"TOTAL_EVENTS={total_events}")
    print(f"FEASIBLE_EVENTS={feasible_events}")
    print(f"FAILED_EVENTS={failed_events}")

    print()
    print(f"GREEDY_PASS={greedy_pass}")
    print(f"FALLBACK_PASS={fallback_pass}")
    print(
        f"MAX_FALLBACK_STATES="
        f"{max_fallback_states}"
    )

    print()
    print(
        "ALREADY_VALID_ORIGINAL_ORDER="
        f"{already_valid_original_order}"
    )
    print(
        f"REORDERED_EVENTS="
        f"{reordered_events}"
    )

    print(
        "TOTAL_MOVED_PARTICLES="
        f"{total_moved_particles}"
    )

    print(
        "MAX_PARTICLE_DISPLACEMENT="
        f"{max_particle_displacement}"
    )

    print()
    print("ROOT COUNT HISTOGRAM")

    for n, count in sorted(
        root_count_hist.items()
    ):
        print(
            f"roots={n} events={count}"
        )

    print()
    print("SIBLING-GROUP COUNT HISTOGRAM")

    for n, count in sorted(
        group_count_hist.items()
    ):
        print(
            f"groups={n} events={count}"
        )

    print()
    print("HISTORY PATTERN FEASIBILITY")

    for pattern, n in sorted(
        pattern_total.items(),
        key=lambda kv: (
            -kv[1],
            kv[0],
        ),
    ):
        passed = pattern_pass[
            pattern
        ]

        print(
            f"{pattern:24s} "
            f"total={n:8d} "
            f"pass={passed:8d} "
            f"fail={n-passed:8d}"
        )

    print()
    print("FAILURE REASONS")

    if not failure_reason:
        print("none")
    else:
        for reason, count in failure_reason.most_common():
            print(
                f"{count:8d}  {reason}"
            )

    print()
    print("FIRST FAILURES")

    if not first_failures:
        print("none")
    else:
        for record in first_failures:
            print(
                "\t".join(
                    map(str, record)
                )
            )

    print()

    if (
        total_events > 0
        and feasible_events == total_events
    ):
        print(
            "HISTORY_PRESERVING_REORDER_GATE=PASS"
        )
        return 0

    print(
        "HISTORY_PRESERVING_REORDER_GATE=FAIL"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main(sys.argv[1:])
    )
