#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ttbar_spinpol.genchain.seed_policy import derive_seed


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the canonical direct-full6f WHIZARD production "
            "manifest."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(os.environ.get("REPO", ".")).resolve(),
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path, required=True)

    parser.add_argument("--n-shards", type=int)
    parser.add_argument("--events-per-shard", type=int)
    parser.add_argument("--integration-iterations")
    parser.add_argument("--timeout-minutes", type=int)
    parser.add_argument("--archive-workspace", type=int, choices=[0, 1])

    parser.add_argument(
        "--stage",
        default="phase10_production_v1",
        help="Seed-policy stage name.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo = args.repo.resolve()
    config_path = args.config.resolve()
    output = args.output.resolve()
    campaign_root = args.campaign_root.resolve()

    config = load_json(config_path)

    campaign_id = str(config["campaign_id"])
    production_id = str(config["production_id"])
    defaults = config["production_defaults"]
    samples = config["samples"]

    n_shards = (
        args.n_shards
        if args.n_shards is not None
        else int(defaults["n_shards"])
    )
    events_per_shard = (
        args.events_per_shard
        if args.events_per_shard is not None
        else int(defaults["events_per_shard"])
    )
    integration_iterations = (
        args.integration_iterations
        if args.integration_iterations is not None
        else str(defaults["integration_iterations"])
    )
    timeout_minutes = (
        args.timeout_minutes
        if args.timeout_minutes is not None
        else int(defaults["timeout_minutes"])
    )
    archive_workspace = (
        args.archive_workspace
        if args.archive_workspace is not None
        else int(defaults["archive_workspace"])
    )

    if n_shards <= 0:
        raise SystemExit("ERROR: n_shards must be positive")

    if events_per_shard <= 0:
        raise SystemExit("ERROR: events_per_shard must be positive")

    records: list[dict[str, Any]] = []

    for sample_index, sample in enumerate(samples):
        sample_id = str(sample["sample_id"])
        subprocess_id = str(sample["subprocess_id"])
        polarization = str(sample["polarization"])

        source_card = Path(str(sample["source_card"]))

        if not source_card.is_absolute():
            source_card = repo / source_card

        source_card = source_card.resolve()

        if not source_card.is_file():
            raise SystemExit(
                f"ERROR: source card does not exist: {source_card}"
            )

        render_context = source_card.parent / "render_context.json"

        if not render_context.is_file():
            raise SystemExit(
                f"ERROR: missing render context: {render_context}"
            )

        source_card_sha256 = sha256(source_card)
        render_context_sha256 = sha256(render_context)

        for shard_index in range(n_shards):
            whizard_seed = derive_seed(
                campaign_id,
                sample_id,
                subprocess_id,
                args.stage,
                shard_index,
                "whizard",
            )

            record = {
                "schema_version": 1,
                "campaign_id": campaign_id,
                "production_id": production_id,
                "physics_mode": "direct_full_six_fermion",
                "sample_index": sample_index,
                "sample_id": sample_id,
                "subprocess_id": subprocess_id,
                "polarization": polarization,
                "source_card": str(source_card),
                "source_card_sha256": source_card_sha256,
                "render_context": str(render_context),
                "render_context_sha256": render_context_sha256,
                "shard_index": shard_index,
                "shard_label": f"shard_{shard_index:04d}",
                "n_shards": n_shards,
                "whizard_seed": int(whizard_seed),
                "events": events_per_shard,
                "integration_iterations": integration_iterations,
                "campaign_root": str(campaign_root),
                "archive_workspace": archive_workspace,
                "timeout_minutes": timeout_minutes,
                "request_cpus": int(defaults["request_cpus"]),
                "request_memory_mb": int(
                    defaults["request_memory_mb"]
                ),
                "request_disk_mb": int(
                    defaults["request_disk_mb"]
                ),
                "job_flavour": str(defaults["job_flavour"]),
                "seed_policy": {
                    "stage": args.stage,
                    "stream": "whizard",
                    "shard_index": shard_index,
                },
            }

            records.append(record)

    seeds = [record["whizard_seed"] for record in records]

    if len(seeds) != len(set(seeds)):
        raise SystemExit(
            "ERROR: duplicate WHIZARD seeds detected in manifest"
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(record, sort_keys=True) + "\n"
            )

    summary = {
        "schema_version": 1,
        "status": "PASS",
        "manifest": str(output),
        "manifest_sha256": sha256(output),
        "campaign_id": campaign_id,
        "production_id": production_id,
        "campaign_root": str(campaign_root),
        "n_samples": len(samples),
        "n_shards_per_sample": n_shards,
        "events_per_shard": events_per_shard,
        "events_per_sample": n_shards * events_per_shard,
        "total_records": len(records),
        "total_requested_events": (
            len(records) * events_per_shard
        ),
        "integration_iterations": integration_iterations,
        "seed_stage": args.stage,
        "samples": [
            {
                "sample_id": sample["sample_id"],
                "polarization": sample["polarization"],
            }
            for sample in samples
        ],
    }

    summary_path = output.with_suffix(
        output.suffix + ".summary.json"
    )
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("FULL6F_PRODUCTION_MANIFEST_BUILD_STATUS=PASS")
    print(f"MANIFEST={output}")
    print(f"SUMMARY={summary_path}")
    print(f"N_SAMPLES={len(samples)}")
    print(f"N_RECORDS={len(records)}")
    print(
        "TOTAL_REQUESTED_EVENTS="
        f"{len(records) * events_per_shard}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
