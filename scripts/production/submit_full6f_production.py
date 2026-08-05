#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


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


def item(value: object) -> str:
    text = str(value)

    if "\t" in text or "\n" in text:
        raise ValueError(
            f"itemdata value contains tab/newline: {text!r}"
        )

    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate and optionally submit the direct-full6f "
            "HTCondor production campaign."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(os.environ.get("REPO", ".")).resolve(),
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--submission-tag", required=True)
    parser.add_argument("--output-base", type=Path)
    parser.add_argument("--submit", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo = args.repo.resolve()
    manifest = args.manifest.resolve()
    records = load_jsonl(manifest)

    if not records:
        raise SystemExit("ERROR: manifest is empty")

    output_base = (
        args.output_base.resolve()
        if args.output_base is not None
        else (
            repo
            / "condor/runtime_submissions"
            / args.submission_tag
        )
    )

    submission_dir = output_base / utc_stamp()
    logs_dir = submission_dir / "logs"

    submission_dir.mkdir(parents=True, exist_ok=False)
    logs_dir.mkdir(parents=True, exist_ok=True)

    wrapper = (
        repo / "scripts/condor/run_full6f_production_job.sh"
    ).resolve()

    if not wrapper.is_file():
        raise SystemExit(f"ERROR: wrapper missing: {wrapper}")

    itemdata_path = submission_dir / "itemdata.tsv"
    submit_path = submission_dir / "full6f_production.sub"
    manifest_copy = submission_dir / "production_manifest.jsonl"

    manifest_copy.write_bytes(manifest.read_bytes())

    columns = [
        "campaign_id",
        "sample_id",
        "subprocess_id",
        "source_card",
        "shard_index",
        "whizard_seed",
        "events",
        "integration_iterations",
        "campaign_root",
        "archive_workspace",
        "timeout_minutes",
    ]

    with itemdata_path.open("w", encoding="utf-8") as handle:
        # HTCondor's "queue ... from FILE" treats every nonblank line as
        # itemdata. Do not write a TSV header: it would become an extra job
        # with literal values such as "campaign_id" and "sample_id".
        for record in records:
            handle.write(
                "\t".join(
                    item(record[column])
                    for column in columns
                )
                + "\n"
            )

    itemdata_lines = [
        line
        for line in itemdata_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    if len(itemdata_lines) != len(records):
        raise SystemExit(
            "ERROR: itemdata/manifest record-count mismatch: "
            f"{len(itemdata_lines)} != {len(records)}"
        )

    request_cpus = max(
        int(record["request_cpus"])
        for record in records
    )
    request_memory_mb = max(
        int(record["request_memory_mb"])
        for record in records
    )
    request_disk_mb = max(
        int(record["request_disk_mb"])
        for record in records
    )

    flavours = {
        str(record["job_flavour"])
        for record in records
    }

    if len(flavours) != 1:
        raise SystemExit(
            f"ERROR: mixed job flavours: {sorted(flavours)}"
        )

    job_flavour = next(iter(flavours))

    submit_text = f"""universe = vanilla

executable = {wrapper}

arguments = \\
  --repo {repo} \\
  --campaign-id $(campaign_id) \\
  --sample-id $(sample_id) \\
  --subprocess-id $(subprocess_id) \\
  --source-card $(source_card) \\
  --shard-index $(shard_index) \\
  --whizard-seed $(whizard_seed) \\
  --events $(events) \\
  --iterations $(integration_iterations) \\
  --campaign-root $(campaign_root) \\
  --archive-workspace $(archive_workspace) \\
  --timeout-minutes $(timeout_minutes)

initialdir = {submission_dir}

should_transfer_files = NO
getenv = False

request_cpus = {request_cpus}
request_memory = {request_memory_mb}MB
request_disk = {request_disk_mb}MB

+JobFlavour = "{job_flavour}"

output = logs/$(sample_id)__$(subprocess_id)__shard_$(shard_index).out
error  = logs/$(sample_id)__$(subprocess_id)__shard_$(shard_index).err
log    = condor.log

notification = Never

queue {", ".join(columns)} from {itemdata_path}
"""

    submit_path.write_text(submit_text, encoding="utf-8")

    provenance = {
        "schema_version": 1,
        "status": "PREPARED",
        "repo": str(repo),
        "manifest": str(manifest),
        "manifest_copy": str(manifest_copy),
        "itemdata": str(itemdata_path),
        "submit_file": str(submit_path),
        "submission_dir": str(submission_dir),
        "records": len(records),
        "itemdata_records": len(itemdata_lines),
        "request_cpus": request_cpus,
        "request_memory_mb": request_memory_mb,
        "request_disk_mb": request_disk_mb,
        "job_flavour": job_flavour,
        "submitted": bool(args.submit),
    }

    provenance_path = (
        submission_dir / "submission_provenance.json"
    )

    if args.submit:
        command = ["condor_submit", str(submit_path)]

        print("COMMAND=" + shlex.join(command))

        completed = subprocess.run(
            command,
            cwd=submission_dir,
            text=True,
            check=False,
        )

        provenance["condor_submit_return_code"] = (
            completed.returncode
        )
        provenance["status"] = (
            "SUBMITTED"
            if completed.returncode == 0
            else "SUBMIT_FAILED"
        )

        provenance_path.write_text(
            json.dumps(
                provenance,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        if completed.returncode != 0:
            return completed.returncode
    else:
        provenance_path.write_text(
            json.dumps(
                provenance,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    print("FULL6F_CONDOR_PREPARATION_STATUS=PASS")
    print(f"SUBMISSION_DIR={submission_dir}")
    print(f"SUBMIT_FILE={submit_path}")
    print(f"ITEMDATA={itemdata_path}")
    print(f"RECORDS={len(records)}")
    print(f"SUBMITTED={int(args.submit)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
