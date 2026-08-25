#!/usr/bin/env python3

from __future__ import annotations

import collections
import sys
from pathlib import Path


def classify_top(pid: int, children: list[int]) -> str:
    s = set(children)

    if pid == 6:
        if s == {24, 5}:
            return "explicit_W"
        if s == {5, -11, 12}:
            return "flat_3body"
        return "other:" + ",".join(map(str, sorted(children)))

    if pid == -6:
        if s == {-24, -5}:
            return "explicit_W"
        if s == {-5, 13, -14}:
            return "flat_3body"
        return "other:" + ",".join(map(str, sorted(children)))

    return "not_top"


def iter_events(path: Path):
    inside = False
    header_seen = False
    remaining = 0
    particles = []

    with path.open(errors="replace") as stream:
        for line in stream:
            s = line.strip()

            if s == "<event>":
                inside = True
                header_seen = False
                particles = []
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

                toks = s.split()

                particles.append(
                    {
                        "pid": int(toks[0]),
                        "status": int(toks[1]),
                        "m1": int(toks[2]),
                        "m2": int(toks[3]),
                    }
                )

                remaining -= 1
                continue

            if s == "</event>":
                yield particles
                inside = False


def main(paths: list[str]) -> int:

    pair_counter = collections.Counter()
    w_counter = collections.Counter()
    nup_counter = collections.Counter()
    malformed = collections.Counter()

    total = 0

    for raw_path in paths:
        path = Path(raw_path)

        print(f"SCANNING {path}", file=sys.stderr)

        local = 0

        for particles in iter_events(path):
            total += 1
            local += 1
            nup_counter[len(particles)] += 1

            tops = [
                i
                for i, p in enumerate(particles, start=1)
                if p["pid"] == 6
            ]

            antitops = [
                i
                for i, p in enumerate(particles, start=1)
                if p["pid"] == -6
            ]

            if len(tops) != 1 or len(antitops) != 1:
                malformed[
                    f"top_count={len(tops)},tbar_count={len(antitops)}"
                ] += 1
                continue

            top_i = tops[0]
            tbar_i = antitops[0]

            children = collections.defaultdict(list)

            for i, p in enumerate(particles, start=1):
                for mother in {p["m1"], p["m2"]}:
                    if mother:
                        children[mother].append(i)

            top_children = [
                particles[i - 1]["pid"]
                for i in sorted(set(children[top_i]))
            ]

            tbar_children = [
                particles[i - 1]["pid"]
                for i in sorted(set(children[tbar_i]))
            ]

            top_mode = classify_top(
                6,
                top_children,
            )

            tbar_mode = classify_top(
                -6,
                tbar_children,
            )

            pair_counter[
                (top_mode, tbar_mode)
            ] += 1

            pids = {
                p["pid"]
                for p in particles
            }

            wp = 24 in pids
            wm = -24 in pids

            if wp and wm:
                w_mode = "both_W"
            elif wp:
                w_mode = "Wplus_only"
            elif wm:
                w_mode = "Wminus_only"
            else:
                w_mode = "no_W"

            w_counter[w_mode] += 1

        print(
            f"  events={local}",
            file=sys.stderr,
        )

    print()
    print("=" * 80)
    print("TTBAR RESONANCE-HISTORY CLASSIFICATION")
    print("=" * 80)
    print(f"TOTAL_EVENTS={total}")

    print()
    print("TOP/TBAR DIRECT-CHILD MODES")

    for key, value in sorted(
        pair_counter.items(),
        key=lambda kv: (-kv[1], kv[0]),
    ):
        frac = value / total if total else 0.0

        print(
            f"{key[0]:20s} "
            f"{key[1]:20s} "
            f"{value:8d} "
            f"{100.0*frac:9.5f}%"
        )

    print()
    print("EXPLICIT-W PRESENCE")

    for key, value in sorted(
        w_counter.items(),
        key=lambda kv: (-kv[1], kv[0]),
    ):
        frac = value / total if total else 0.0

        print(
            f"{key:20s} "
            f"{value:8d} "
            f"{100.0*frac:9.5f}%"
        )

    print()
    print("NUP DISTRIBUTION")

    for key, value in sorted(nup_counter.items()):
        print(
            f"NUP={key:3d}  events={value}"
        )

    print()
    print("MALFORMED / UNCLASSIFIED")

    if not malformed:
        print("none")
    else:
        for key, value in malformed.items():
            print(
                f"{key}: {value}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(sys.argv[1:])
    )
