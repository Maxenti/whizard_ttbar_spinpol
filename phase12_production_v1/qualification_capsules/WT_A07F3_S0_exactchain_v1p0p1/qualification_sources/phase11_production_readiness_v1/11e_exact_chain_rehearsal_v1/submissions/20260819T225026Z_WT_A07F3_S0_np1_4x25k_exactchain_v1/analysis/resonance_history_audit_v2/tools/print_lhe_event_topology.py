#!/usr/bin/env python3

from pathlib import Path
import sys


path = Path(sys.argv[1])

inside = False
header = False
remaining = 0
particles = []

with path.open(errors="replace") as f:
    for line in f:
        s = line.strip()

        if s == "<event>":
            inside = True
            continue

        if not inside:
            continue

        if not header:
            if not s or s.startswith("#"):
                continue

            remaining = int(
                s.split()[0]
            )

            header = True
            continue

        if remaining:
            if not s or s.startswith("#"):
                continue

            particles.append(
                s.split()
            )

            remaining -= 1
            continue

        break


print(
    f"{'IDX':>3} "
    f"{'PDG':>7} "
    f"{'STAT':>5} "
    f"{'M1':>4} "
    f"{'M2':>4}"
)

print("-" * 31)

for i, p in enumerate(
    particles,
    start=1,
):
    print(
        f"{i:3d} "
        f"{int(p[0]):7d} "
        f"{int(p[1]):5d} "
        f"{int(p[2]):4d} "
        f"{int(p[3]):4d}"
    )


children = {}

for i, p in enumerate(
    particles,
    start=1,
):
    for mother in {
        int(p[2]),
        int(p[3]),
    }:
        if mother:
            children.setdefault(
                mother,
                [],
            ).append(i)


print()
print("PARENT -> CHILDREN")

bad = 0

for parent in sorted(children):
    ds = sorted(
        set(children[parent])
    )

    expected = list(
        range(
            ds[0],
            ds[-1] + 1,
        )
    )

    contiguous = (
        ds == expected
    )

    if not contiguous:
        bad += 1

    pdg = int(
        particles[parent - 1][0]
    )

    child_pdgs = [
        int(
            particles[x - 1][0]
        )
        for x in ds
    ]

    print(
        f"{parent:3d} "
        f"PDG={pdg:7d} "
        f"children={ds} "
        f"pdgs={child_pdgs} "
        f"contiguous={contiguous}"
    )

print()
print(
    f"NONCONTIGUOUS_PARENT_COUNT={bad}"
)
