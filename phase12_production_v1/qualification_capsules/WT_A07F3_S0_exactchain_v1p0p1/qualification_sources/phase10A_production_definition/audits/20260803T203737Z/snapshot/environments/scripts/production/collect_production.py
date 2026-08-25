#!/usr/bin/env python3
"""Collect shard products and optionally merge LHE files per production sample."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import re
import tempfile
from pathlib import Path

from production_common import (
    campaign_root as default_campaign_root,
    count_lhe_events,
    default_output_root,
    ensure_eos,
    filter_configs,
    iter_lhe_event_blocks,
    open_text,
    read_configs,
    read_lhe_init,
    repo_root_from_script,
    sha256,
    utc_now,
    write_csv,
)

FIELDS = [
    "campaign_id", "sample_id", "source", "expected_shards", "collected_shards",
    "expected_events", "collected_events", "merged_lhe_path", "merged_lhe_sha256",
    "cross_section_pb", "cross_section_error_pb", "status", "updated_utc", "notes",
]


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script(__file__)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=root / "configs/production/production_500GeV_ISR_sc_v1.csv")
    p.add_argument("--campaign-root", type=Path, default=None)
    p.add_argument("--sample", action="append", default=[])
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--source", choices=("raw", "final"), default="final")
    p.add_argument("--merge", action="store_true", help="write one merged LHE per sample")
    p.add_argument("--gzip", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--allow-incomplete", action="store_true")
    p.add_argument("--allow-non-eos", action="store_true")
    return p.parse_args()


def load_csv_index(path: Path, key: str) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        return {row[key]: row for row in csv.DictReader(stream)}


def read_preamble(path: Path) -> list[str]:
    lines: list[str] = []
    with open_text(path) as stream:
        for line in stream:
            if line.lstrip().startswith("<event"):
                break
            lines.append(line)
    return lines


def patch_preamble(lines: list[str], events: int, xsec_pb: float, error_pb: float) -> list[str]:
    out: list[str] = []
    in_init = False
    numeric_line = 0
    for line in lines:
        stripped = line.strip()
        if stripped == "<init>":
            in_init = True
            numeric_line = 0
            out.append(line)
            continue
        if stripped == "</init>":
            in_init = False
            out.append(line)
            continue
        if in_init and stripped.startswith("<xsecinfo"):
            line = re.sub(r'neve="\d+"', f'neve="{events}"', line)
            line = re.sub(r'totxsec="[^"]+"', f'totxsec="{xsec_pb:.10E}"', line)
            out.append(line)
            continue
        if in_init and stripped and not stripped.startswith("<"):
            numeric_line += 1
            if numeric_line == 2:
                fields = line.split()
                fields[0] = f"{xsec_pb:.10E}"
                fields[1] = f"{error_pb:.10E}"
                out.append("  " + "  ".join(fields) + "\n")
                continue
        if stripped == "</LesHouchesEvents>":
            continue
        out.append(line)
    return out


def merge_lhe(files: list[Path], destination: Path, expected_events: int, xsec_pb: float, error_pb: float) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    out = gzip.open(tmp, "wt", encoding="utf-8") if destination.name.endswith(".gz") else tmp.open("w", encoding="utf-8")
    try:
        preamble = patch_preamble(read_preamble(files[0]), expected_events, xsec_pb, error_pb)
        with out:
            out.writelines(preamble)
            out.write(
                "<!-- merged by collect_production.py; "
                f"shards={len(files)} events={expected_events} created_utc={utc_now()} -->\n"
            )
            for path in files:
                for block in iter_lhe_event_blocks(path):
                    out.writelines(block)
            out.write("</LesHouchesEvents>\n")
        os.replace(tmp, destination)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    actual = count_lhe_events(destination)
    if actual != expected_events:
        destination.unlink(missing_ok=True)
        raise ValueError(f"merged event count mismatch for {destination}: {actual} != {expected_events}")
    init = read_lhe_init(destination)
    if abs(init.cross_section_pb - xsec_pb) > max(1e-12, abs(xsec_pb) * 1e-9):
        destination.unlink(missing_ok=True)
        raise ValueError(f"merged cross section mismatch in {destination}")


def main() -> int:
    args = parse_args()
    configs = filter_configs(read_configs(args.config), args.sample)
    campaign_id = configs[0].campaign_id
    campaign = args.campaign_root or default_campaign_root(default_output_root(), campaign_id, smoke=args.smoke)
    ensure_eos(campaign, allow_non_eos=args.allow_non_eos)
    manifests = campaign / "manifests"
    shard_path = manifests / "shard_manifest.csv"
    sample_path = manifests / "sample_manifest.csv"
    if not shard_path.exists() or not sample_path.exists():
        raise FileNotFoundError("run make_production_manifest.py before collection")
    with shard_path.open(newline="") as stream:
        shard_rows = list(csv.DictReader(stream))
    samples = load_csv_index(sample_path, "sample_id")

    results: list[dict[str, object]] = []
    for cfg in configs:
        expected_shards = 1 if args.smoke else cfg.n_shards
        rows = [row for row in shard_rows if row["sample_id"] == cfg.sample_id and row["status"] == "success"]
        key = "raw_lhe_path" if args.source == "raw" else "final_lhe_path"
        files = [Path(row[key]) for row in rows if row.get(key)]
        files = [path for path in files if path.exists()]
        files.sort()
        notes: list[str] = []
        status = "success"
        if len(files) != expected_shards:
            status = "incomplete"
            notes.append(f"found {len(files)}/{expected_shards} {args.source} LHE shards")
            if not args.allow_incomplete:
                raise ValueError(f"{cfg.sample_id}: {notes[-1]}")
        events = sum(count_lhe_events(path) for path in files)
        expected_events = sum(int(row["requested_events"]) for row in rows if row.get(key))
        sample_row = samples[cfg.sample_id]
        if args.source == "raw":
            xsec_fb = float(sample_row["inclusive_cross_section_fb"])
            error_fb = float(sample_row["inclusive_cross_section_error_fb"])
        else:
            if not sample_row.get("exclusive_cross_section_fb") or not sample_row.get("forced_decay_weight"):
                raise ValueError(f"{cfg.sample_id}: final normalization is absent; rerun manifest after calibration/finalization")
            xsec_fb = float(sample_row["exclusive_cross_section_fb"])
            error_fb = float(sample_row["inclusive_cross_section_error_fb"]) * float(sample_row["forced_decay_weight"])
        merged = campaign / "lhe_merged" / args.source / f"{cfg.sample_id}.lhe{'.gz' if args.gzip else ''}"
        if args.merge:
            if merged.exists() and not args.overwrite:
                if count_lhe_events(merged) != events:
                    raise FileExistsError(f"merged file exists with wrong event count: {merged}; use --overwrite")
                print(f"SKIP {merged} (already present)")
            else:
                merge_lhe(files, merged, events, xsec_fb / 1000.0, error_fb / 1000.0)
                print(f"WROTE {merged} events={events}")
        results.append({
            "campaign_id": campaign_id,
            "sample_id": cfg.sample_id,
            "source": args.source,
            "expected_shards": expected_shards,
            "collected_shards": len(files),
            "expected_events": expected_events,
            "collected_events": events,
            "merged_lhe_path": str(merged) if merged.exists() else "",
            "merged_lhe_sha256": sha256(merged) if merged.exists() else "",
            "cross_section_pb": f"{xsec_fb / 1000.0:.12g}",
            "cross_section_error_pb": f"{error_fb / 1000.0:.12g}",
            "status": status,
            "updated_utc": utc_now(),
            "notes": "; ".join(notes),
        })

    out_csv = manifests / f"collection_{args.source}.csv"
    write_csv(out_csv, FIELDS, results)
    out_md = manifests / f"collection_{args.source}.md"
    lines = [
        f"# WHIZARD production collection: {args.source}", "",
        f"- Campaign: `{campaign}`",
        f"- Samples: **{len(results)}**",
        f"- Complete: **{sum(row['status'] == 'success' for row in results)}**", "",
        "| Sample | Shards | Events | Merged LHE | Status |",
        "|---|---:|---:|---|---|",
    ]
    for row in results:
        lines.append(
            f"| `{row['sample_id']}` | {row['collected_shards']}/{row['expected_shards']} | "
            f"{row['collected_events']} | `{row['merged_lhe_path'] or '—'}` | **{row['status']}** |"
        )
    lines.append("")
    out_md.write_text("\n".join(lines))
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
