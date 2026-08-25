#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

GRID_SPECS = {
    "S0": {"grid_label": "S0", "seed_start": 211170001},
    "S1": {"grid_label": "S1", "seed_start": 211171001},
    "S2": {"grid_label": "S2", "seed_start": 211172001},
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Phase 11C.5G-A 60-job itemdata.")
    p.add_argument("--grid-catalog", required=True, type=Path)
    p.add_argument("--itemdata", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--events-per-shard", type=int, default=500)
    p.add_argument("--shards-per-grid", type=int, default=20)
    return p.parse_args()


def load_catalog(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    required = {
        "grid_label",
        "checkpoint_kind",
        "workspace_tar",
        "vg2_sha256",
        "phs_sha256",
        "grid_construction_seed",
    }
    if not rows:
        raise SystemExit(f"ERROR: empty grid catalog: {path}")
    missing = required - set(rows[0])
    if missing:
        raise SystemExit(f"ERROR: grid catalog missing columns: {sorted(missing)}")
    out = {r["grid_label"]: r for r in rows}
    for label in ("S0", "S1", "S2"):
        if label not in out:
            raise SystemExit(f"ERROR: grid catalog missing {label}")
    return out


def main() -> None:
    args = parse_args()
    if args.events_per_shard <= 0 or args.shards_per_grid <= 0:
        raise SystemExit("ERROR: events/shards must be positive")

    catalog = load_catalog(args.grid_catalog)
    args.itemdata.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    item_lines: list[str] = []
    manifest_rows: list[list[str]] = []
    header = [
        "mode",
        "grid_label",
        "checkpoint_kind",
        "workspace_tar",
        "vg2_sha256",
        "phs_sha256",
        "grid_construction_seed",
        "shard_rng_seed",
        "metadata_seed",
        "events",
    ]

    for family in ("S0", "S1", "S2"):
        r = catalog[GRID_SPECS[family]["grid_label"]]
        start = GRID_SPECS[family]["seed_start"]
        for idx in range(1, args.shards_per_grid + 1):
            mode = f"{family}_GA{idx:02d}"
            seed = start + idx - 1
            fields = [
                mode,
                family,
                r["checkpoint_kind"],
                r["workspace_tar"],
                r["vg2_sha256"],
                r["phs_sha256"],
                r["grid_construction_seed"],
                str(seed),
                str(seed),
                str(args.events_per_shard),
            ]
            item_lines.append("\t".join(fields))
            manifest_rows.append(fields)

    args.itemdata.write_text("\n".join(item_lines) + "\n")
    with args.manifest.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(manifest_rows)

    print(f"C5GA_ITEMDATA_ROWS={len(item_lines)}")
    print(f"C5GA_ITEMDATA={args.itemdata}")
    print(f"C5GA_JOB_MANIFEST={args.manifest}")
    print("C5GA_ITEMDATA_BUILD=PASS")


if __name__ == "__main__":
    main()
