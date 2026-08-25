#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, default=None)
    args = parser.parse_args()

    records = load_jsonl(args.manifest)
    status_dir = args.out_dir / "status"

    rows = []
    failures = []

    for proc_id, record in enumerate(records):
        label = record["label"]
        candidates = sorted(status_dir.glob(f"job_{proc_id}_*.status.json"))

        if not candidates:
            row = {
                "proc_id": proc_id,
                "label": label,
                "parent_label": record.get("parent_label", label),
                "shard_index": record.get("shard_index", proc_id),
                "status": "MISSING",
                "runner_status": None,
                "return_code": None,
                "run_dir": None,
                "event_counts": None,
                "warning_counts": None,
                "job_log": None,
            }
            failures.append(row)
            rows.append(row)
            continue

        status = json.loads(candidates[-1].read_text(encoding="utf-8"))
        row = {
            "proc_id": proc_id,
            "label": label,
            "parent_label": status.get("parent_label"),
            "shard_index": status.get("shard_index"),
            "status": status.get("status"),
            "runner_status": status.get("runner_status"),
            "return_code": status.get("return_code"),
            "run_dir": status.get("run_dir"),
            "event_counts": status.get("event_counts"),
            "warning_counts": status.get("warning_counts"),
            "job_log": status.get("job_log"),
            "summary_copy": status.get("summary_copy"),
        }
        rows.append(row)

        if row["return_code"] != 0 or row["runner_status"] not in {"PASS", "PASS_WITH_RUNTIME_WARNINGS"}:
            failures.append(row)

    campaign_status = "PASS" if not failures else "FAIL"

    print(f"PHASE9_SHARD_COLLECT_STATUS={campaign_status}")
    print(f"TOTAL_RECORDS={len(records)}")
    print(f"FAILURES={len(failures)}")
    print()

    for row in rows:
        counts = row.get("event_counts") or {}
        print(
            f"{row['proc_id']:4d}  "
            f"{row['label']:60s}  "
            f"rc={row.get('return_code')}  "
            f"runner={row.get('runner_status')}  "
            f"raw={counts.get('raw_lhe')} "
            f"canon={counts.get('canonical_lhe')} "
            f"hepmc={counts.get('hepmc')}"
        )

        if row.get("return_code") != 0 or row.get("runner_status") not in {"PASS", "PASS_WITH_RUNTIME_WARNINGS"}:
            print(f"      log={row.get('job_log')}")
            print(f"      dir={row.get('run_dir')}")

    summary = {
        "status": campaign_status,
        "total_records": len(records),
        "failures": len(failures),
        "rows": rows,
    }

    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print()
        print(f"WROTE_SUMMARY_JSON={args.summary_json}")

    return 0 if campaign_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
