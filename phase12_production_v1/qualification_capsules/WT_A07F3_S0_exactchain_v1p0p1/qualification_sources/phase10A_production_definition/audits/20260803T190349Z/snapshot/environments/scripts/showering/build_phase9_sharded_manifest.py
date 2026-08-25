#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_jsonl(path: Path):
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ERROR: invalid JSON on {path}:{line_no}: {exc}") from exc
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", action="append", required=True)
    parser.add_argument("--events-per-shard", type=int, default=500)
    parser.add_argument("--shards-per-label", type=int, default=20)
    parser.add_argument("--base-seed", type=int, default=24700000)
    parser.add_argument("--iterations", default=None)
    parser.add_argument("--pythia-profile", default="parton_only", choices=["parton_only", "full_hadron"])
    args = parser.parse_args()

    source_records = load_jsonl(args.source_manifest)
    by_label = {record["label"]: record for record in source_records}

    missing = [label for label in args.label if label not in by_label]
    if missing:
        raise SystemExit(f"ERROR: missing source labels: {missing}")

    output_records = []

    for sample_index, parent_label in enumerate(args.label):
        base = by_label[parent_label]

        for shard_index in range(args.shards_per_label):
            suffix = f"s{shard_index:03d}"
            record = dict(base)

            record["schema_version"] = 1
            record["parent_label"] = parent_label
            record["label"] = f"{parent_label}_{suffix}"
            record["sample_id"] = f"{base['sample_id']}_{suffix}"
            record["shard_id"] = f"bridge_{args.events_per_shard}ev_{parent_label}_{suffix}"
            record["shard_index"] = shard_index
            record["n_shards"] = args.shards_per_label
            record["events"] = args.events_per_shard
            record["seed"] = args.base_seed + 1000 * sample_index + shard_index
            record["iterations"] = args.iterations if args.iterations is not None else base.get("iterations", "5:50000")
            record["pythia_profile"] = args.pythia_profile
            record["phase9_note"] = "Condor shard manifest for WHIZARD unweighting stability and parton-only bridge qualification"

            output_records.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as handle:
        for record in output_records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    print(f"WROTE={args.output}")
    print(f"RECORDS={len(output_records)}")
    for index, record in enumerate(output_records):
        print(
            f"{index:4d}  {record['label']:55s} "
            f"events={record['events']} seed={record['seed']} "
            f"profile={record['pythia_profile']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
