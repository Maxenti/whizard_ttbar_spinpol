#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SEED_RE = re.compile(r"(?m)^\s*seed\s*=\s*(\d+)\s*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"{path}:{line_number}: invalid JSON: {exc}"
                ) from exc

    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-samples", type=int, required=True)
    parser.add_argument(
        "--expected-shards-per-sample",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--expected-events-per-shard",
        type=int,
        required=True,
    )
    parser.add_argument("--output-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    manifest = args.manifest.resolve()
    records = load_jsonl(manifest)

    failures: list[str] = []
    checks: dict[str, bool] = {}

    required_fields = {
        "campaign_id",
        "production_id",
        "physics_mode",
        "sample_id",
        "subprocess_id",
        "polarization",
        "source_card",
        "source_card_sha256",
        "shard_index",
        "whizard_seed",
        "events",
        "integration_iterations",
        "campaign_root",
        "archive_workspace",
        "timeout_minutes",
        "request_cpus",
        "request_memory_mb",
        "request_disk_mb",
        "job_flavour",
    }

    expected_records = (
        args.expected_samples
        * args.expected_shards_per_sample
    )

    checks["record_count"] = len(records) == expected_records

    if not checks["record_count"]:
        failures.append(
            f"record count {len(records)} != {expected_records}"
        )

    sample_counts: Counter[str] = Counter()
    shard_indices: dict[str, list[int]] = defaultdict(list)
    seeds: list[int] = []
    sample_polarizations: dict[str, str] = {}

    for index, record in enumerate(records):
        missing = required_fields - set(record)

        if missing:
            failures.append(
                f"record {index}: missing fields {sorted(missing)}"
            )
            continue

        sample_id = str(record["sample_id"])
        source_card = Path(record["source_card"])

        sample_counts[sample_id] += 1
        shard_indices[sample_id].append(
            int(record["shard_index"])
        )
        seeds.append(int(record["whizard_seed"]))
        sample_polarizations[sample_id] = str(
            record["polarization"]
        )

        if record["physics_mode"] != "direct_full_six_fermion":
            failures.append(
                f"record {index}: wrong physics_mode"
            )

        if int(record["events"]) != args.expected_events_per_shard:
            failures.append(
                f"record {index}: event count mismatch"
            )

        if not source_card.is_file():
            failures.append(
                f"record {index}: source card missing: "
                f"{source_card}"
            )
            continue

        if sha256(source_card) != record["source_card_sha256"]:
            failures.append(
                f"record {index}: source-card hash mismatch"
            )

        process_text = source_card.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if "=> b, bbar," not in process_text:
            failures.append(
                f"record {index}: source card is not direct full6f"
            )

        integration = (
            source_card.parent / "common" / "integration.inc"
        )

        if not integration.is_file():
            failures.append(
                f"record {index}: missing integration include"
            )
        else:
            integration_text = integration.read_text(
                encoding="utf-8",
                errors="replace",
            )

            seed_matches = SEED_RE.findall(integration_text)

            if len(seed_matches) != 1:
                failures.append(
                    f"record {index}: baseline seed count "
                    f"{len(seed_matches)} != 1"
                )

            if "integrate (" not in integration_text:
                failures.append(
                    f"record {index}: no integrate statement"
                )

            if seed_matches and (
                integration_text.index(
                    f"seed = {seed_matches[0]}"
                )
                >= integration_text.index("integrate (")
            ):
                failures.append(
                    f"record {index}: baseline seed is after "
                    "integration"
                )

    checks["sample_count"] = (
        len(sample_counts) == args.expected_samples
    )
    checks["sample_shard_counts"] = all(
        count == args.expected_shards_per_sample
        for count in sample_counts.values()
    )
    checks["shard_index_coverage"] = all(
        sorted(indices)
        == list(range(args.expected_shards_per_sample))
        for indices in shard_indices.values()
    )
    checks["seeds_unique"] = len(seeds) == len(set(seeds))
    checks["polarization_triad"] = (
        set(sample_polarizations.values())
        == {"unpol", "LR100", "RL100"}
    )
    checks["all_record_checks"] = not failures

    status = (
        "PASS"
        if all(checks.values()) and not failures
        else "FAIL"
    )

    payload = {
        "schema_version": 1,
        "status": status,
        "manifest": str(manifest),
        "manifest_sha256": sha256(manifest),
        "expected": {
            "samples": args.expected_samples,
            "shards_per_sample": (
                args.expected_shards_per_sample
            ),
            "events_per_shard": (
                args.expected_events_per_shard
            ),
            "records": expected_records,
        },
        "observed": {
            "records": len(records),
            "sample_counts": dict(sample_counts),
            "sample_polarizations": sample_polarizations,
            "unique_seeds": len(set(seeds)),
        },
        "checks": checks,
        "failures": failures,
    }

    output = args.output_json.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    for name, passed in checks.items():
        print(f"{name}={'PASS' if passed else 'FAIL'}")

    for failure in failures[:30]:
        print(f"FAILURE={failure}")

    print(f"FULL6F_PRODUCTION_MANIFEST_VALIDATION={status}")
    print(f"N_RECORDS={len(records)}")
    print(f"N_UNIQUE_SEEDS={len(set(seeds))}")
    print(f"WROTE={output}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
