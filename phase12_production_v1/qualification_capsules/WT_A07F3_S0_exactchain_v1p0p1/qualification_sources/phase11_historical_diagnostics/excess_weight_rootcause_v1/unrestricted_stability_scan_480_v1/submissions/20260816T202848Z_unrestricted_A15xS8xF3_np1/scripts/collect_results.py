#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROW_RE = re.compile(
    r"^\s*(?P<iteration>\d+)\s+"
    r"(?P<calls>\d+)\s+"
    r"(?P<integral>[+-]?\d+(?:\.\d*)?[Ee][+-]?\d+)\s+"
    r"(?P<error>[+-]?\d+(?:\.\d*)?[Ee][+-]?\d+)\s+"
    r"(?P<errpct>[+-]?\d+(?:\.\d*)?)\s+"
    r"(?P<acc>[+-]?\d+(?:\.\d*)?)\*?\s+"
    r"(?P<eff>[+-]?\d+(?:\.\d*)?)"
)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def find_console(d: Path) -> Path | None:
    preferred = [d / "console.log", d / "whizard.log"]
    for p in preferred:
        if p.is_file():
            return p
    logs = sorted(d.glob("*.log"))
    return logs[0] if logs else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-dir", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=None)
    args = ap.parse_args()

    campaign = args.campaign_dir.resolve()
    outdir = args.outdir.resolve() if args.outdir else campaign / "collected"
    outdir.mkdir(parents=True, exist_ok=True)

    with (campaign / "campaign_manifest.tsv").open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    node_rows = []
    iteration_rows = []

    for r in rows:
        d = Path(r["output_dir"])
        status_file = d / "STATUS.txt"
        status = status_file.read_text().strip() if status_file.is_file() else "MISSING"

        md_path = d / ("metadata.json" if r["stage"] == "adaptive" else "fixed_child_metadata.json")
        md = load_json(md_path) if md_path.is_file() else {}
        console = find_console(d)

        node_rows.append(
            {
                **r,
                "output_status": status,
                "metadata_status": str(md.get("status", "")),
                "whizard_rc": str(md.get("whizard_rc", "")),
                "phs_sha256": str(md.get("phs_sha256", md.get("final_phs_sha256", ""))),
                "vg2_sha256": str(md.get("vg2_sha256", md.get("final_vg2_sha256", ""))),
                "parent_vg2_sha256": str(md.get("parent_vg2_sha256", "")),
                "reuse_message_count": str(md.get("reuse_message_count", "")),
                "new_grid_init_count": str(md.get("new_grid_init_count", "")),
                "phs_unchanged": str(md.get("phs_unchanged", "")),
                "console_log": str(console or ""),
                "artifact_present": "1" if (d / "integration_artifacts.tar.gz").is_file() else "0",
            }
        )

        if console is not None:
            for lineno, line in enumerate(console.read_text(errors="replace").splitlines(), 1):
                m = ROW_RE.match(line)
                if not m:
                    continue
                integral = float(m.group("integral"))
                error = float(m.group("error"))
                rel = abs(error / integral) if integral != 0 else math.inf
                iteration_rows.append(
                    {
                        "stage": r["stage"],
                        "mode": r["mode"],
                        "adaptive_id": r["adaptive_id"],
                        "fixed_id": r["fixed_id"],
                        "seed_id": r["seed_id"],
                        "line_number": lineno,
                        "iteration": int(m.group("iteration")),
                        "calls": int(m.group("calls")),
                        "integral_fb": integral,
                        "error_fb": error,
                        "relative_error": rel,
                        "reported_err_pct": float(m.group("errpct")),
                        "accuracy": float(m.group("acc")),
                        "efficiency_pct": float(m.group("eff")),
                        "raw_line": line.strip(),
                    }
                )

    node_fields = list(node_rows[0].keys())
    with (outdir / "node_summary.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=node_fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(node_rows)

    if iteration_rows:
        iter_fields = list(iteration_rows[0].keys())
        with (outdir / "iteration_rows.tsv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=iter_fields, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(iteration_rows)

    grouped = defaultdict(lambda: {"expected": 0, "pass": 0, "missing": 0, "fail": 0})
    for r in node_rows:
        key = (r["stage"], r["adaptive_id"], r["fixed_id"] or "PARENT")
        g = grouped[key]
        g["expected"] += 1
        if r["output_status"] == "PASS":
            g["pass"] += 1
        elif r["output_status"] == "MISSING":
            g["missing"] += 1
        else:
            g["fail"] += 1

    fam_rows = []
    for (stage, aid, fid), g in sorted(grouped.items()):
        fam_rows.append({"stage": stage, "adaptive_id": aid, "fixed_id": fid, **g})
    with (outdir / "family_completion.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fam_rows[0].keys()), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(fam_rows)

    print(f"NODE_SUMMARY={outdir / 'node_summary.tsv'}")
    print(f"ITERATION_ROWS={outdir / 'iteration_rows.tsv'}")
    print(f"FAMILY_COMPLETION={outdir / 'family_completion.tsv'}")
    print(f"NODES_EXPECTED={len(rows)}")
    print(f"NODES_PASS={sum(r['output_status']=='PASS' for r in node_rows)}")
    print("COLLECT_RESULTS=PASS")


if __name__ == "__main__":
    main()
