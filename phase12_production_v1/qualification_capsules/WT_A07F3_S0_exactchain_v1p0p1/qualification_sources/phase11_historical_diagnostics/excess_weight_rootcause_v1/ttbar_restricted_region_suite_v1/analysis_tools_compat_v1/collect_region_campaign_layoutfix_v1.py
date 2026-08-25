#!/usr/bin/env python3
"""
Post-run collector for the Phase-11 unrestricted region campaign.

Why this exists
---------------
The original region campaign manifest recorded the intended layout:

    OUTPUT_ROOT / WINDOW / REGION / RECIPE / ...

but the standard worker sourced campaign.env after parsing --output-root.
campaign.env contained the global OUTPUT_ROOT and therefore overwrote the
region-specific CLI value.

Consequently, successful jobs wrote to:

    GLOBAL_OUTPUT_ROOT/adaptive/<MODE>/
    GLOBAL_OUTPUT_ROOT/fixed/<PARENT_MODE>/<FIXED_ID>/

All DAG nodes can still be scientifically valid because parents and children
used the same runtime layout consistently.  This collector resolves both the
manifest-intended path and the actual runtime path without modifying the
frozen campaign manifest.

The collector fails if any expected node lacks PASS status.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Use the campaign's frozen common.py for exact WHIZARD log parsing semantics.
def import_campaign_common(campaign: Path):
    sys.path.insert(0, str(campaign / "scripts"))
    from common import parse_log, write_tsv
    return parse_log, write_tsv


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def find_log(directory: Path) -> Path | None:
    for name in ("console.log", "whizard.log"):
        candidate = directory / name
        if candidate.is_file():
            return candidate

    logs = sorted(directory.glob("*.log"))
    return logs[0] if logs else None


def runtime_output_dir(global_root: Path, row: dict[str, str]) -> Path:
    stage = row["stage"]

    if stage == "adaptive":
        return (
            global_root
            / "adaptive"
            / row["mode"]
        )

    if stage == "fixed":
        return (
            global_root
            / "fixed"
            / row["parent_mode"]
            / row["fixed_id"]
        )

    raise ValueError(
        f"unsupported stage {stage!r} for node {row.get('node')}"
    )


def resolve_output_dir(
    global_root: Path,
    row: dict[str, str],
) -> tuple[Path, str]:
    """
    Prefer the frozen manifest path if it actually contains output.
    Otherwise use the known runtime-layout fallback.
    """

    manifest_dir = Path(row["output_dir"])
    runtime_dir = runtime_output_dir(global_root, row)

    if (manifest_dir / "STATUS.txt").is_file():
        return manifest_dir, "manifest"

    if (runtime_dir / "STATUS.txt").is_file():
        return runtime_dir, "runtime_flat_fallback"

    # If neither has STATUS, preserve the best diagnostics.
    if manifest_dir.exists():
        return manifest_dir, "manifest_missing_status"

    if runtime_dir.exists():
        return runtime_dir, "runtime_missing_status"

    return runtime_dir, "missing"


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--campaign-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--outdir",
        type=Path,
        default=None,
    )

    args = parser.parse_args()

    campaign = args.campaign_dir.resolve()

    parse_log, write_tsv = import_campaign_common(campaign)

    manifest_path = campaign / "campaign_manifest.tsv"
    design_path = campaign / "CAMPAIGN_DESIGN.json"

    if not manifest_path.is_file():
        raise SystemExit(
            f"ERROR: missing manifest: {manifest_path}"
        )

    if not design_path.is_file():
        raise SystemExit(
            f"ERROR: missing design record: {design_path}"
        )

    design = load_json(design_path)

    if "output_root" not in design:
        raise SystemExit(
            "ERROR: CAMPAIGN_DESIGN.json has no output_root"
        )

    global_root = Path(design["output_root"])

    with manifest_path.open(newline="") as handle:
        manifest = list(
            csv.DictReader(
                handle,
                delimiter="\t",
            )
        )

    if not manifest:
        raise SystemExit("ERROR: empty campaign manifest")

    outdir = (
        args.outdir.resolve()
        if args.outdir
        else campaign / "collected"
    )

    outdir.mkdir(
        parents=True,
        exist_ok=True,
    )

    node_rows: list[dict] = []
    iteration_rows: list[dict] = []
    resolution_rows: list[dict] = []

    for row in manifest:
        resolved_dir, resolution = resolve_output_dir(
            global_root,
            row,
        )

        manifest_dir = Path(row["output_dir"])

        status_file = resolved_dir / "STATUS.txt"

        if status_file.is_file():
            status = status_file.read_text().strip()
        else:
            status = "MISSING"

        metadata = {}

        for name in (
            "metadata.json",
            "fixed_child_metadata.json",
        ):
            path = resolved_dir / name

            if path.is_file():
                metadata = load_json(path)
                break

        log = find_log(resolved_dir)

        node = dict(row)

        node.update(
            manifest_output_dir=str(manifest_dir),
            resolved_output_dir=str(resolved_dir),
            output_layout_resolution=resolution,
            output_status=status,
            metadata_status=metadata.get("status", ""),
            whizard_rc=metadata.get("whizard_rc", ""),
            phs_sha256=metadata.get(
                "phs_sha256",
                metadata.get("final_phs_sha256", ""),
            ),
            vg2_sha256=metadata.get(
                "vg2_sha256",
                metadata.get("final_vg2_sha256", ""),
            ),
            parent_vg2_sha256=metadata.get(
                "parent_vg2_sha256",
                "",
            ),
            reuse_message_count=metadata.get(
                "reuse_message_count",
                "",
            ),
            new_grid_init_count=metadata.get(
                "new_grid_init_count",
                "",
            ),
            phs_unchanged=metadata.get(
                "phs_unchanged",
                "",
            ),
            console_log=str(log or ""),
            artifact_present=int(
                (resolved_dir / "integration_artifacts.tar.gz").is_file()
            ),
        )

        node_rows.append(node)

        resolution_rows.append(
            {
                "node": row["node"],
                "stage": row["stage"],
                "mode": row["mode"],
                "manifest_output_dir": str(manifest_dir),
                "resolved_output_dir": str(resolved_dir),
                "resolution": resolution,
                "status": status,
            }
        )

        if log:
            parsed = parse_log(log)

            for parsed_row in parsed:
                record = {
                    key: row.get(key, "")
                    for key in (
                        "node",
                        "stage",
                        "mode",
                        "adaptive_id",
                        "fixed_id",
                        "seed_id",
                        "recipe_id",
                        "region_id",
                        "window_id",
                        "aggregate",
                    )
                }

                record.update(parsed_row)

                iteration_rows.append(record)

    write_tsv(
        outdir / "node_summary.tsv",
        node_rows,
    )

    write_tsv(
        outdir / "iteration_rows.tsv",
        iteration_rows,
    )

    write_tsv(
        outdir / "output_layout_resolution.tsv",
        resolution_rows,
    )

    status_counts = Counter(
        row["output_status"]
        for row in node_rows
    )

    resolution_counts = Counter(
        row["output_layout_resolution"]
        for row in node_rows
    )

    expected = len(node_rows)
    passed = status_counts.get("PASS", 0)

    print(
        f"NODE_SUMMARY={outdir / 'node_summary.tsv'}"
    )

    print(
        f"ITERATION_ROWS={outdir / 'iteration_rows.tsv'}"
    )

    print(
        "OUTPUT_LAYOUT_RESOLUTION="
        f"{outdir / 'output_layout_resolution.tsv'}"
    )

    print(f"NODES_EXPECTED={expected}")
    print(f"NODES_PASS={passed}")
    print(f"ITERATION_ROWS_COUNT={len(iteration_rows)}")

    print("STATUS_COUNTS:")
    for key, value in sorted(status_counts.items()):
        print(f"  {key}={value}")

    print("LAYOUT_RESOLUTION_COUNTS:")
    for key, value in sorted(resolution_counts.items()):
        print(f"  {key}={value}")

    if passed != expected:
        print(
            "ERROR: not all expected nodes resolved to PASS",
            file=sys.stderr,
        )

        for row in node_rows:
            if row["output_status"] != "PASS":
                print(
                    f"  {row['node']}: "
                    f"{row['output_status']} "
                    f"{row['resolved_output_dir']}",
                    file=sys.stderr,
                )

        return 2

    if len(iteration_rows) == 0:
        print(
            "ERROR: zero WHIZARD iteration rows parsed",
            file=sys.stderr,
        )
        return 3

    print("COLLECT_REGION_LAYOUTFIX=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
