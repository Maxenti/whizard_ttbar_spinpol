#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EVENT_RE = re.compile(r"(?m)^\s*<event(?:\s|>)")
SEED_RE = re.compile(r"(?m)^\s*seed\s*=\s*(\d+)\s*$")
ITERATIONS_RE = re.compile(
    r"(?m)^\s*iterations\s*=\s*(.+?)\s*$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"{path}:{line_number}: invalid JSON: {exc}"
                ) from exc

    return rows


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect and certify direct-full6f WHIZARD shards."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--production-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--catalog-jsonl", type=Path, required=True)
    parser.add_argument("--recovery-manifest", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    manifest_path = args.manifest.resolve()
    root = args.production_root.resolve()

    records = read_jsonl(manifest_path)

    if not records:
        raise SystemExit("ERROR: production manifest is empty")

    shard_catalog: list[dict[str, Any]] = []
    recovery_records: list[dict[str, Any]] = []
    failures: list[str] = []

    sample_shards: Counter[str] = Counter()
    sample_events: Counter[str] = Counter()
    sample_bytes: Counter[str] = Counter()
    sample_seeds: dict[str, set[int]] = defaultdict(set)

    for expected in records:
        sample_id = str(expected["sample_id"])
        subprocess_id = str(expected["subprocess_id"])
        shard_index = int(expected["shard_index"])
        shard_label = str(
            expected.get(
                "shard_label",
                f"shard_{shard_index:04d}",
            )
        )

        run_dir = (
            root
            / "runs"
            / sample_id
            / subprocess_id
            / shard_label
        )

        lhe_path = (
            root
            / "lhe_raw"
            / sample_id
            / subprocess_id
            / f"{sample_id}__{subprocess_id}__{shard_label}.lhe"
        )

        paths = {
            "run_dir": run_dir,
            "success": run_dir / "SUCCESS",
            "metadata": run_dir / "run_metadata.json",
            "process": run_dir / "effective_process.sin",
            "integration": (
                run_dir / "effective_common" / "integration.inc"
            ),
            "event_output": (
                run_dir / "effective_common" / "event_output.inc"
            ),
            "console": run_dir / "console.log",
            "lhe": lhe_path,
        }

        shard_failures: list[str] = []

        for name, path in paths.items():
            if name == "run_dir":
                if not path.is_dir():
                    shard_failures.append(
                        f"missing directory: {path}"
                    )
            elif not path.is_file():
                shard_failures.append(
                    f"missing file {name}: {path}"
                )

        metadata: dict[str, Any] | None = None
        process = ""
        integration = ""
        console = ""
        event_count = 0
        lhe_hash = ""
        lhe_size = 0

        if paths["metadata"].is_file():
            try:
                metadata = json.loads(
                    paths["metadata"].read_text(
                        encoding="utf-8"
                    )
                )
            except Exception as exc:
                shard_failures.append(
                    f"invalid metadata JSON: {exc}"
                )

        if paths["process"].is_file():
            process = paths["process"].read_text(
                encoding="utf-8",
                errors="replace",
            )

        if paths["integration"].is_file():
            integration = paths["integration"].read_text(
                encoding="utf-8",
                errors="replace",
            )

        if paths["console"].is_file():
            console = paths["console"].read_text(
                encoding="utf-8",
                errors="replace",
            )

        if paths["lhe"].is_file():
            lhe_size = paths["lhe"].stat().st_size
            lhe_hash = sha256(paths["lhe"])

            event_count = len(
                EVENT_RE.findall(
                    paths["lhe"].read_text(
                        encoding="utf-8",
                        errors="replace",
                    )
                )
            )

        requested_seed = int(expected["whizard_seed"])
        requested_events = int(expected["events"])
        requested_iterations = str(
            expected["integration_iterations"]
        )
        expected_polarization = str(
            expected["polarization"]
        )

        checks: dict[str, bool] = {
            "success_marker": paths["success"].is_file(),
            "metadata_present": metadata is not None,
            "lhe_nonempty": (
                paths["lhe"].is_file()
                and lhe_size > 0
            ),
            "event_count": event_count == requested_events,
            "required_process_includes": all(
                f'include("common/{name}")' in process
                for name in (
                    "model.inc",
                    "beams.inc",
                    "isr.inc",
                    "integration.inc",
                    "event_output.inc",
                )
            ),
            "no_absolute_generated_include": (
                "/sindarin/generated/" not in process
            ),
            "polarization_include": (
                (
                    'include("common/polarization.inc")'
                    in process
                )
                == (expected_polarization != "unpol")
            ),
            "seed_effective": (
                SEED_RE.findall(integration)
                == [str(requested_seed)]
            ),
            "iterations_effective": (
                ITERATIONS_RE.findall(integration)
                == [requested_iterations]
            ),
            "whizard_finished": (
                "WHIZARD run finished." in console
            ),
        }

        if metadata is not None:
            checks.update(
                {
                    "metadata_status": (
                        metadata.get("status") == "success"
                    ),
                    "metadata_sample": (
                        metadata.get("sample_id") == sample_id
                    ),
                    "metadata_subprocess": (
                        metadata.get("subprocess_id")
                        == subprocess_id
                    ),
                    "metadata_shard": (
                        int(metadata.get("shard_index", -1))
                        == shard_index
                    ),
                    "metadata_events": (
                        int(metadata.get("generated_events", -1))
                        == requested_events
                    ),
                    "metadata_seed": (
                        metadata.get(
                            "random_streams",
                            {},
                        ).get("whizard_seed")
                        == requested_seed
                    ),
                    "metadata_whizard_version": (
                        "3.1.8"
                        in metadata.get(
                            "runtime",
                            {},
                        ).get("whizard_version", "")
                    ),
                    "metadata_lhe_hash": (
                        metadata.get("raw_lhe_sha256")
                        == lhe_hash
                    ),
                    "production_mode": (
                        metadata.get("production_mode")
                        == "direct_full_six_fermion"
                    ),
                }
            )

        failed_checks = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        shard_failures.extend(
            f"failed check: {name}"
            for name in failed_checks
        )

        status = "PASS" if not shard_failures else "FAIL"

        catalog_row = {
            "schema_version": 1,
            "status": status,
            "campaign_id": expected["campaign_id"],
            "production_id": expected["production_id"],
            "sample_id": sample_id,
            "polarization": expected_polarization,
            "subprocess_id": subprocess_id,
            "shard_index": shard_index,
            "shard_label": shard_label,
            "whizard_seed": requested_seed,
            "requested_events": requested_events,
            "generated_events": event_count,
            "integration_iterations": requested_iterations,
            "lhe_path": str(paths["lhe"]),
            "lhe_size_bytes": lhe_size,
            "lhe_sha256": lhe_hash,
            "run_directory": str(run_dir),
            "checks": checks,
            "failures": shard_failures,
        }

        shard_catalog.append(catalog_row)

        if status == "PASS":
            sample_shards[sample_id] += 1
            sample_events[sample_id] += event_count
            sample_bytes[sample_id] += lhe_size
            sample_seeds[sample_id].add(requested_seed)
        else:
            recovery_records.append(expected)

            failures.extend(
                f"{sample_id}/{shard_label}: {failure}"
                for failure in shard_failures
            )

    catalog_path = args.catalog_jsonl.resolve()
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    with catalog_path.open("w", encoding="utf-8") as handle:
        for row in shard_catalog:
            handle.write(
                json.dumps(row, sort_keys=True) + "\n"
            )

    recovery_path = args.recovery_manifest.resolve()
    recovery_path.parent.mkdir(parents=True, exist_ok=True)

    with recovery_path.open("w", encoding="utf-8") as handle:
        for row in recovery_records:
            handle.write(
                json.dumps(row, sort_keys=True) + "\n"
            )

    manifest_samples = sorted(
        {str(row["sample_id"]) for row in records}
    )

    sample_summary = {}

    for sample_id in manifest_samples:
        sample_summary[sample_id] = {
            "passing_shards": sample_shards[sample_id],
            "generated_events": sample_events[sample_id],
            "unique_seeds": len(sample_seeds[sample_id]),
            "total_lhe_bytes": sample_bytes[sample_id],
        }

    expected_total = len(records)
    passing_total = sum(
        row["status"] == "PASS"
        for row in shard_catalog
    )

    status = (
        "PASS"
        if passing_total == expected_total
        and not recovery_records
        else "FAIL"
    )

    payload = {
        "schema_version": 1,
        "status": status,
        "campaign_id": records[0]["campaign_id"],
        "production_id": records[0]["production_id"],
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "production_root": str(root),
        "expected_shards": expected_total,
        "passing_shards": passing_total,
        "failed_shards": len(recovery_records),
        "total_generated_events": sum(
            sample_events.values()
        ),
        "sample_summary": sample_summary,
        "catalog_jsonl": str(catalog_path),
        "recovery_manifest": str(recovery_path),
        "failures": failures,
    }

    output_path = args.output_json.resolve()
    write_json(output_path, payload)

    print(f"FULL6F_PRODUCTION_COLLECTION_STATUS={status}")
    print(f"EXPECTED_SHARDS={expected_total}")
    print(f"PASSING_SHARDS={passing_total}")
    print(f"FAILED_SHARDS={len(recovery_records)}")
    print(
        "TOTAL_GENERATED_EVENTS="
        f"{sum(sample_events.values())}"
    )

    for sample_id in manifest_samples:
        summary = sample_summary[sample_id]

        print(
            f"{sample_id}: "
            f"shards={summary['passing_shards']} "
            f"events={summary['generated_events']} "
            f"seeds={summary['unique_seeds']} "
            f"bytes={summary['total_lhe_bytes']}"
        )

    print(f"WROTE_AUDIT={output_path}")
    print(f"WROTE_CATALOG={catalog_path}")
    print(f"WROTE_RECOVERY_MANIFEST={recovery_path}")

    for failure in failures[:100]:
        print(f"FAILURE={failure}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
