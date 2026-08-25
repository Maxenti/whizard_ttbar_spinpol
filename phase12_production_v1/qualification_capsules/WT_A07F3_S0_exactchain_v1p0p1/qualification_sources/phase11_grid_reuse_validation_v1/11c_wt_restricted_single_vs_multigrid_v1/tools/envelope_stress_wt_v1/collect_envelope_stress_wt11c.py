#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

# FROZEN Phase 11C.5G-A decision constants.
EXPECTED_GRIDS = ("S0", "S1", "S2")
EXPECTED_SHARDS_PER_GRID = 20
EXPECTED_EVENTS_PER_SHARD = 500
EXPECTED_EVENTS_PER_GRID = 10_000
EXPECTED_TOTAL_EVENTS = 30_000
MAX_EXCESS_FRACTION = 0.01     # <= 1.0%
MAX_AGGREGATE_AVG_EXCESS = 0.01
MAX_GLOBAL_EVENT_EXCESS = 10.0
EXPECTED_FINAL_STATE = tuple(sorted((-14, -11, -5, 5, 12, 13, 22, 22)))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect/freeze Phase 11C.5G-A envelope stress results.")
    p.add_argument("--itemdata", required=True, type=Path)
    p.add_argument("--output-root", required=True, type=Path)
    p.add_argument("--outdir", required=True, type=Path)
    p.add_argument("--audit-lhe", action="store_true", help="Audit LHE count, unit weights, final state, and exact duplicates.")
    return p.parse_args()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def read_itemdata(path: Path) -> list[dict[str, str]]:
    rows = []
    for n, raw in enumerate(path.read_text().splitlines(), start=1):
        if not raw.strip():
            continue
        c = raw.split("\t")
        if len(c) != 10:
            raise SystemExit(f"ERROR: itemdata line {n}: expected 10 columns, got {len(c)}")
        rows.append(dict(zip(
            ("mode", "grid", "kind", "workspace_tar", "vg2", "phs", "grid_seed", "shard_seed", "metadata_seed", "events"), c
        )))
    return rows


