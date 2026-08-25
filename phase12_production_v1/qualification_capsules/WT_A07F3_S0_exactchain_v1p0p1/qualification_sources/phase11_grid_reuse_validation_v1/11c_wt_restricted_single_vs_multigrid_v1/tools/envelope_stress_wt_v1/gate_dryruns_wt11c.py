#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Gate all WT Phase-11C worker dry-runs.")
    p.add_argument("--itemdata", required=True, type=Path)
    p.add_argument("--dryrun-dir", required=True, type=Path)
    return p.parse_args()


def main():
    a = parse_args()
    failures = []
    n = 0
    for raw in a.itemdata.read_text().splitlines():
        if not raw.strip():
            continue
        c = raw.split("\t")
        mode, grid, kind, tar, vg2, phs, grid_seed, shard_seed, metadata_seed, events = c
        n += 1
        p = a.dryrun_dir / f"{mode}.dryrun.txt"
        if not p.is_file():
            failures.append(f"{mode}: missing dry-run output")
            continue
        text = p.read_text(errors="replace")
        pass_marker = "R0V2_DRY_RUN=PASS" in text
        preseed = f"seed = {shard_seed}" in text
        simulate = "simulate (proc_epmum)" in text
        event_match = re.search(r"===== EVENT_OUTPUT\.INC =====\n(.*)", text, flags=re.S)
        event_block = event_match.group(1) if event_match else ""
        explicit_post_seed = bool(re.search(r"(?m)^\s*seed\s*=", event_block))
        events_ok = bool(re.search(rf"(?m)^\s*n_events\s*=\s*{re.escape(events)}\s*$", event_block))
        ok = pass_marker and preseed and simulate and not explicit_post_seed and events_ok
        print(
            f"{mode}: dryrun={'PASS' if pass_marker else 'FAIL'} "
            f"seed={'PASS' if preseed else 'FAIL'} simulate={'PASS' if simulate else 'FAIL'} "
            f"events={'PASS' if events_ok else 'FAIL'} post_reseed={'ABSENT' if not explicit_post_seed else 'FAIL'} "
            f"OVERALL={'PASS' if ok else 'FAIL'}"
        )
        if not ok:
            failures.append(f"{mode}: dry-run gate failed")

    if n != 60:
        failures.append(f"expected 60 itemdata rows, got {n}")
    if failures:
        print("\nWT11C_DRYRUN_GATE=FAIL")
        for x in failures:
            print(f"ERROR: {x}")
        raise SystemExit(2)
    print("\nWT11C_DRYRUN_GATE=PASS")


if __name__ == "__main__":
    main()
