#!/usr/bin/env python3
"""Merge validated HepMC3 shower shards in deterministic source-event order."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> tuple[Path, int]:
    payload: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    root = Path(str(payload["campaign"]["output_root"])) / "shower"
    total_events = int(payload.get("showering", {}).get("total_events_per_sample", 10000))
    return root, total_events


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_info_signature(run_info: object) -> tuple[object, ...]:
    """Return a deterministic comparison signature for HepMC GenRunInfo."""
    if run_info is None:
        return ("none",)

    tools = tuple(
        (
            str(tool.name),
            str(tool.version),
            str(tool.description),
        )
        for tool in run_info.tools
    )

    weight_names = tuple(str(name) for name in run_info.weight_names)

    attributes: list[tuple[str, str]] = []
    try:
        keys = sorted(str(key) for key in run_info.attributes)
    except Exception:
        keys = []

    for key in keys:
        try:
            value = run_info.attributes[key]
            attributes.append((key, str(value)))
        except Exception as exc:
            attributes.append(
                (key, f"<unreadable:{type(exc).__name__}>")
            )

    return (
        "run_info",
        weight_names,
        tools,
        tuple(attributes),
    )


def merge_hepmc(inputs: list[Path], output: Path) -> int:
    """Merge shards using one verified canonical GenRunInfo object."""
    if not inputs:
        raise ValueError(f"no input HepMC3 files for {output.stem}")

    try:
        import pyhepmc
    except ImportError as exc:
        raise RuntimeError(
            "pyhepmc is required to merge HepMC3 files"
        ) from exc

    output.parent.mkdir(parents=True, exist_ok=True)

    temporary = output.with_name(
        f".{output.stem}.partial{output.suffix}"
    )
    temporary.unlink(missing_ok=True)

    events = 0
    canonical_run_info = None
    canonical_run_info_signature = None
    canonical_source: Path | None = None

    try:
        with pyhepmc.open(temporary, "w") as writer:
            for source in inputs:
                with pyhepmc.open(source) as reader:
                    for event in reader:
                        current_signature = run_info_signature(
                            event.run_info
                        )

                        if canonical_run_info_signature is None:
                            canonical_run_info = event.run_info
                            canonical_run_info_signature = (
                                current_signature
                            )
                            canonical_source = source
                        elif (
                            current_signature
                            != canonical_run_info_signature
                        ):
                            raise RuntimeError(
                                "incompatible GenRunInfo while merging "
                                f"{output.stem}: source={source}, "
                                f"canonical_source={canonical_source}, "
                                f"current={current_signature!r}, "
                                "canonical="
                                f"{canonical_run_info_signature!r}"
                            )

                        # All events in one merged HepMC stream must refer to
                        # the same run-info object, not merely equivalent
                        # objects loaded independently from each shard.
                        event.run_info = canonical_run_info
                        event.event_number = events

                        writer.write(event)
                        events += 1

        if not temporary.is_file():
            raise RuntimeError(
                f"missing merged temporary output: {temporary}"
            )

        if temporary.stat().st_size <= 0:
            raise RuntimeError(
                f"empty merged temporary output: {temporary}"
            )

        temporary.replace(output)

    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--shard-manifest", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    config_root, total_events_per_sample = load_config(args.config)
    root = args.root or config_root
    manifest_path = args.shard_manifest or root / "manifests/lhe_shard_manifest.csv"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    with manifest_path.open(newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("status") == "ready"]
    if not rows:
        raise ValueError(f"no ready rows in {manifest_path}")

    by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row)

    records: list[dict[str, object]] = []
    for sample, sample_rows in sorted(by_sample.items()):
        ordered = sorted(sample_rows, key=lambda row: int(row["shard_index"]))
        expected_indices = list(range(len(ordered)))
        indices = [int(row["shard_index"]) for row in ordered]
        if indices != expected_indices:
            raise ValueError(f"non-contiguous shard indices for {sample}: {indices}")
        starts = [int(row["source_event_start"]) for row in ordered]
        stops = [int(row["source_event_stop_exclusive"]) for row in ordered]
        if starts[0] != 0 or stops[-1] != total_events_per_sample:
            raise ValueError(f"incomplete source range for {sample}: [{starts[0]},{stops[-1]})")
        if any(stops[i] != starts[i + 1] for i in range(len(ordered) - 1)):
            raise ValueError(f"gap/overlap in source ranges for {sample}")

        inputs: list[Path] = []
        accepted_sum = 0
        for row in ordered:
            shard = row["shard_id"]
            requested = int(row["requested_events"])
            source = root / "hepmc3" / sample / f"{sample}__{shard}.hepmc3"
            metadata_path = root / "metadata" / sample / f"{sample}__{shard}.json"
            if not source.is_file() or source.stat().st_size <= 0:
                raise FileNotFoundError(source)
            if not metadata_path.is_file():
                raise FileNotFoundError(metadata_path)
            metadata = json.loads(metadata_path.read_text())
            accepted = int(metadata.get("accepted_events", 0))
            if metadata.get("status") != "success" or int(metadata.get("return_code", 1)) != 0:
                raise RuntimeError(f"invalid shower metadata for {sample}/{shard}")
            if accepted != requested:
                raise RuntimeError(
                    f"event-count mismatch for {sample}/{shard}: "
                    f"accepted={accepted} requested={requested}"
                )
            accepted_sum += accepted
            inputs.append(source)
        if accepted_sum != total_events_per_sample:
            raise RuntimeError(
                f"aggregate accepted count for {sample}: "
                f"{accepted_sum}, expected {total_events_per_sample}"
            )

        output = root / "hepmc3_merged" / f"{sample}.hepmc3"
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"merged output exists: {output}; use --overwrite")
        events = merge_hepmc(inputs, output)
        if events != total_events_per_sample:
            output.unlink(missing_ok=True)
            raise RuntimeError(
                f"merged event count for {sample}: {events}, "
                f"expected {total_events_per_sample}"
            )
        record = {
            "sample_id": sample,
            "shards": len(inputs),
            "source_event_start": starts[0],
            "source_event_stop_exclusive": stops[-1],
            "events": events,
            "inputs": [str(path) for path in inputs],
            "output": str(output),
            "output_sha256": sha256(output),
        }
        records.append(record)
        print(f"WROTE {output} shards={len(inputs)} events={events}")

    manifest_dir = root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_path = manifest_dir / "shower_collection.json"
    json_path.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
    csv_path = manifest_dir / "shower_collection.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "sample_id",
                "shards",
                "source_event_start",
                "source_event_stop_exclusive",
                "events",
                "output",
                "output_sha256",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow({key: record[key] for key in writer.fieldnames})
    md_path = manifest_dir / "shower_collection.md"
    md_path.write_text(
        "# Sharded shower collection\n\n"
        f"- Samples: **{len(records)}**\n"
        f"- Events per sample: **{total_events_per_sample}**\n\n"
        "| Sample | Shards | Events | Output |\n"
        "|---|---:|---:|---|\n"
        + "\n".join(
            f"| `{record['sample_id']}` | {record['shards']} | "
            f"{record['events']} | `{record['output']}` |"
            for record in records
        )
        + "\n"
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"SHOWER COLLECTION PASS samples={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
