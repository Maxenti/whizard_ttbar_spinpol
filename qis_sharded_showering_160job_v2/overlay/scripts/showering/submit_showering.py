#!/usr/bin/env python3
"""Prepare reproducible HTCondor jobs from deterministic LHE shard manifests."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import fnmatch
import hashlib
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text()) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"configuration root must be a mapping: {path}")
    return payload


def successful_metadata(
    metadata_path: Path,
    output_path: Path,
    requested_events: int,
) -> bool:
    if (
        not metadata_path.is_file()
        or not output_path.is_file()
        or output_path.stat().st_size <= 0
    ):
        return False
    try:
        data = json.loads(metadata_path.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return (
        data.get("status") == "success"
        and int(data.get("return_code", 1)) == 0
        and int(data.get("accepted_events", 0)) == requested_events
        and int(data.get("requested_events", -1)) == requested_events
    )



def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def deterministic_seed(base: int, sample_id: str, shard_id: str) -> int:
    digest = hashlib.sha256(f"{sample_id}:{shard_id}".encode()).digest()
    offset = int.from_bytes(digest[:4], "big") % 800_000_000
    return 1 + ((base + offset - 1) % 900_000_000)


def positive_int(name: str, value: int) -> int:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--shard-manifest", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--settings", type=Path)
    parser.add_argument(
        "--key4hep-setup", type=Path, default=repo / "setup_lxplus.sh"
    )
    parser.add_argument("--sample", action="append", default=[])
    parser.add_argument("--expected-jobs", type=int)
    parser.add_argument("--seed-base", type=int)
    parser.add_argument("--request-cpus", type=int)
    parser.add_argument("--request-memory-mb", type=int)
    parser.add_argument("--request-disk-gb", type=int)
    parser.add_argument("--job-flavour")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.resume and args.force:
        raise ValueError("--resume and --force are mutually exclusive")

    config = load_yaml(args.config)
    campaign_cfg = config.get("campaign", {})
    shower_cfg = config.get("showering", {})
    resource_cfg = shower_cfg.get("resources", {})
    if not isinstance(campaign_cfg, dict) or not isinstance(shower_cfg, dict):
        raise ValueError("campaign and showering sections must be mappings")
    if not isinstance(resource_cfg, dict):
        raise ValueError("showering.resources must be a mapping")

    campaign_output = Path(str(campaign_cfg.get("output_root", ""))).expanduser()
    output_root = (args.output_root or campaign_output / "shower").expanduser()
    shard_manifest = (
        args.shard_manifest
        or output_root / "manifests/lhe_shard_manifest.csv"
    ).expanduser()
    executable = (
        args.executable
        or repo / str(shower_cfg.get("executable", "build/qis_lhe_to_hepmc3"))
    ).expanduser()
    settings = (
        args.settings
        or repo / str(shower_cfg.get("settings_file", "configs/pythia/level_a.cmnd"))
    ).expanduser()
    seed_base = (
        args.seed_base
        if args.seed_base is not None
        else int(shower_cfg.get("seed_base", 5_100_000))
    )
    request_cpus = positive_int(
        "request_cpus",
        args.request_cpus
        if args.request_cpus is not None
        else int(resource_cfg.get("request_cpus", 1)),
    )
    request_memory_mb = positive_int(
        "request_memory_mb",
        args.request_memory_mb
        if args.request_memory_mb is not None
        else int(resource_cfg.get("request_memory_mb", 1000)),
    )
    request_disk_gb = positive_int(
        "request_disk_gb",
        args.request_disk_gb
        if args.request_disk_gb is not None
        else int(resource_cfg.get("request_disk_gb", 2)),
    )
    job_flavour = args.job_flavour or str(
        resource_cfg.get("job_flavour", "workday")
    )
    qed_shower_by_gamma = (
        "on" if bool(shower_cfg.get("qed_shower_by_gamma", True)) else "off"
    )
    expected_policy = str(
        shower_cfg.get(
            "lhe_preparation_policy",
            "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3",
        )
    )
    if expected_policy != "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3":
        raise ValueError(f"unsupported LHE preparation policy: {expected_policy}")

    wrapper = repo / "scripts/showering/run_pythia_shard.sh"
    runtime_helpers = (
        wrapper,
        repo / "scripts/showering/canonicalize_whizard_lhe_for_pythia.py",
        repo / "scripts/showering/insert_explicit_w_resonances.py",
        repo / "scripts/showering/augment_shower_metadata.py",
    )
    if not shard_manifest.is_file():
        raise FileNotFoundError(
            f"LHE shard manifest not found: {shard_manifest}; "
            "run prepare_lhe_shards.py first"
        )
    if not settings.is_file():
        raise FileNotFoundError(f"PYTHIA settings not found: {settings}")
    if not args.key4hep_setup.is_file():
        raise FileNotFoundError(f"environment setup not found: {args.key4hep_setup}")
    if args.submit and not executable.is_file():
        raise FileNotFoundError(f"shower executable not built: {executable}")
    for helper in runtime_helpers:
        if not helper.is_file():
            raise FileNotFoundError(f"runtime helper not found: {helper}")
        if not os.access(helper, os.X_OK):
            raise PermissionError(f"runtime helper is not executable: {helper}")
    if not str(output_root).startswith("/eos/"):
        raise ValueError(f"output root must be on EOS: {output_root}")

    with shard_manifest.open(newline="") as stream:
        records = list(csv.DictReader(stream))
    required = {
        "campaign_id",
        "sample_id",
        "source_lhe_path",
        "shard_id",
        "shard_index",
        "source_event_start",
        "source_event_stop_exclusive",
        "requested_events",
        "shard_lhe_path",
        "shard_lhe_sha256",
        "status",
    }
    if not records or not required.issubset(records[0]):
        raise ValueError(
            f"shard manifest missing columns {sorted(required)}: {shard_manifest}"
        )
    records = [row for row in records if row.get("status") == "ready"]
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
        raise ValueError("no ready LHE shard rows match the selection")
    if args.expected_jobs is not None and len(records) != args.expected_jobs:
        raise ValueError(
            f"shard manifest provides {len(records)} jobs; "
            f"expected {args.expected_jobs}"
        )

    campaign_ids = {row["campaign_id"] for row in records}
    if len(campaign_ids) != 1:
        raise ValueError(f"mixed campaign IDs in shard manifest: {campaign_ids}")
    campaign_id = next(iter(campaign_ids))

    seen_keys: set[tuple[str, str]] = set()
    for row in records:
        key = (row["sample_id"], row["shard_id"])
        if key in seen_keys:
            raise ValueError(f"duplicate shard row: {key}")
        seen_keys.add(key)
        requested = int(row["requested_events"])
        start = int(row["source_event_start"])
        stop = int(row["source_event_stop_exclusive"])
        if requested <= 0 or stop - start != requested:
            raise ValueError(f"invalid event range/count for {key}: {row}")
        shard_lhe = Path(row["shard_lhe_path"])
        if not shard_lhe.is_file() or shard_lhe.stat().st_size <= 0:
            raise FileNotFoundError(f"missing/empty LHE shard for {key}: {shard_lhe}")
        actual_sha = sha256(shard_lhe)
        if actual_sha != row["shard_lhe_sha256"]:
            raise ValueError(
                f"LHE shard checksum mismatch for {key}: "
                f"manifest={row['shard_lhe_sha256']} actual={actual_sha}"
            )

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    control = repo / "condor/runtime_submissions/qis_shower" / stamp
    provenance = output_root / "manifests/submissions" / stamp
    persistent_dirs = [
        output_root / "hepmc3",
        output_root / "metadata",
        output_root / "logs",
        output_root / "preparation",
        output_root / "manifests",
        output_root / "validation",
        provenance,
    ]
    local_dirs = [control, control / "stdout", control / "stderr"]
    for directory in (*persistent_dirs, *local_dirs):
        directory.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    seen_seeds: set[int] = set()
    for row in sorted(
        records,
        key=lambda item: (item["sample_id"], int(item["shard_index"])),
    ):
        sample = row["sample_id"]
        shard_id = row["shard_id"]
        requested = int(row["requested_events"])
        input_lhe = Path(row["shard_lhe_path"])
        output = output_root / "hepmc3" / sample / f"{sample}__{shard_id}.hepmc3"
        metadata = output_root / "metadata" / sample / f"{sample}__{shard_id}.json"
        if args.resume and successful_metadata(metadata, output, requested):
            skipped.append(
                {
                    "sample_id": sample,
                    "shard_id": shard_id,
                    "reason": "validated output already exists",
                }
            )
            continue
        if not args.force and not args.resume and (output.exists() or metadata.exists()):
            raise FileExistsError(
                f"existing output for {sample}/{shard_id}; use --resume or --force"
            )
        if args.force:
            output.unlink(missing_ok=True)
            metadata.unlink(missing_ok=True)
        for directory in (
            output.parent,
            metadata.parent,
            output_root / "logs" / sample,
            output_root / "preparation" / sample,
            control / "stdout" / sample,
            control / "stderr" / sample,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        seed = deterministic_seed(seed_base, sample, shard_id)
        if seed in seen_seeds:
            raise RuntimeError(f"deterministic seed collision: {seed}")
        seen_seeds.add(seed)
        jobs.append(
            {
                "wrapper": str(wrapper),
                "input_lhe": str(input_lhe),
                "parent_lhe": row["source_lhe_path"],
                "input_lhe_sha256": row["shard_lhe_sha256"],
                "source_event_start": row["source_event_start"],
                "source_event_stop": row["source_event_stop_exclusive"],
                "output_root": str(output_root),
                "sample_id": sample,
                "campaign_id": campaign_id,
                "shard_id": shard_id,
                "seed": str(seed),
                "max_events": str(requested),
                "shower_executable": str(executable.resolve()),
                "settings_file": str(settings.resolve()),
                "key4hep_setup": str(args.key4hep_setup.resolve()),
                "qed_shower_by_gamma": qed_shower_by_gamma,
                "repo_root": str(repo),
                "stdout_path": str(
                    control
                    / "stdout"
                    / sample
                    / f"{shard_id}.$(ClusterId).$(ProcId).out"
                ),
                "stderr_path": str(
                    control
                    / "stderr"
                    / sample
                    / f"{shard_id}.$(ClusterId).$(ProcId).err"
                ),
                "event_log": str(control / "qis_shower.condor.log"),
                "job_cpus": str(request_cpus),
                "job_memory_mb": str(request_memory_mb),
                "job_disk_gb": str(request_disk_gb),
                "job_flavour": job_flavour,
                "batch_name": f"qis_shower_{campaign_id}",
            }
        )

    if not jobs:
        print(f"Prepared jobs: 0\nSkipped jobs: {len(skipped)}")
        return 0

    itemdata = control / "jobs.itemdata"
    fields = list(jobs[0])
    with itemdata.open("w", newline="") as stream:
        writer = csv.writer(
            stream,
            delimiter=" ",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        for job in jobs:
            writer.writerow([job[field] for field in fields])
    itemdata_rows = [line for line in itemdata.read_text().splitlines() if line.strip()]
    if len(itemdata_rows) != len(jobs):
        raise RuntimeError(
            f"itemdata row-count mismatch: wrote {len(itemdata_rows)}, "
            f"expected {len(jobs)}"
        )
    if itemdata_rows and itemdata_rows[0].split(maxsplit=1)[0] == fields[0]:
        raise RuntimeError("jobs.itemdata incorrectly contains a header row")

    template = (repo / "condor/qis/pythia_shower.sub").read_text()
    submit_file = control / "pythia_shower.sub"
    submit_file.write_text(template.replace("$(itemdata)", str(itemdata)))
    submission = {
        "schema_version": 2,
        "created_utc": stamp,
        "config": str(args.config.resolve()),
        "shard_manifest": str(shard_manifest),
        "output_root": str(output_root),
        "lhe_preparation_policy": expected_policy,
        "qed_shower_by_gamma": qed_shower_by_gamma,
        "jobs": len(jobs),
        "skipped": len(skipped),
        "resources": {
            "request_cpus": request_cpus,
            "request_memory_mb": request_memory_mb,
            "request_disk_gb": request_disk_gb,
            "job_flavour": job_flavour,
        },
        "submit_file": str(submit_file),
        "submitted": False,
    }
    (control / "jobs.json").write_text(
        json.dumps(jobs, indent=2, sort_keys=True) + "\n"
    )
    (control / "skipped.json").write_text(
        json.dumps(skipped, indent=2, sort_keys=True) + "\n"
    )
    (control / "submission.json").write_text(
        json.dumps(submission, indent=2, sort_keys=True) + "\n"
    )
    for file in control.iterdir():
        if file.is_file():
            shutil.copy2(file, provenance / file.name)

    command = ["condor_submit", str(submit_file)]
    print(f"Prepared jobs: {len(jobs)}")
    print(f"Skipped jobs:  {len(skipped)}")
    print(
        "Resources:     "
        f"cpu={request_cpus} memory={request_memory_mb}MB "
        f"disk={request_disk_gb}GB flavour={job_flavour}"
    )
    print(f"Control dir:   {control}")
    print(f"EOS record:    {provenance}")
    print(f"Submit file:   {submit_file}")
    if not args.submit:
        print("Command:\n  " + shlex.join(command))
        return 0
    result = subprocess.run(command, text=True)
    if result.returncode == 0:
        submission["submitted"] = True
        submission["submitted_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        (control / "submission.json").write_text(
            json.dumps(submission, indent=2, sort_keys=True) + "\n"
        )
        shutil.copy2(control / "submission.json", provenance / "submission.json")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
