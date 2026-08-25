#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path

EXPECTED = {
    "S0": {"seed_start": 211170001, "seed_end": 211170020},
    "S1": {"seed_start": 211171001, "seed_end": 211171020},
    "S2": {"seed_start": 211172001, "seed_end": 211172020},
}
EXPECTED_EVENTS = 500
EXPECTED_SHARDS = 20
EXPECTED_TOTAL = 60

PRIOR_VALIDATION_SEEDS = {
    211120001, 211120002, 211120101, 211120102,
    211130001, 211130002,
    211140001, 211140002,
    211150001, 211150002,
    211160001, 211160002, 211160101, 211160102,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate C5G-A itemdata before submission.")
    p.add_argument("--itemdata", required=True, type=Path)
    p.add_argument("--grid-catalog", required=True, type=Path)
    p.add_argument("--worker", required=True, type=Path)
    p.add_argument("--expected-worker-sha", required=True)
    p.add_argument("--source-card", required=True, type=Path)
    return p.parse_args()


def load_catalog(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return {r["grid_label"]: r for r in rows}


def main() -> None:
    a = parse_args()
    issues: list[str] = []

    for p, label in ((a.itemdata, "itemdata"), (a.grid_catalog, "grid catalog"),
                     (a.worker, "worker"), (a.source_card, "source card")):
        if not p.is_file():
            issues.append(f"missing {label}: {p}")

    if issues:
        for x in issues:
            print(f"ERROR: {x}")
        raise SystemExit(2)

    actual_worker_sha = sha256(a.worker)
    if actual_worker_sha != a.expected_worker_sha:
        issues.append(
            f"worker sha mismatch: got={actual_worker_sha} expected={a.expected_worker_sha}"
        )

    catalog = load_catalog(a.grid_catalog)
    for g in EXPECTED:
        if g not in catalog:
            issues.append(f"grid catalog missing {g}")

    rows = []
    for line_no, raw in enumerate(a.itemdata.read_text().splitlines(), start=1):
        if not raw.strip():
            continue
        c = raw.split("\t")
        if len(c) != 10:
            issues.append(f"line {line_no}: expected 10 columns, got {len(c)}")
            continue
        mode, grid, kind, tar, vg2, phs, grid_seed, shard_seed, metadata_seed, events = c
        rows.append({
            "line": line_no,
            "mode": mode,
            "grid": grid,
            "kind": kind,
            "tar": tar,
            "vg2": vg2,
            "phs": phs,
            "grid_seed": grid_seed,
            "shard_seed": shard_seed,
            "metadata_seed": metadata_seed,
            "events": events,
        })

    if len(rows) != EXPECTED_TOTAL:
        issues.append(f"expected {EXPECTED_TOTAL} rows, got {len(rows)}")

    modes = [r["mode"] for r in rows]
    seeds = []
    if len(set(modes)) != len(modes):
        issues.append("duplicate mode names")

    counts = Counter(r["grid"] for r in rows)
    for grid in EXPECTED:
        if counts[grid] != EXPECTED_SHARDS:
            issues.append(f"{grid}: expected {EXPECTED_SHARDS} rows, got {counts[grid]}")

    for r in rows:
        grid = r["grid"]
        if grid not in EXPECTED or grid not in catalog:
            issues.append(f"line {r['line']}: unexpected grid {grid}")
            continue
        cat = catalog[grid]
        expected_idx = int(r["mode"][-2:]) if r["mode"][-2:].isdigit() else -1
        expected_mode_prefix = f"{grid}_GA"
        if not r["mode"].startswith(expected_mode_prefix) or not (1 <= expected_idx <= 20):
            issues.append(f"line {r['line']}: bad mode {r['mode']}")
        if r["kind"] != cat["checkpoint_kind"]:
            issues.append(f"{r['mode']}: checkpoint mismatch")
        if r["tar"] != cat["workspace_tar"]:
            issues.append(f"{r['mode']}: workspace tar mismatch")
        if not Path(r["tar"]).is_file():
            issues.append(f"{r['mode']}: workspace tar missing: {r['tar']}")
        if r["vg2"] != cat["vg2_sha256"]:
            issues.append(f"{r['mode']}: VG2 hash mismatch")
        if r["phs"] != cat["phs_sha256"]:
            issues.append(f"{r['mode']}: PHS hash mismatch")
        if r["grid_seed"] != cat["grid_construction_seed"]:
            issues.append(f"{r['mode']}: grid seed mismatch")
        try:
            seed = int(r["shard_seed"])
            meta = int(r["metadata_seed"])
            nev = int(r["events"])
        except ValueError:
            issues.append(f"{r['mode']}: non-integer seed/events field")
            continue
        seeds.append(seed)
        lo = EXPECTED[grid]["seed_start"]
        hi = EXPECTED[grid]["seed_end"]
        if not (lo <= seed <= hi):
            issues.append(f"{r['mode']}: shard seed {seed} outside [{lo},{hi}]")
        if expected_idx > 0 and seed != lo + expected_idx - 1:
            issues.append(f"{r['mode']}: seed does not match deterministic index")
        if meta != seed:
            issues.append(f"{r['mode']}: metadata seed != shard seed")
        if seed in PRIOR_VALIDATION_SEEDS:
            issues.append(f"{r['mode']}: seed collides with prior validation seed")
        if nev != EXPECTED_EVENTS:
            issues.append(f"{r['mode']}: events={nev}, expected {EXPECTED_EVENTS}")

    if len(set(seeds)) != len(seeds):
        issues.append("duplicate shard RNG seeds")

    if issues:
        print("C5GA_ITEMDATA_VALIDATION=FAIL")
        for x in issues:
            print(f"ERROR: {x}")
        raise SystemExit(2)

    print(f"C5GA_ROWS={len(rows)}")
    print(f"C5GA_S0_ROWS={counts['S0']}")
    print(f"C5GA_S1_ROWS={counts['S1']}")
    print(f"C5GA_S2_ROWS={counts['S2']}")
    print(f"C5GA_UNIQUE_SEEDS={len(set(seeds))}")
    print(f"C5GA_WORKER_SHA256={actual_worker_sha}")
    print("C5GA_ITEMDATA_VALIDATION=PASS")


if __name__ == "__main__":
    main()