def read_key_values(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.is_file():
        return vals
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    return vals


def first_text(paths: list[Path]) -> str:
    parts = []
    for p in paths:
        if p.is_file():
            parts.append(p.read_text(errors="replace"))
    return "\n".join(parts)


def parse_generation_diag(text: str) -> tuple[float | None, int | None, float | None, float | None]:
    eff_m = re.search(r"actual unweighting efficiency\s*=\s*([0-9.+\-Ee]+)\s*%", text, re.I)
    exc_m = re.search(r"Encountered events with excess weight:\s*(\d+)\s+events", text, re.I)
    max_m = re.search(r"Maximum excess weight\s*=\s*([0-9.+\-Ee]+)", text, re.I)
    avg_m = re.search(r"Average excess weight\s*=\s*([0-9.+\-Ee]+)", text, re.I)
    eff = float(eff_m.group(1)) if eff_m else None
    if exc_m:
        n_exc = int(exc_m.group(1))
        max_exc = float(max_m.group(1)) if max_m else None
        avg_exc = float(avg_m.group(1)) if avg_m else None
    else:
        # If no warning exists and the sample completed, WHIZARD had zero excess events.
        n_exc = 0
        max_exc = 0.0
        avg_exc = 0.0
    return eff, n_exc, max_exc, avg_exc


def audit_lhe(path: Path) -> dict:
    events = 0
    weights: list[float] = []
    signatures = Counter()
    event_hashes: list[str] = []
    issues: list[str] = []
    inside = False
    block: list[str] = []

    def process(lines: list[str], idx: int) -> None:
        payload = [x.strip() for x in lines if x.strip() and not x.lstrip().startswith("#")]
        if not payload:
            issues.append(f"event {idx}: empty event")
            return
        try:
            header = payload[0].split()
            nup = int(header[0])
            w = float(header[2])
            particles = payload[1:nup + 1]
            if len(particles) != nup:
                issues.append(f"event {idx}: NUP={nup}, particle_lines={len(particles)}")
                return
            pdgs = []
            for line in particles:
                c = line.split()
                if int(c[1]) == 1:
                    pdgs.append(int(c[0]))
            weights.append(w)
            signatures[tuple(sorted(pdgs))] += 1
            normalized = "<event>\n" + "".join(lines) + "</event>\n"
            event_hashes.append(hashlib.sha256(normalized.encode()).hexdigest())
        except Exception as exc:
            issues.append(f"event {idx}: {exc}")

    with path.open(errors="replace") as f:
        for raw in f:
            s = raw.strip()
            if s.startswith("<event"):
                inside = True
                block = []
                continue
            if s.startswith("</event"):
                events += 1
                process(block, events)
                inside = False
                block = []
                continue
            if inside:
                block.append(raw)

    return {
        "events": events,
        "weights": weights,
        "signatures": signatures,
        "hashes": event_hashes,
        "issues": issues,
        "unique_events": len(set(event_hashes)),
        "unit_weights": len(weights) == events and all(w == 1.0 for w in weights),
        "final_state_ok": signatures == Counter({EXPECTED_FINAL_STATE: events}) if events else False,
    }


def as_float_or_nan(v):
    return float(v) if v is not None else math.nan


def main() -> None:
    a = parse_args()
    rows = read_itemdata(a.itemdata)
    a.outdir.mkdir(parents=True, exist_ok=True)

    structural_issues: list[tuple[str, str]] = []
    shard_rows: list[dict] = []
    all_event_hashes: list[tuple[str, str]] = []
    raw_files_to_hash: list[Path] = [a.itemdata]

    for r in rows:
        mode = r["mode"]
        d = a.output_root / mode
        issues: list[str] = []
        reuse = d / "reuse_checks.txt"
        diag = d / "generation_diagnostics.txt"
        console = d / "console.log"
        rngprobe = d / "rng_seed_probe.txt"
        marker = d / "REUSE_PASS"

        for p in (reuse, diag, console, rngprobe):
            if p.is_file():
                raw_files_to_hash.append(p)

        vals = read_key_values(reuse)
        expected_events = int(r["events"])
        required = {
            "STATUS": "PASS",
            "WHIZARD_RC": "0",
            "EVENTS_REQUESTED": str(expected_events),
            "EVENTS_WRITTEN": str(expected_events),
            "WORKSPACE_UNCHANGED": "1",
            "NEW_GRID_INIT_COUNT": "0",
            "GRID_SEED": r["grid_seed"],
            "PHS_SHA256_BEFORE": r["phs"],
            "PHS_SHA256_AFTER": r["phs"],
            "VG2_SHA256_BEFORE": r["vg2"],
            "VG2_SHA256_AFTER": r["vg2"],
        }
        if not marker.is_file():
            issues.append("missing REUSE_PASS")
        if not reuse.is_file():
            issues.append("missing reuse_checks.txt")
        for k, want in required.items():
            if vals.get(k) != want:
                issues.append(f"{k}: got={vals.get(k)!r} expected={want!r}")

        rng_text = rngprobe.read_text(errors="replace") if rngprobe.is_file() else ""
        if f"PRE_INTEGRATION_RNG_SEED={r['shard_seed']}" not in rng_text:
            issues.append("wrong/missing PRE_INTEGRATION_RNG_SEED")

        text = first_text([diag, console])
        eff, n_exc, max_exc, avg_exc = parse_generation_diag(text)
        if eff is None:
            issues.append("could not parse actual unweighting efficiency")
        if n_exc is None or max_exc is None or avg_exc is None:
            issues.append("could not parse excess diagnostics")

        lhe_paths = sorted(d.glob("*.lhe"))
        lhe = lhe_paths[0] if len(lhe_paths) == 1 else None
        lhe_audit = None
        if len(lhe_paths) != 1:
            issues.append(f"expected exactly one LHE, found {len(lhe_paths)}")
        elif a.audit_lhe:
            raw_files_to_hash.append(lhe)
            lhe_audit = audit_lhe(lhe)
            if lhe_audit["events"] != expected_events:
                issues.append(f"LHE events={lhe_audit['events']}, expected={expected_events}")
            if lhe_audit["issues"]:
                issues.append(f"LHE parse issues={len(lhe_audit['issues'])}")
            if lhe_audit["unique_events"] != expected_events:
                issues.append(f"LHE unique events={lhe_audit['unique_events']}, expected={expected_events}")
            if not lhe_audit["unit_weights"]:
                issues.append("LHE unit weights FAIL")
            if not lhe_audit["final_state_ok"]:
                issues.append("LHE final state FAIL")
            all_event_hashes.extend((h, mode) for h in lhe_audit["hashes"])

        technical_pass = not issues
        for issue in issues:
            structural_issues.append((mode, issue))

        n_events_written = int(vals.get("EVENTS_WRITTEN", "0")) if vals.get("EVENTS_WRITTEN", "").isdigit() else 0
        sum_excess = (avg_exc * n_events_written) if (avg_exc is not None) else math.nan

        shard_rows.append({
            "mode": mode,
            "grid": r["grid"],
            "shard_seed": int(r["shard_seed"]),
            "events": n_events_written,
            "technical_pass": technical_pass,
            "efficiency_percent": eff,
            "excess_events": n_exc,
            "excess_fraction": (n_exc / n_events_written) if (n_exc is not None and n_events_written > 0) else math.nan,
            "max_excess": max_exc,
            "avg_excess": avg_exc,
            "sum_excess": sum_excess,
            "lhe": str(lhe) if lhe else "",
        })

    # Global exact-event duplicate audit.
    duplicate_pairs: list[tuple[str, str, str]] = []
    if a.audit_lhe:
        seen: dict[str, str] = {}
        for h, mode in all_event_hashes:
            if h in seen:
                duplicate_pairs.append((h, seen[h], mode))
            else:
                seen[h] = mode
        if duplicate_pairs:
            for h, a_mode, b_mode in duplicate_pairs[:1000]:
                structural_issues.append(("GLOBAL", f"duplicate event hash {h}: {a_mode} vs {b_mode}"))

    # Write shard metrics.
    shard_path = a.outdir / "shard_metrics.tsv"
    shard_fields = [
        "mode", "grid", "shard_seed", "events", "technical_pass",
        "efficiency_percent", "excess_events", "excess_fraction",
        "max_excess", "avg_excess", "sum_excess", "lhe",
    ]
    with shard_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=shard_fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in shard_rows:
            w.writerow(r)

    issues_path = a.outdir / "structural_issues.tsv"
    with issues_path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["mode", "issue"])
        w.writerows(structural_issues)

    grouped = defaultdict(list)
    for r in shard_rows:
        grouped[r["grid"]].append(r)

    grid_rows: list[dict] = []
    for grid in EXPECTED_GRIDS:
        rr = sorted(grouped.get(grid, []), key=lambda x: x["mode"])
        tech = len(rr) == EXPECTED_SHARDS_PER_GRID and all(x["technical_pass"] for x in rr)
        total_events = sum(x["events"] for x in rr)
        excess_events = sum(int(x["excess_events"] or 0) for x in rr)
        sum_excess = sum(float(x["sum_excess"]) for x in rr if math.isfinite(float(x["sum_excess"])))
        max_values = [float(x["max_excess"]) for x in rr if x["max_excess"] is not None]
        eff_values = [float(x["efficiency_percent"]) for x in rr if x["efficiency_percent"] is not None]
        excess_fraction = excess_events / total_events if total_events else math.nan
        avg_excess = sum_excess / total_events if total_events else math.nan
        global_max = max(max_values) if max_values else math.nan

        gate_count = len(rr) == EXPECTED_SHARDS_PER_GRID
        gate_events = total_events == EXPECTED_EVENTS_PER_GRID
        gate_fraction = math.isfinite(excess_fraction) and excess_fraction <= MAX_EXCESS_FRACTION
        gate_avg = math.isfinite(avg_excess) and avg_excess <= MAX_AGGREGATE_AVG_EXCESS
        gate_max = math.isfinite(global_max) and global_max <= MAX_GLOBAL_EVENT_EXCESS
        grid_gate = tech and gate_count and gate_events and gate_fraction and gate_avg and gate_max

        grid_rows.append({
            "grid": grid,
            "n_shards": len(rr),
            "technical_pass": tech,
            "total_events": total_events,
            "excess_events": excess_events,
            "excess_fraction": excess_fraction,
            "aggregate_avg_excess": avg_excess,
            "global_max_excess": global_max,
            "efficiency_min_percent": min(eff_values) if eff_values else math.nan,
            "efficiency_median_percent": statistics.median(eff_values) if eff_values else math.nan,
            "efficiency_mean_percent": statistics.fmean(eff_values) if eff_values else math.nan,
            "efficiency_max_percent": max(eff_values) if eff_values else math.nan,
            "gate_shard_count": gate_count,
            "gate_event_count": gate_events,
            "gate_excess_fraction": gate_fraction,
            "gate_aggregate_avg_excess": gate_avg,
            "gate_global_max_excess": gate_max,
            "grid_gate": grid_gate,
        })

    grid_path = a.outdir / "grid_aggregate.tsv"
    grid_fields = list(grid_rows[0].keys())
    with grid_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=grid_fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(grid_rows)

    total_events_all = sum(r["total_events"] for r in grid_rows)
    all_technical = all(r["technical_pass"] for r in grid_rows)
    all_grid_pass = all(r["grid_gate"] for r in grid_rows)
    s0_pass = next(r["grid_gate"] for r in grid_rows if r["grid"] == "S0")
    refs_pass = all(r["grid_gate"] for r in grid_rows if r["grid"] in ("S1", "S2"))

    if not all_technical or total_events_all != EXPECTED_TOTAL_EVENTS or structural_issues:
        status = "INCOMPLETE_TECHNICAL"
        rc = 3
        next_action = "Rerun only technical-failure modes with the SAME mode/grid/seed; do not substitute RNG seeds."
    elif all_grid_pass:
        status = "PASS_ALL_GRIDS"
        rc = 0
        next_action = "Freeze C5G-A PASS and build a fresh C5R holdout using new validation-only seeds; do not reuse stress events for physics."
    elif s0_pass and not refs_pass:
        status = "FAIL_REFERENCE_ONLY"
        rc = 2
        next_action = "Retain G2_S0 candidate; S1/S2 are not qualified references. Build a predetermined fresh-reference-grid qualification stage before any new holdout."
    elif not s0_pass:
        status = "FAIL_PRODUCTION_CANDIDATE"
        rc = 2
        next_action = "G2_S0 is not generation-envelope qualified. Revisit integration/envelope prescription before C5R or Phase12."
    else:
        status = "FAIL_ENVELOPE"
        rc = 2
        next_action = "Investigate failing grid envelope(s); do not cherry-pick replacement shards."

    result = {
        "phase": "11C.5G-A",
        "status": status,
        "thresholds": {
            "max_excess_fraction": MAX_EXCESS_FRACTION,
            "max_aggregate_avg_excess": MAX_AGGREGATE_AVG_EXCESS,
            "max_global_event_excess": MAX_GLOBAL_EVENT_EXCESS,
        },
        "expected": {
            "shards_per_grid": EXPECTED_SHARDS_PER_GRID,
            "events_per_shard": EXPECTED_EVENTS_PER_SHARD,
            "events_per_grid": EXPECTED_EVENTS_PER_GRID,
            "total_events": EXPECTED_TOTAL_EVENTS,
        },
        "audit_lhe": a.audit_lhe,
        "total_events": total_events_all,
        "global_unique_events": len(set(h for h, _ in all_event_hashes)) if a.audit_lhe else None,
        "duplicate_event_hashes": len(duplicate_pairs) if a.audit_lhe else None,
        "grids": grid_rows,
        "next_action": next_action,
    }

    (a.outdir / "WT11C_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (a.outdir / "WT11C_RESULT.txt").open("w") as f:
        f.write("Phase 11C.5G-A generation-envelope stress result\n")
        f.write("================================================\n\n")
        f.write(f"WT11C_STATUS={status}\n")
        f.write(f"WT11C_TOTAL_EVENTS={total_events_all}\n")
        if a.audit_lhe:
            f.write(f"WT11C_GLOBAL_UNIQUE_EVENTS={result['global_unique_events']}\n")
            f.write(f"WT11C_DUPLICATE_EVENT_HASHES={result['duplicate_event_hashes']}\n")
        f.write("\nFrozen aggregate gates:\n")
        f.write(f"  excess_fraction <= {MAX_EXCESS_FRACTION}\n")
        f.write(f"  aggregate_avg_excess <= {MAX_AGGREGATE_AVG_EXCESS}\n")
        f.write(f"  global_max_excess <= {MAX_GLOBAL_EVENT_EXCESS}\n\n")
        for g in grid_rows:
            f.write(
                f"{g['grid']}: gate={'PASS' if g['grid_gate'] else 'FAIL'} "
                f"technical={'PASS' if g['technical_pass'] else 'FAIL'} "
                f"events={g['total_events']} excess_events={g['excess_events']} "
                f"excess_fraction={g['excess_fraction']:.8g} "
                f"aggregate_avg_excess={g['aggregate_avg_excess']:.8g} "
                f"global_max_excess={g['global_max_excess']:.8g}\n"
            )
        f.write("\nNext action:\n")
        f.write(f"  {next_action}\n")

    # Raw-input SHA manifest for audit reproducibility.
    sha_path = a.outdir / "RAW_INPUTS.sha256"
    unique_paths = sorted({p.resolve() for p in raw_files_to_hash if p.is_file()}, key=str)
    with sha_path.open("w") as f:
        for p in unique_paths:
            f.write(f"{file_sha256(p)}  {p}\n")

    # Output SHA manifest excludes itself.
    out_sha = a.outdir / "RESULT_OUTPUTS.sha256"
    output_files = [shard_path, grid_path, issues_path, a.outdir / "WT11C_RESULT.json", a.outdir / "WT11C_RESULT.txt", sha_path]
    with out_sha.open("w") as f:
        for p in output_files:
            f.write(f"{file_sha256(p)}  {p}\n")

    print(f"WT11C_STATUS={status}")
    for g in grid_rows:
        print(
            f"{g['grid']}: gate={'PASS' if g['grid_gate'] else 'FAIL'} "
            f"technical={'PASS' if g['technical_pass'] else 'FAIL'} "
            f"events={g['total_events']} "
            f"excess_fraction={g['excess_fraction']:.6f} "
            f"avg_excess={g['aggregate_avg_excess']:.6f} "
            f"max_excess={g['global_max_excess']:.6g}"
        )
    if a.audit_lhe:
        print(f"WT11C_GLOBAL_UNIQUE_EVENTS={result['global_unique_events']}")
        print(f"WT11C_DUPLICATE_EVENT_HASHES={result['duplicate_event_hashes']}")
    print(f"WT11C_NEXT_ACTION={next_action}")
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
