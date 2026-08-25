#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


def parse_kv(path):
    out = {}
    for line in Path(path).read_text().splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def parse_diag(path):
    text = Path(path).read_text()

    m = re.search(
        r"Encountered events with excess weight:\s*"
        r"(\d+)\s+events\s+\(\s*([0-9.eE+-]+)\s*%\)",
        text,
    )

    if m:
        excess_count = int(m.group(1))
        excess_percent = float(m.group(2))
    else:
        excess_count = 0
        excess_percent = 0.0

    m = re.search(
        r"Maximum excess weight\s*=\s*([0-9.eE+-]+)",
        text,
    )
    max_excess = float(m.group(1)) if m else 0.0

    m = re.search(
        r"Average excess weight\s*=\s*([0-9.eE+-]+)",
        text,
    )
    avg_excess = float(m.group(1)) if m else 0.0

    return {
        "excess_count": excess_count,
        "excess_percent": excess_percent,
        "max_excess": max_excess,
        "avg_excess": avg_excess,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--sample",
        action="append",
        required=True,
        help="NAME=/path/to/sample_dir",
    )
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []

    for spec in args.sample:
        name, directory = spec.split("=", 1)
        d = Path(directory)

        checks = parse_kv(d / "reuse_checks.txt")
        diag = parse_diag(d / "generation_diagnostics.txt")

        row = {
            "sample": name,
            "directory": str(d),
            "status": checks.get("STATUS", "UNKNOWN"),
            "whizard_rc": int(checks.get("WHIZARD_RC", "-999")),
            "events_requested": int(
                checks.get("EVENTS_REQUESTED", "-1")
            ),
            "events_written": int(
                checks.get("EVENTS_WRITTEN", "-1")
            ),
            "wall_seconds": int(
                checks.get("WALL_SECONDS", "-1")
            ),
            "workspace_unchanged": int(
                checks.get("WORKSPACE_UNCHANGED", "0")
            ),
            "new_grid_init_count": int(
                checks.get("NEW_GRID_INIT_COUNT", "-1")
            ),
            "efficiency_line": checks.get(
                "EFFICIENCY_LINE", ""
            ),
            **diag,
        }

        failures = []

        if row["status"] != "PASS":
            failures.append("status")

        if row["whizard_rc"] != 0:
            failures.append("whizard_rc")

        if row["events_requested"] != 10000:
            failures.append("requested_event_count")

        if row["events_written"] != 10000:
            failures.append("written_event_count")

        if row["workspace_unchanged"] != 1:
            failures.append("workspace_changed")

        if row["new_grid_init_count"] != 0:
            failures.append("new_grid_initialization")

        if row["excess_percent"] > 1.0:
            failures.append("excess_fraction_gt_1pct")

        if row["max_excess"] > 10.0:
            failures.append("max_excess_gt_10")

        if row["avg_excess"] > 0.01:
            failures.append("avg_excess_gt_0p01")

        row["gate"] = "PASS" if not failures else "FAIL"
        row["failures"] = ";".join(failures)

        rows.append(row)

    fields = [
        "sample",
        "gate",
        "status",
        "whizard_rc",
        "events_requested",
        "events_written",
        "wall_seconds",
        "workspace_unchanged",
        "new_grid_init_count",
        "excess_count",
        "excess_percent",
        "max_excess",
        "avg_excess",
        "efficiency_line",
        "failures",
        "directory",
    ]

    with (outdir / "generation_gate.tsv").open("w") as f:
        f.write("\t".join(fields) + "\n")
        for r in rows:
            f.write(
                "\t".join(str(r[x]) for x in fields) + "\n"
            )

    overall = all(r["gate"] == "PASS" for r in rows)

    payload = {
        "schema_version": 1,
        "gate": "PASS" if overall else "FAIL",
        "samples": rows,
        "thresholds": {
            "events": 10000,
            "workspace_unchanged": True,
            "new_grid_init_count": 0,
            "excess_percent_max": 1.0,
            "max_excess_max": 10.0,
            "avg_excess_max": 0.01,
        },
    }

    (outdir / "generation_gate.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )

    with (outdir / "generation_gate_summary.txt").open("w") as f:
        f.write(
            f"PHASE11C_GENERATION_GATE="
            f"{'PASS' if overall else 'FAIL'}\n\n"
        )

        for r in rows:
            f.write(
                f"{r['sample']}: "
                f"{r['gate']} "
                f"events={r['events_written']} "
                f"wall={r['wall_seconds']}s "
                f"excess={r['excess_percent']:.4f}% "
                f"max_excess={r['max_excess']:.6g} "
                f"avg_excess={r['avg_excess']:.6g}\n"
            )

    print(
        f"PHASE11C_GENERATION_GATE="
        f"{'PASS' if overall else 'FAIL'}"
    )

    for r in rows:
        print(
            f"{r['sample']:6s} "
            f"{r['gate']:4s} "
            f"events={r['events_written']:5d} "
            f"wall={r['wall_seconds']:5d}s "
            f"excess={r['excess_percent']:7.4f}% "
            f"max={r['max_excess']:9.4g}"
        )


if __name__ == "__main__":
    main()
