#!/usr/bin/env python3

from __future__ import annotations

import math
import sys
from pathlib import Path


RANKS = [1, 2, 4, 8, 16]


def parse_keyvals(path: Path) -> dict[str, str]:
    out = {}

    if not path.exists():
        return out

    for line in path.read_text().splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()

    return out


def parse_final_row(path: Path):
    if not path.exists():
        return None

    line = path.read_text().strip()

    if not line:
        return None

    fields = line.split()

    if len(fields) < 4:
        return None

    try:
        return {
            "iteration": int(fields[0]),
            "calls": int(fields[1]),
            "integral_fb": float(fields[2]),
            "error_fb": float(fields[3]),
        }
    except ValueError:
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} EOS_RUN", file=sys.stderr)
        return 2

    root = Path(sys.argv[1])

    rows = []

    for n in RANKS:
        d = root / f"np{n}"

        timing = parse_keyvals(d / "time.txt")
        result = parse_final_row(d / "final_integration_row.txt")

        if not timing or result is None:
            print(f"WARNING: incomplete result for np={n}", file=sys.stderr)
            continue

        rows.append(
            {
                "ranks": n,
                "wall_s": float(timing["WALL_SECONDS"]),
                "user_s": float(timing.get("USER_SECONDS", "nan")),
                "sys_s": float(timing.get("SYS_SECONDS", "nan")),
                "max_rss_kb": float(timing.get("MAX_RSS_KB", "nan")),
                "exit_code": int(timing.get("EXIT_CODE", "-999")),
                **result,
            }
        )

    if not rows:
        print("ERROR: no complete scaling results found.", file=sys.stderr)
        return 1

    baseline = next((r for r in rows if r["ranks"] == 1), None)

    if baseline is None:
        print("ERROR: np=1 baseline is missing.", file=sys.stderr)
        return 1

    t1 = baseline["wall_s"]
    i1 = baseline["integral_fb"]
    e1 = baseline["error_fb"]

    print(
        "ranks\twall_s\twall_min\tspeedup\tefficiency"
        "\tcalls\tintegral_fb\terror_fb\tpull_vs_np1"
        "\tuser_s\tsys_s\tmax_rss_kb\texit_code"
    )

    for row in rows:
        n = row["ranks"]
        wall = row["wall_s"]

        speedup = t1 / wall
        efficiency = speedup / n

        if n == 1:
            pull = 0.0
        else:
            denom = math.sqrt(
                e1 * e1 + row["error_fb"] * row["error_fb"]
            )
            pull = (
                (row["integral_fb"] - i1) / denom
                if denom > 0
                else float("nan")
            )

        print(
            f"{n}\t"
            f"{wall:.2f}\t"
            f"{wall / 60.0:.3f}\t"
            f"{speedup:.6f}\t"
            f"{efficiency:.6f}\t"
            f"{row['calls']}\t"
            f"{row['integral_fb']:.10g}\t"
            f"{row['error_fb']:.6g}\t"
            f"{pull:.6f}\t"
            f"{row['user_s']:.2f}\t"
            f"{row['sys_s']:.2f}\t"
            f"{row['max_rss_kb']:.0f}\t"
            f"{row['exit_code']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
