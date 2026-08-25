#!/usr/bin/env python3

from __future__ import annotations

import collections
import math
import sys
from pathlib import Path


TARGET_FINAL = {
    5: "b",
    -5: "bbar",
    -11: "eplus",
    12: "nue",
    13: "muminus",
    -14: "numubar",
}


def add4(*vecs):
    return tuple(
        sum(v[i] for v in vecs)
        for i in range(4)
    )


def mass(v):
    px, py, pz, e = v
    m2 = e * e - px * px - py * py - pz * pz

    if m2 < 0 and abs(m2) < 1.0e-8:
        m2 = 0.0

    return math.sqrt(max(m2, 0.0))


def percentile(values, q):
    if not values:
        return float("nan")

    xs = sorted(values)

    if len(xs) == 1:
        return xs[0]

    pos = q * (len(xs) - 1)

    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))

    if lo == hi:
        return xs[lo]

    frac = pos - lo

    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def iter_events(path):
    inside = False
    header_seen = False
    remaining = 0
    particles = []

    local_event = 0

    with path.open(errors="replace") as f:
        for line in f:
            s = line.strip()

            if s == "<event>":
                inside = True
                header_seen = False
                remaining = 0
                particles = []
                local_event += 1
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

                t = s.split()

                particles.append(
                    {
                        "pid": int(t[0]),
                        "status": int(t[1]),
                        "m1": int(t[2]),
                        "m2": int(t[3]),
                        "col1": int(t[4]),
                        "col2": int(t[5]),
                        "p4": (
                            float(t[6]),
                            float(t[7]),
                            float(t[8]),
                            float(t[9]),
                        ),
                    }
                )

                remaining -= 1
                continue

            if s == "</event>":
                yield local_event, particles
                inside = False


def main(paths):

    pattern_count = collections.Counter()
    pattern_nup = collections.Counter()

    mass_data = collections.defaultdict(
        lambda: {
            "Wp": [],
            "Wm": [],
            "t": [],
            "tbar": [],
        }
    )

    first_example = {}

    total = 0
    bad_final_state = 0

    for raw in paths:
        path = Path(raw)

        print(
            f"SCANNING {path}",
            file=sys.stderr,
        )

        local_total = 0

        for local_event, particles in iter_events(path):
            total += 1
            local_total += 1

            pids = [
                p["pid"]
                for p in particles
            ]

            nt = pids.count(6)
            ntb = pids.count(-6)
            nwp = pids.count(24)
            nwm = pids.count(-24)

            pattern = (
                f"t{nt}_"
                f"tb{ntb}_"
                f"Wp{nwp}_"
                f"Wm{nwm}"
            )

            pattern_count[pattern] += 1
            pattern_nup[(pattern, len(particles))] += 1

            if pattern not in first_example:
                first_example[pattern] = (
                    str(path),
                    local_event,
                    len(particles),
                )

            finals = {}

            for pid in TARGET_FINAL:
                matches = [
                    p
                    for p in particles
                    if p["pid"] == pid
                    and p["status"] == 1
                ]

                if len(matches) != 1:
                    break

                finals[pid] = matches[0]["p4"]

            if len(finals) != len(TARGET_FINAL):
                bad_final_state += 1
                continue

            wp = add4(
                finals[-11],
                finals[12],
            )

            wm = add4(
                finals[13],
                finals[-14],
            )

            top = add4(
                wp,
                finals[5],
            )

            tbar = add4(
                wm,
                finals[-5],
            )

            mass_data[pattern]["Wp"].append(
                mass(wp)
            )

            mass_data[pattern]["Wm"].append(
                mass(wm)
            )

            mass_data[pattern]["t"].append(
                mass(top)
            )

            mass_data[pattern]["tbar"].append(
                mass(tbar)
            )

        print(
            f"  events={local_total}",
            file=sys.stderr,
        )

    print()
    print("=" * 120)
    print("RESONANCE-HISTORY / RECONSTRUCTED-MASS AUDIT")
    print("=" * 120)

    print(f"TOTAL_EVENTS={total}")
    print(
        f"BAD_FINAL_STATE_MULTIPLICITY={bad_final_state}"
    )

    print()
    print("HISTORY PATTERNS")
    print("-" * 120)

    for pattern, n in sorted(
        pattern_count.items(),
        key=lambda kv: (-kv[1], kv[0]),
    ):
        print(
            f"{pattern:24s} "
            f"{n:8d} "
            f"{100*n/total:10.5f}%"
        )

    print()
    print("PATTERN x NUP")
    print("-" * 120)

    for (pattern, nup), n in sorted(
        pattern_nup.items(),
        key=lambda kv: (
            kv[0][0],
            kv[0][1],
        ),
    ):
        print(
            f"{pattern:24s} "
            f"NUP={nup:2d} "
            f"events={n:8d}"
        )

    print()
    print("RECONSTRUCTED MASSES [GeV]")
    print("-" * 120)

    header = (
        f"{'pattern':24s} "
        f"{'n':>8s} "
        f"{'quantity':>8s} "
        f"{'mean':>12s} "
        f"{'p05':>12s} "
        f"{'p50':>12s} "
        f"{'p95':>12s} "
        f"{'min':>12s} "
        f"{'max':>12s}"
    )

    print(header)

    for pattern, n in sorted(
        pattern_count.items(),
        key=lambda kv: (-kv[1], kv[0]),
    ):
        for quantity in (
            "Wp",
            "Wm",
            "t",
            "tbar",
        ):
            vals = mass_data[pattern][quantity]

            if not vals:
                continue

            mean = sum(vals) / len(vals)

            print(
                f"{pattern:24s} "
                f"{len(vals):8d} "
                f"{quantity:>8s} "
                f"{mean:12.6f} "
                f"{percentile(vals,0.05):12.6f} "
                f"{percentile(vals,0.50):12.6f} "
                f"{percentile(vals,0.95):12.6f} "
                f"{min(vals):12.6f} "
                f"{max(vals):12.6f}"
            )

    print()
    print("FIRST EXAMPLE OF EACH HISTORY PATTERN")
    print("-" * 120)

    for pattern, (path, ev, nup) in sorted(
        first_example.items()
    ):
        print(
            f"{pattern:24s} "
            f"event={ev:8d} "
            f"NUP={nup:2d} "
            f"file={path}"
        )

    if bad_final_state == 0:
        print()
        print("FINAL_STATE_CONTENT_GATE=PASS")
    else:
        print()
        print("FINAL_STATE_CONTENT_GATE=FAIL")

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(sys.argv[1:])
    )
