#!/usr/bin/env python3

from __future__ import annotations

import csv
import sys
from pathlib import Path


def pattern_from_event(block: list[str]) -> tuple[str, int]:
    header_seen = False
    remaining = 0
    pids: list[int] = []
    nup = None

    for line in block:
        s = line.strip()

        if s in {"<event>", "</event>"}:
            continue

        if not header_seen:
            if not s or s.startswith("#"):
                continue

            nup = int(s.split()[0])
            remaining = nup
            header_seen = True
            continue

        if remaining:
            if not s or s.startswith("#"):
                continue

            pids.append(int(s.split()[0]))
            remaining -= 1

    if nup is None:
        raise RuntimeError("event has no header")

    pattern = (
        f"t{int(6 in pids)}_"
        f"tb{int(-6 in pids)}_"
        f"Wp{int(24 in pids)}_"
        f"Wm{int(-24 in pids)}"
    )

    return pattern, nup


def parse_file(path: Path):
    lines = path.read_text(
        errors="replace"
    ).splitlines(keepends=True)

    prefix: list[str] = []
    events: list[list[str]] = []

    i = 0

    while i < len(lines):
        if lines[i].strip() == "<event>":
            break

        prefix.append(lines[i])
        i += 1

    while i < len(lines):
        if lines[i].strip() != "<event>":
            i += 1
            continue

        block = [lines[i]]
        i += 1

        while i < len(lines):
            block.append(lines[i])

            if lines[i].strip() == "</event>":
                i += 1
                break

            i += 1

        events.append(block)

    return prefix, events


def write_lhe(
    output: Path,
    prefix: list[str],
    event_blocks: list[list[str]],
):
    payload = list(prefix)

    for block in event_blocks:
        payload.extend(block)

    payload.append("</LesHouchesEvents>\n")

    output.write_text("".join(payload))


def main(paths: list[str]) -> int:
    if not paths:
        raise SystemExit("no serialized LHE inputs")

    selected: dict[str, tuple[Path, int, int, list[str]]] = {}
    reference_prefix = None

    for raw_path in paths:
        path = Path(raw_path)

        prefix, events = parse_file(path)

        if reference_prefix is None:
            reference_prefix = prefix

        for event_index, block in enumerate(events, start=1):
            pattern, nup = pattern_from_event(block)

            if pattern not in selected:
                selected[pattern] = (
                    path,
                    event_index,
                    nup,
                    block,
                )

    expected = {
        f"t{t}_tb{tb}_Wp{wp}_Wm{wm}"
        for t in (0, 1)
        for tb in (0, 1)
        for wp in (0, 1)
        for wm in (0, 1)
    }

    missing = sorted(expected - set(selected))

    if missing:
        raise SystemExit(
            "missing history patterns: "
            + ", ".join(missing)
        )

    assert reference_prefix is not None

    output_root = Path(sys.argv[1]).resolve()

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Deterministic order.
    patterns = sorted(selected)

    history16_blocks = [
        selected[p][3]
        for p in patterns
    ]

    write_lhe(
        output_root / "history16.serialized_v1.lhe",
        reference_prefix,
        history16_blocks,
    )

    # Use the common fully resonant topology for the first one-event gate.
    full_pattern = "t1_tb1_Wp1_Wm1"

    write_lhe(
        output_root / "one_fullhistory.serialized_v1.lhe",
        reference_prefix,
        [selected[full_pattern][3]],
    )

    with (
        output_root / "history16_manifest.tsv"
    ).open("w", newline="") as f:
        writer = csv.writer(
            f,
            delimiter="\t",
        )

        writer.writerow(
            [
                "output_event_index",
                "pattern",
                "source_lhe",
                "source_event_index",
                "nup",
            ]
        )

        for out_index, pattern in enumerate(patterns):
            path, event_index, nup, _ = selected[pattern]

            writer.writerow(
                [
                    out_index,
                    pattern,
                    str(path),
                    event_index,
                    nup,
                ]
            )

    print(f"HISTORY_PATTERNS={len(patterns)}")

    for index, pattern in enumerate(patterns):
        path, event_index, nup, _ = selected[pattern]

        print(
            f"{index:2d} "
            f"{pattern:20s} "
            f"NUP={nup:2d} "
            f"event={event_index:6d} "
            f"file={path.name}"
        )

    print()
    print("HISTORY16_INPUT_GATE=PASS")

    return 0


if __name__ == "__main__":
    output = sys.argv[1]
    inputs = sys.argv[2:]

    old_argv = sys.argv
    sys.argv = [sys.argv[0], output]

    raise SystemExit(main(inputs))
