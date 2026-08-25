#!/usr/bin/env python3

from __future__ import annotations

import collections
import sys
from pathlib import Path


def iter_events(path: Path):
    inside = False
    header = False
    remaining = 0
    particles = []

    with path.open(errors="replace") as f:
        for line in f:
            s = line.strip()

            if s == "<event>":
                inside = True
                header = False
                particles = []
                continue

            if not inside:
                continue

            if not header:
                if not s or s.startswith("#"):
                    continue

                remaining = int(s.split()[0])
                header = True
                continue

            if remaining:
                if not s or s.startswith("#"):
                    continue

                t = s.split()

                particles.append(
                    (
                        int(t[0]),
                        int(t[1]),
                    )
                )

                remaining -= 1
                continue

            if s == "</event>":
                yield particles
                inside = False


def pattern(event):
    pids = [pid for pid, _ in event]

    return (
        pids.count(6),
        pids.count(-6),
        pids.count(24),
        pids.count(-24),
    )


def stable_signature(event):
    return collections.Counter(
        pid
        for pid, status in event
        if status == 1
    )


def main(raw_paths, serialized_paths):
    if len(raw_paths) != len(serialized_paths):
        raise SystemExit(
            "ERROR: raw/serialized shard count differs"
        )

    total = 0

    for raw_path, ser_path in zip(
        raw_paths,
        serialized_paths,
    ):
        print(
            f"COMPARE\n"
            f"  RAW={raw_path}\n"
            f"  SER={ser_path}"
        )

        raw_iter = iter_events(
            Path(raw_path)
        )

        ser_iter = iter_events(
            Path(ser_path)
        )

        local = 0

        while True:
            try:
                raw = next(raw_iter)
                raw_done = False
            except StopIteration:
                raw = None
                raw_done = True

            try:
                ser = next(ser_iter)
                ser_done = False
            except StopIteration:
                ser = None
                ser_done = True

            if raw_done and ser_done:
                break

            if raw_done != ser_done:
                raise RuntimeError(
                    "event count mismatch"
                )

            assert raw is not None
            assert ser is not None

            local += 1
            total += 1

            if pattern(raw) != pattern(ser):
                raise RuntimeError(
                    f"event {local}: "
                    "resonance-history pattern changed"
                )

            if stable_signature(raw) != stable_signature(ser):
                raise RuntimeError(
                    f"event {local}: "
                    "stable final state changed"
                )

        print(f"  EVENTS={local}")

    print()
    print(f"EVENTS_COMPARED={total}")
    print("RESONANCE_HISTORY_PATTERN_PRESERVATION=PASS")
    print("STABLE_FINAL_STATE_PRESERVATION=PASS")
    print("RAW_VS_SERIALIZED_HISTORY_GATE=PASS")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--" not in args:
        raise SystemExit(
            "usage: compare.py RAW... -- SERIALIZED..."
        )

    split = args.index("--")

    main(
        args[:split],
        args[split + 1:],
    )
