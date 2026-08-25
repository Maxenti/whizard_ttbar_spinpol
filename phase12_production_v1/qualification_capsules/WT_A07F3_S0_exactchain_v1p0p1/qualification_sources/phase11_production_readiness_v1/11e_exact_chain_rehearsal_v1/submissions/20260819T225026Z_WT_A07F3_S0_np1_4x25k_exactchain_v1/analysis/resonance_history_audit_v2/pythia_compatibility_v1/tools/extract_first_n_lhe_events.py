#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def args():
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

    p.add_argument(
        "--events",
        required=True,
        type=int,
    )

    return p.parse_args()


def main():
    a = args()

    if a.events <= 0:
        raise SystemExit(
            "--events must be positive"
        )

    lines = a.input.read_text(
        errors="replace"
    ).splitlines(
        keepends=True
    )

    output = []
    in_event = False
    events = 0
    done = False

    for line in lines:
        s = line.strip()

        if done:
            if s == "</LesHouchesEvents>":
                output.append(line)
                break
            continue

        output.append(line)

        if s == "<event>":
            in_event = True

        elif in_event and s == "</event>":
            events += 1
            in_event = False

            if events == a.events:
                done = True

    if events != a.events:
        raise SystemExit(
            f"requested={a.events} "
            f"found={events}"
        )

    if not any(
        line.strip() == "</LesHouchesEvents>"
        for line in output
    ):
        output.append(
            "</LesHouchesEvents>\n"
        )

    a.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    a.output.write_text(
        "".join(output)
    )

    print(
        f"EXTRACT_EVENTS=PASS "
        f"events={events} "
        f"output={a.output}"
    )


if __name__ == "__main__":
    main()
