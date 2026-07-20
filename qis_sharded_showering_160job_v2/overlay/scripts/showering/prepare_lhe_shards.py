#!/usr/bin/env python3
"""Create deterministic, disjoint LHE input shards for shower qualification.

Only the requested leading event window is read from each authoritative merged
LHE file.  Unused source events are never copied, canonicalized, or passed to
PYTHIA.  Every shard carries an explicit half-open source-event range and a
SHA256 checksum in ``manifests/lhe_shard_manifest.csv``.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import fnmatch
import gzip
import hashlib
import json
import os
import re
import shutil
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, TextIO

import yaml

MANIFEST_FIELDS = [
    "schema_version",
    "campaign_id",
    "sample_id",
    "source_lhe_path",
    "source_size_bytes",
    "source_mtime_ns",
    "selected_event_window_sha256",
    "shard_id",
    "shard_index",
    "source_event_start",
    "source_event_stop_exclusive",
    "requested_events",
    "shard_lhe_path",
    "shard_lhe_size_bytes",
    "shard_lhe_sha256",
    "status",
    "created_utc",
]


@dataclass(frozen=True)
class ShardPlan:
    index: int
    start: int
    stop: int

    @property
    def shard_id(self) -> str:
        return f"shard_{self.index:04d}"

    @property
    def events(self) -> int:
        return self.stop - self.start


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text()) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"configuration root must be a mapping: {path}")
    return payload


def open_text(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="strict", newline="")
    return path.open("r", encoding="utf-8", errors="strict", newline="")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def balanced_plan(total_events: int, shards: int) -> list[ShardPlan]:
    if total_events <= 0:
        raise ValueError("total_events must be positive")
    if shards <= 0:
        raise ValueError("shards must be positive")
    if shards > total_events:
        raise ValueError(
            f"cannot create {shards} non-empty shards from {total_events} events"
        )
    base, remainder = divmod(total_events, shards)
    plans: list[ShardPlan] = []
    start = 0
    for index in range(shards):
        count = base + (1 if index < remainder else 0)
        stop = start + count
        plans.append(ShardPlan(index=index, start=start, stop=stop))
        start = stop
    assert start == total_events
    return plans


def rewrite_prefix(prefix: str, event_count: int) -> str:
    rewritten = re.sub(
        r'(<xsecinfo\b[^>]*\bneve=")[^"]*(")',
        rf"\g<1>{event_count}\g<2>",
        prefix,
        count=1,
    )
    if not rewritten.endswith("\n"):
        rewritten += "\n"
    return rewritten


def existing_rows_valid(
    rows: list[dict[str, str]],
    *,
    source: Path,
    plans: list[ShardPlan],
) -> bool:
    if len(rows) != len(plans):
        return False
    stat = source.stat()
    by_index = {int(row["shard_index"]): row for row in rows}
    for plan in plans:
        row = by_index.get(plan.index)
        if row is None:
            return False
        output = Path(row["shard_lhe_path"])
        if (
            row.get("source_lhe_path") != str(source)
            or int(row.get("source_size_bytes", -1)) != stat.st_size
            or int(row.get("source_mtime_ns", -1)) != stat.st_mtime_ns
            or int(row.get("source_event_start", -1)) != plan.start
            or int(row.get("source_event_stop_exclusive", -1)) != plan.stop
            or int(row.get("requested_events", -1)) != plan.events
            or not output.is_file()
            or output.stat().st_size <= 0
            or sha256(output) != row.get("shard_lhe_sha256")
        ):
            return False
    return True


def write_sample_shards(
    *,
    campaign_id: str,
    sample_id: str,
    source: Path,
    output_dir: Path,
    plans: list[ShardPlan],
    created_utc: str,
) -> list[dict[str, str]]:
    stat = source.stat()
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary_dir = output_dir / f".partial_{os.getpid()}"
    if temporary_dir.exists():
        shutil.rmtree(temporary_dir)
    temporary_dir.mkdir(parents=True)

    outputs = [
        output_dir / f"{sample_id}__{plan.shard_id}.lhe"
        for plan in plans
    ]
    temporaries = [temporary_dir / output.name for output in outputs]
    selected_digest = hashlib.sha256()
    prefix_lines: list[str] = []
    first_event_line: str | None = None

    try:
        with open_text(source) as input_stream:
            for line in input_stream:
                if line.strip() == "<event>":
                    first_event_line = line
                    break
                prefix_lines.append(line)
                selected_digest.update(line.encode())

            if first_event_line is None:
                raise ValueError(f"no <event> block found in {source}")
            if not any(
                line.strip().startswith("<LesHouchesEvents")
                for line in prefix_lines
            ):
                raise ValueError(f"not an LHE document: {source}")

            prefix = "".join(prefix_lines)
            with ExitStack() as stack:
                streams = [
                    stack.enter_context(
                        temporary.open("w", encoding="utf-8", newline="")
                    )
                    for temporary in temporaries
                ]
                for stream, plan in zip(streams, plans):
                    stream.write(rewrite_prefix(prefix, plan.events))
                    stream.write(
                        "<!-- qis deterministic shower input shard\n"
                        f"     source={source}\n"
                        f"     source_event_start={plan.start}\n"
                        f"     source_event_stop_exclusive={plan.stop}\n"
                        f"     requested_events={plan.events}\n"
                        "-->\n"
                    )

                event_index = 0
                pending_start = first_event_line
                plan_index = 0
                while event_index < plans[-1].stop:
                    if pending_start is None:
                        for line in input_stream:
                            if line.strip() == "<event>":
                                pending_start = line
                                break
                            if line.strip() == "</LesHouchesEvents>":
                                break
                    if pending_start is None:
                        raise ValueError(
                            f"{source} contains only {event_index} readable events; "
                            f"{plans[-1].stop} required"
                        )

                    while not (
                        plans[plan_index].start
                        <= event_index
                        < plans[plan_index].stop
                    ):
                        plan_index += 1
                    output_stream = streams[plan_index]

                    output_stream.write(pending_start)
                    selected_digest.update(pending_start.encode())
                    pending_start = None
                    closed = False
                    for line in input_stream:
                        output_stream.write(line)
                        selected_digest.update(line.encode())
                        if line.strip() == "</event>":
                            closed = True
                            break
                    if not closed:
                        raise ValueError(
                            f"truncated <event> block {event_index} in {source}"
                        )
                    event_index += 1

                for stream in streams:
                    stream.write("</LesHouchesEvents>\n")

        for temporary in temporaries:
            if not temporary.is_file() or temporary.stat().st_size <= 0:
                raise RuntimeError(f"empty temporary shard: {temporary}")
        for temporary, output in zip(temporaries, outputs):
            temporary.replace(output)

        selected_sha = selected_digest.hexdigest()
        rows: list[dict[str, str]] = []
        for plan, output in zip(plans, outputs):
            rows.append(
                {
                    "schema_version": "2",
                    "campaign_id": campaign_id,
                    "sample_id": sample_id,
                    "source_lhe_path": str(source),
                    "source_size_bytes": str(stat.st_size),
                    "source_mtime_ns": str(stat.st_mtime_ns),
                    "selected_event_window_sha256": selected_sha,
                    "shard_id": plan.shard_id,
                    "shard_index": str(plan.index),
                    "source_event_start": str(plan.start),
                    "source_event_stop_exclusive": str(plan.stop),
                    "requested_events": str(plan.events),
                    "shard_lhe_path": str(output),
                    "shard_lhe_size_bytes": str(output.stat().st_size),
                    "shard_lhe_sha256": sha256(output),
                    "status": "ready",
                    "created_utc": created_utc,
                }
            )
        return rows
    except Exception:
        for output in outputs:
            output.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(temporary_dir, ignore_errors=True)

def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--jobs-per-sample", required=True, type=int)
    parser.add_argument("--total-events-per-sample", type=int)
    parser.add_argument("--sample", action="append", default=[])
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.resume and args.force:
        raise ValueError("--resume and --force are mutually exclusive")

    config = load_yaml(args.config)
    campaign_cfg = config.get("campaign", {})
    shower_cfg = config.get("showering", {})
    if not isinstance(campaign_cfg, dict) or not isinstance(shower_cfg, dict):
        raise ValueError("campaign and showering sections must be mappings")

    manifest = (
        args.manifest
        or Path(str(campaign_cfg.get("source_manifest", "")))
    ).expanduser()
    campaign_output = Path(str(campaign_cfg.get("output_root", ""))).expanduser()
    root = (args.output_root or campaign_output / "shower").expanduser()
    total_events = (
        args.total_events_per_sample
        if args.total_events_per_sample is not None
        else int(shower_cfg.get("total_events_per_sample", 10000))
    )
    if not str(root).startswith("/eos/") and not str(root).startswith("/tmp/"):
        raise ValueError(f"output root must be on EOS or under /tmp: {root}")
    plans = balanced_plan(total_events, args.jobs_per_sample)

    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    with manifest.open(newline="") as stream:
        records = list(csv.DictReader(stream))
    required = {"sample_id", "status", "merged_final_lhe_path"}
    if not records or not required.issubset(records[0]):
        raise ValueError(f"manifest missing columns {sorted(required)}: {manifest}")
    records = [row for row in records if row.get("status") == "success"]
    if args.sample:
        records = [
            row
            for row in records
            if any(
                fnmatch.fnmatch(row["sample_id"], pattern)
                for pattern in args.sample
            )
        ]
    if not records:
        raise ValueError("no successful samples match the selection")

    shard_root = root / "input_shards"
    manifest_dir = root / "manifests"
    manifest_path = manifest_dir / "lhe_shard_manifest.csv"
    existing: list[dict[str, str]] = []
    if manifest_path.is_file():
        with manifest_path.open(newline="") as stream:
            existing = list(csv.DictReader(stream))
        if not args.resume and not args.force:
            raise FileExistsError(
                f"shard manifest exists: {manifest_path}; use --resume or --force"
            )

    if args.force:
        shutil.rmtree(shard_root, ignore_errors=True)
        existing = []

    created_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    all_rows: list[dict[str, str]] = []
    reused = 0
    written = 0
    for row in sorted(records, key=lambda item: item["sample_id"]):
        sample = row["sample_id"]
        source = Path(row["merged_final_lhe_path"])
        if not source.is_file():
            raise FileNotFoundError(
                f"authoritative merged LHE missing for {sample}: {source}"
            )
        previous = [item for item in existing if item.get("sample_id") == sample]
        if args.resume and existing_rows_valid(previous, source=source, plans=plans):
            all_rows.extend(sorted(previous, key=lambda item: int(item["shard_index"])))
            reused += len(previous)
            print(f"REUSE {sample}: {len(previous)} validated shards")
            continue
        sample_dir = shard_root / sample
        shutil.rmtree(sample_dir, ignore_errors=True)
        generated = write_sample_shards(
            campaign_id=str(
                campaign_cfg.get("source_campaign_id", row.get("campaign_id", ""))
            ),
            sample_id=sample,
            source=source,
            output_dir=sample_dir,
            plans=plans,
            created_utc=created_utc,
        )
        all_rows.extend(generated)
        written += len(generated)
        print(
            f"WROTE {sample}: shards={len(generated)} "
            f"events={sum(int(item['requested_events']) for item in generated)}"
        )

    all_rows.sort(key=lambda item: (item["sample_id"], int(item["shard_index"])))
    manifest_dir.mkdir(parents=True, exist_ok=True)
    temporary = manifest_path.with_name(f".{manifest_path.name}.partial")
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    temporary.replace(manifest_path)

    plan = {
        "schema_version": 2,
        "created_utc": created_utc,
        "config": str(args.config.resolve()),
        "source_manifest": str(manifest),
        "output_root": str(root),
        "samples": len(records),
        "jobs_per_sample": args.jobs_per_sample,
        "requested_jobs": len(all_rows),
        "total_events_per_sample": total_events,
        "total_events": total_events * len(records),
        "events_per_shard_min": min(plan.events for plan in plans),
        "events_per_shard_max": max(plan.events for plan in plans),
        "source_read_policy": "prefix_plus_first_requested_events_only",
        "manifest": str(manifest_path),
        "written_shards": written,
        "reused_shards": reused,
    }
    plan_json = manifest_dir / "lhe_shard_plan.json"
    plan_json.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    plan_md = manifest_dir / "lhe_shard_plan.md"
    plan_md.write_text(
        "# LHE shower-shard plan\n\n"
        + "\n".join(f"- {key}: `{value}`" for key, value in plan.items())
        + "\n"
    )
    print(f"Wrote {manifest_path}")
    print(f"Wrote {plan_json}")
    print(
        f"SHARD PREPARATION PASS samples={len(records)} "
        f"jobs={len(all_rows)} jobs_per_sample={args.jobs_per_sample} "
        f"events_per_sample={total_events}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
