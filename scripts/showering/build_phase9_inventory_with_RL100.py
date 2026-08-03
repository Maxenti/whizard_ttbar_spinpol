#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"ERROR: failed to read JSON {path}: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception as exc:
                raise SystemExit(f"ERROR: bad JSONL line {lineno} in {path}: {exc}") from exc
    return out


def recursive_find_strings(obj: Any, predicate) -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for v in obj.values():
            found.extend(recursive_find_strings(v, predicate))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(recursive_find_strings(v, predicate))
    elif isinstance(obj, str):
        if predicate(obj):
            found.append(obj)
    return found


def first_existing_path(paths: list[str], suffix: str | None = None) -> str | None:
    for s in paths:
        if suffix is not None and not s.endswith(suffix):
            continue
        p = Path(s)
        if p.is_file():
            return str(p)
    return None


def extract_event_count(summary: dict[str, Any]) -> int:
    candidates = []

    def walk(obj: Any):
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).lower()
                if lk in {"hepmc", "canonical_lhe", "raw_lhe"} and isinstance(v, int):
                    candidates.append(v)
                if lk in {"event_counts", "counts"}:
                    walk(v)
                else:
                    walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(summary)

    if 500 in candidates:
        return 500

    positive = [x for x in candidates if isinstance(x, int) and x > 0]
    if positive:
        return max(set(positive), key=positive.count)

    return 500


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-inventory", required=True)
    ap.add_argument("--rl100-condor-out-dir", required=True)
    ap.add_argument("--rl100-summary-json", required=True)
    ap.add_argument("--output-jsonl", required=True)
    ap.add_argument("--summary-json", required=True)
    args = ap.parse_args()

    old_inventory = load_jsonl(Path(args.old_inventory))
    rl100_summary = load_json(Path(args.rl100_summary_json))
    condor_out = Path(args.rl100_condor_out_dir)

    summaries_dir = condor_out / "summaries"
    if not summaries_dir.is_dir():
        raise SystemExit(f"ERROR: missing summaries dir: {summaries_dir}")

    # Use copied per-job phase7 summaries because they contain the durable
    # run-product paths.
    summary_files = sorted(summaries_dir.glob("job_*_RL100_epmum_s*.phase7_bridge_summary.json"))
    if len(summary_files) != 20:
        raise SystemExit(f"ERROR: expected 20 RL100 phase7 summaries, found {len(summary_files)} in {summaries_dir}")

    new_records: list[dict[str, Any]] = []

    for sf in summary_files:
        s = load_json(sf)
        all_paths = recursive_find_strings(s, lambda x: x.startswith("/") or x.startswith("/eos/"))

        hepmc = first_existing_path(all_paths, ".hepmc3")
        canonical_lhe = first_existing_path(all_paths, ".canonical_v2.lhe")
        raw_lhe = first_existing_path(all_paths, "bridge_raw.lhe")

        if hepmc is None:
            raise SystemExit(f"ERROR: could not find existing .hepmc3 path in {sf}")

        label = sf.name
        # job_0_RL100_epmum_s000.phase7_bridge_summary.json -> RL100_epmum_s000
        if "_RL100_epmum_s" not in label:
            raise SystemExit(f"ERROR: unexpected RL100 summary filename: {sf.name}")
        label = label.split("_", 1)[1].replace(".phase7_bridge_summary.json", "")
        label = label.split("_RL100_epmum_s", 1)
        label = "RL100_epmum_s" + label[1]

        shard_index = int(label.rsplit("_s", 1)[1])
        events = extract_event_count(s)

        record = {
            "schema_version": 1,
            "campaign_id": "full6f_365gev_ee_ttbar_spinpol_v1",
            "parent_label": "RL100_epmum",
            "label": label,
            "category": "dilepton_polarized",
            "beam_polarization": "RL100",
            "events": events,
            "hepmc": hepmc,
            "canonical_lhe": canonical_lhe,
            "raw_lhe": raw_lhe,
            "source_phase7_summary": str(sf),
            "source_condor_out_dir": str(condor_out),
            "source_collect_summary": str(Path(args.rl100_summary_json)),
            "shard_index": shard_index,
            "n_shards": 20,
        }

        new_records.append(record)

    new_records.sort(key=lambda r: r["shard_index"])

    all_records = old_inventory + new_records

    out = Path(args.output_jsonl)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for r in all_records:
            handle.write(json.dumps(r, sort_keys=True) + "\n")

    records_by_parent = Counter(r.get("parent_label", "UNKNOWN") for r in all_records)
    events_by_parent = Counter()
    for r in all_records:
        events_by_parent[r.get("parent_label", "UNKNOWN")] += int(r.get("events", 0))

    summary = {
        "schema_version": 1,
        "status": "PASS",
        "old_inventory": str(Path(args.old_inventory)),
        "rl100_condor_out_dir": str(condor_out),
        "rl100_collect_summary": str(Path(args.rl100_summary_json)),
        "output_jsonl": str(out),
        "total_records": len(all_records),
        "total_events": sum(events_by_parent.values()),
        "records_by_parent_label": dict(sorted(records_by_parent.items())),
        "events_by_parent_label": dict(sorted(events_by_parent.items())),
        "added_records": len(new_records),
        "added_events": sum(int(r.get("events", 0)) for r in new_records),
        "added_parent_label": "RL100_epmum",
    }

    Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("UPDATED_INVENTORY_STATUS=PASS")
    print(f"TOTAL_RECORDS={summary['total_records']}")
    print(f"TOTAL_EVENTS={summary['total_events']}")
    print(f"ADDED_RECORDS={summary['added_records']}")
    print(f"ADDED_EVENTS={summary['added_events']}")
    print(f"WROTE_JSONL={out}")
    print(f"WROTE_SUMMARY={args.summary_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
