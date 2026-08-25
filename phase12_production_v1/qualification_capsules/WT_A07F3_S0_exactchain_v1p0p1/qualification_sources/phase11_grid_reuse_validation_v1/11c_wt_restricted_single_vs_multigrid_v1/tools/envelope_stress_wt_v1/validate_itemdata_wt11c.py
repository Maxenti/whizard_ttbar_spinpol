#!/usr/bin/env python3

import argparse
import csv
import hashlib
import re
from pathlib import Path


MODE_RE = re.compile(r"^(S[012])_WTGA(0[1-9]|1[0-9]|20)$")

EXPECTED_SEED_BASE = {
    "S0": 311170000,
    "S1": 311171000,
    "S2": 311172000,
}

EXPECTED_EVENTS = 500
EXPECTED_ROWS_PER_GRID = 20
EXPECTED_TOTAL_ROWS = 60


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fail(errors):
    print("WT11C_ITEMDATA_VALIDATION=FAIL")
    for e in errors:
        print(f"ERROR: {e}")
    raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--itemdata", required=True)
    ap.add_argument("--grid-catalog", required=True)
    ap.add_argument("--worker", required=True)
    ap.add_argument("--expected-worker-sha", required=True)
    ap.add_argument("--source-card", required=True)

    args = ap.parse_args()

    itemdata = Path(args.itemdata)
    catalog_path = Path(args.grid_catalog)
    worker = Path(args.worker)
    source = Path(args.source_card)

    errors = []

    for p, label in [
        (itemdata, "itemdata"),
        (catalog_path, "grid catalog"),
        (worker, "worker"),
        (source, "source card"),
    ]:
        if not p.is_file():
            errors.append(f"missing {label}: {p}")

    if errors:
        fail(errors)

    actual_worker_sha = sha256(worker)

    if actual_worker_sha != args.expected_worker_sha:
        errors.append(
            "worker SHA mismatch: "
            f"expected={args.expected_worker_sha} "
            f"actual={actual_worker_sha}"
        )

    #
    # Confirm that this really is the WT restricted source.
    #
    source_text = source.read_text()

    required_source_tokens = [
        "?resonance_history = true",
        "resonance_on_shell_limit = 10",
        "resonance_background_factor = 0",
        '$restrictions = "5+6~W+ && 7+8~W- && 3+5+6~t && 4+7+8~tbar"',
    ]

    for token in required_source_tokens:
        if token not in source_text:
            errors.append(
                f"WT source missing required token: {token}"
            )

    #
    # Load frozen grid catalog.
    #
    with catalog_path.open(newline="") as f:
        catalog_rows = list(csv.DictReader(f, delimiter="\t"))

    catalog = {
        r["grid_label"]: r
        for r in catalog_rows
    }

    if set(catalog) != {"S0", "S1", "S2"}:
        errors.append(
            "grid catalog labels are not exactly S0,S1,S2: "
            f"{sorted(catalog)}"
        )

    #
    # itemdata.tsv intentionally has no header because Condor queue-from
    # consumes positional columns.
    #
    fields = [
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

    rows = []

    with itemdata.open(newline="") as f:
        reader = csv.reader(f, delimiter="\t")

        for lineno, values in enumerate(reader, start=1):
            if not values:
                continue

            if len(values) != len(fields):
                errors.append(
                    f"line {lineno}: expected {len(fields)} columns, "
                    f"found {len(values)}"
                )
                continue

            r = dict(zip(fields, values))
            r["_lineno"] = lineno
            rows.append(r)

    if len(rows) != EXPECTED_TOTAL_ROWS:
        errors.append(
            f"expected {EXPECTED_TOTAL_ROWS} rows, found {len(rows)}"
        )

    counts = {
        "S0": 0,
        "S1": 0,
        "S2": 0,
    }

    seen_modes = set()
    seen_seeds = set()

    for r in rows:
        lineno = r["_lineno"]
        mode = r["mode"]

        m = MODE_RE.fullmatch(mode)

        if not m:
            errors.append(
                f"line {lineno}: bad WT11C mode {mode}"
            )
            continue

        mode_grid = m.group(1)
        shard_index = int(m.group(2))

        grid = r["grid_label"]

        if grid != mode_grid:
            errors.append(
                f"{mode}: mode grid {mode_grid} != grid_label {grid}"
            )

        if grid not in counts:
            errors.append(
                f"{mode}: unexpected grid label {grid}"
            )
            continue

        counts[grid] += 1

        if mode in seen_modes:
            errors.append(f"duplicate mode: {mode}")
        seen_modes.add(mode)

        try:
            shard_seed = int(r["shard_rng_seed"])
            metadata_seed = int(r["metadata_seed"])
            grid_seed = int(r["grid_construction_seed"])
            events = int(r["events"])
        except ValueError as exc:
            errors.append(
                f"{mode}: integer parsing failure: {exc}"
            )
            continue

        expected_seed = EXPECTED_SEED_BASE[grid] + shard_index

        if shard_seed != expected_seed:
            errors.append(
                f"{mode}: shard seed {shard_seed} "
                f"!= deterministic expected {expected_seed}"
            )

        if metadata_seed != shard_seed:
            errors.append(
                f"{mode}: metadata_seed={metadata_seed} "
                f"!= shard_rng_seed={shard_seed}"
            )

        if shard_seed in seen_seeds:
            errors.append(
                f"{mode}: duplicate validation RNG seed {shard_seed}"
            )
        seen_seeds.add(shard_seed)

        if events != EXPECTED_EVENTS:
            errors.append(
                f"{mode}: events={events}, "
                f"expected {EXPECTED_EVENTS}"
            )

        if grid not in catalog:
            continue

        c = catalog[grid]

        comparisons = [
            ("checkpoint_kind", r["checkpoint_kind"],
             c["checkpoint_kind"]),
            ("workspace_tar", r["workspace_tar"],
             c["workspace_tar"]),
            ("vg2_sha256", r["vg2_sha256"],
             c["vg2_sha256"]),
            ("phs_sha256", r["phs_sha256"],
             c["phs_sha256"]),
        ]

        for field, got, expected in comparisons:
            if got != expected:
                errors.append(
                    f"{mode}: {field} mismatch: "
                    f"got={got!r} expected={expected!r}"
                )

        try:
            catalog_grid_seed = int(c["grid_construction_seed"])
        except ValueError:
            errors.append(
                f"{mode}: bad catalog grid-construction seed"
            )
            continue

        if grid_seed != catalog_grid_seed:
            errors.append(
                f"{mode}: grid construction seed {grid_seed} "
                f"!= catalog {catalog_grid_seed}"
            )

        workspace = Path(r["workspace_tar"])

        if not workspace.is_file():
            errors.append(
                f"{mode}: workspace tar missing: {workspace}"
            )

    for grid in ["S0", "S1", "S2"]:
        if counts[grid] != EXPECTED_ROWS_PER_GRID:
            errors.append(
                f"{grid}: expected {EXPECTED_ROWS_PER_GRID} rows, "
                f"found {counts[grid]}"
            )

    if len(seen_seeds) != EXPECTED_TOTAL_ROWS:
        errors.append(
            f"expected {EXPECTED_TOTAL_ROWS} unique shard seeds, "
            f"found {len(seen_seeds)}"
        )

    if errors:
        fail(errors)

    print(f"WT11C_ROWS={len(rows)}")
    print(f"WT11C_S0_ROWS={counts['S0']}")
    print(f"WT11C_S1_ROWS={counts['S1']}")
    print(f"WT11C_S2_ROWS={counts['S2']}")
    print(f"WT11C_UNIQUE_SEEDS={len(seen_seeds)}")
    print(f"WT11C_EVENTS_PER_JOB={EXPECTED_EVENTS}")
    print(
        f"WT11C_EVENTS_PER_GRID="
        f"{EXPECTED_EVENTS * EXPECTED_ROWS_PER_GRID}"
    )
    print(
        f"WT11C_TOTAL_EVENTS="
        f"{EXPECTED_EVENTS * EXPECTED_TOTAL_ROWS}"
    )
    print(f"WT11C_WORKER_SHA256={actual_worker_sha}")
    print("WT11C_SOURCE_RESTRICTION_CHECK=PASS")
    print("WT11C_ITEMDATA_VALIDATION=PASS")


if __name__ == "__main__":
    main()
