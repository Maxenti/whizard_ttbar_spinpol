#!/usr/bin/env python3
"""Run a Phase 7 canonical bridge manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_manifest(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
    return records


def extract_runner_dir(log_text: str) -> str | None:
    matches = re.findall(r"PHASE7_BRIDGE_RUNNER_RUN_DIR=(.+)", log_text)
    return matches[-1].strip() if matches else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(os.environ.get("REPO", ".")).resolve())
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runner", type=Path, default=None)
    parser.add_argument("--output-base", type=Path, default=None)
    parser.add_argument("--log-dir", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-label", action="append", default=[])
    parser.add_argument("--events", type=int, default=None)
    parser.add_argument("--iterations", default=None)
    parser.add_argument(
        "--timeout-whizard-minutes",
        type=int,
        default=None,
        help="Forwarded timeout for the WHIZARD stage in each child bridge runner.",
    )
    parser.add_argument(
        "--pythia-profile",
        choices=["full_hadron", "parton_only"],
        default=None,
    )
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    manifest = args.manifest.resolve()
    runner = args.runner or (repo / "scripts/showering/run_phase7_canonical_bridge.py")
    runner = runner.resolve()

    if not manifest.is_file():
        raise RuntimeError(f"manifest not found: {manifest}")
    if not runner.is_file():
        raise RuntimeError(f"runner not found: {runner}")

    records = load_manifest(manifest)

    if args.only_label:
        wanted = set(args.only_label)
        records = [record for record in records if record.get("label") in wanted]

    if args.limit is not None:
        records = records[: args.limit]

    if not records:
        raise RuntimeError("manifest selection is empty")

    stamp = utc_stamp()
    log_dir = args.log_dir or (repo / "inspection_outputs" / f"phase7_bridge_manifest_run_{stamp}")
    log_dir.mkdir(parents=True, exist_ok=True)

    summary_records = []
    failures = 0

    for index, record in enumerate(records, start=1):
        label = record["label"]
        card = record["card"]

        manifest_events = int(record.get("events", 100))
        events = args.events if args.events is not None else manifest_events
        iterations = args.iterations if args.iterations is not None else str(record.get("iterations", "3:5000"))
        seed = int(record["seed"])
        pythia_profile = args.pythia_profile or str(record.get("pythia_profile", "full_hadron"))
        sample_id = record.get("sample_id", f"{label}_canonical_v2")

        default_manifest_shard_id = f"bridge_{manifest_events}ev_{label}"
        manifest_shard_id = str(record.get("shard_id", default_manifest_shard_id))

        # If --events overrides the manifest event count, keep shard/event
        # bookkeeping consistent for default shard IDs.  Preserve explicitly
        # customized shard IDs.
        if args.events is not None and manifest_shard_id == default_manifest_shard_id:
            shard_id = f"bridge_{events}ev_{label}"
        else:
            shard_id = manifest_shard_id

        command = [
            sys.executable,
            str(runner),
            "--repo",
            str(repo),
            "--card",
            card,
            "--label",
            label,
            "--sample-id",
            sample_id,
            "--shard-id",
            shard_id,
            "--events",
            str(events),
            "--iterations",
            iterations,
            "--seed",
            str(seed),
            "--pythia-profile",
            pythia_profile,
        ]

        if args.output_base is not None:
            command += ["--output-base", str(args.output_base)]

        if args.timeout_whizard_minutes is not None:
            command += ["--timeout-whizard-minutes", str(args.timeout_whizard_minutes)]

        if args.dry_run:
            command.append("--dry-run")

        log_path = log_dir / f"{index:03d}_{label}.log"

        print("=" * 100)
        print(f"MANIFEST_INDEX={index}")
        print(f"LABEL={label}")
        print(f"LOG={log_path}")
        print("COMMAND=" + " ".join(command))
        print("=" * 100)

        child_output_lines = []
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.Popen(
                command,
                cwd=str(repo),
                env=os.environ.copy(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
            )

            assert proc.stdout is not None
            for line in proc.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
                child_output_lines.append(line)

            return_code = proc.wait()

        child_stdout = "".join(child_output_lines)

        runner_dir = extract_runner_dir(child_stdout)

        child_summary = None
        child_summary_path = None
        runner_status = None
        event_counts = None
        warning_counts = None
        runner_warnings = None
        runner_errors = None

        if runner_dir:
            candidate = Path(runner_dir) / "phase7_bridge_summary.json"
            child_summary_path = str(candidate)
            if candidate.is_file():
                try:
                    child_summary = json.loads(candidate.read_text(encoding="utf-8"))
                    runner_status = child_summary.get("status")
                    event_counts = child_summary.get("event_counts")
                    warning_counts = child_summary.get("warning_counts")
                    runner_warnings = child_summary.get("warnings")
                    runner_errors = child_summary.get("errors")
                except Exception as exc:
                    runner_errors = [f"could not parse child summary {candidate}: {exc}"]

        result = {
            "index": index,
            "label": label,
            "category": record.get("category"),
            "card": card,
            "events": events,
            "iterations": iterations,
            "seed": seed,
            "pythia_profile": pythia_profile,
            "sample_id": sample_id,
            "shard_id": shard_id,
            "return_code": return_code,
            "runner_dir": runner_dir,
            "runner_summary": child_summary_path,
            "runner_status": runner_status,
            "event_counts": event_counts,
            "warning_counts": warning_counts,
            "runner_warnings": runner_warnings,
            "runner_errors": runner_errors,
            "log": str(log_path),
        }

        summary_records.append(result)

        if return_code != 0:
            failures += 1
            if not args.continue_on_error:
                break

    status = "PASS" if failures == 0 else "FAIL"

    summary = {
        "schema_version": 1,
        "phase_name": "phase7_bridge_manifest_run",
        "status": status,
        "repo": str(repo),
        "manifest": str(manifest),
        "runner": str(runner),
        "log_dir": str(log_dir),
        "selected_records": len(records),
        "completed_records": len(summary_records),
        "failures": failures,
        "records": summary_records,
    }

    summary_path = log_dir / "manifest_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("=" * 100)
    print(f"PHASE7_BRIDGE_MANIFEST_STATUS={status}")
    print(f"PHASE7_BRIDGE_MANIFEST_LOG_DIR={log_dir}")
    print(f"PHASE7_BRIDGE_MANIFEST_SUMMARY={summary_path}")
    print(f"FAILURES={failures}")
    print("=" * 100)

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
