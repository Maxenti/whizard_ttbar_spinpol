#!/usr/bin/env python3
"""Prepare reproducible HTCondor jobs for PYTHIA8 showering.

The submit-side program owns the persistent EOS namespace and Condor control
files.  Workers read authoritative LHE files from EOS, copy them to scratch,
run the C++ shower executable, and atomically stage HepMC3 plus metadata.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import fnmatch
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as stream:
        payload = yaml.safe_load(stream) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"configuration root must be a mapping: {path}")
    return payload


def successful_metadata(path: Path, output: Path) -> bool:
    if not path.is_file() or not output.is_file() or output.stat().st_size <= 0:
        return False
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return (
        data.get("status") == "success"
        and int(data.get("return_code", 1)) == 0
        and int(data.get("accepted_events", 0)) > 0
    )


def deterministic_seed(base: int, sample_id: str, shard_id: str) -> int:
    digest = hashlib.sha256(f"{sample_id}:{shard_id}".encode()).digest()
    offset = int.from_bytes(digest[:4], "big") % 800_000_000
    seed = 1 + ((base + offset - 1) % 900_000_000)
    return seed


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=repo / "configs/qis/level_a_500GeV_ISR_sc_v1.yaml")
    parser.add_argument("--manifest", type=Path, help="Override campaign sample manifest")
    parser.add_argument("--output-root", type=Path, help="Override shower output root")
    parser.add_argument("--executable", type=Path, help="Override qis_lhe_to_hepmc3 executable")
    parser.add_argument("--settings", type=Path, help="Override PYTHIA command file")
    parser.add_argument("--key4hep-setup", type=Path, default=repo / "setup_lxplus.sh")
    parser.add_argument("--sample", action="append", default=[], help="Glob pattern; repeatable")
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--seed-base", type=int, default=5_100_000)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--job-flavour", default="tomorrow")
    parser.add_argument("--request-memory-mb", type=int, default=3000)
    parser.add_argument("--request-disk-gb", type=int, default=6)
    args = parser.parse_args()

    config = load_yaml(args.config)
    campaign_cfg = config.get("campaign", {})
    shower_cfg = config.get("showering", {})
    if not isinstance(campaign_cfg, dict) or not isinstance(shower_cfg, dict):
        raise ValueError("campaign and showering configuration sections must be mappings")

    manifest = (args.manifest or Path(str(campaign_cfg.get("source_manifest", "")))).expanduser()
    campaign_output = Path(str(campaign_cfg.get("output_root", ""))).expanduser()
    output_root = (args.output_root or campaign_output / "shower").expanduser()
    executable = (args.executable or repo / str(shower_cfg.get("executable", "build/qis_lhe_to_hepmc3"))).expanduser()
    settings = (args.settings or repo / str(shower_cfg.get("settings_file", "configs/pythia/level_a.cmnd"))).expanduser()
    max_events = args.max_events if args.max_events is not None else int(shower_cfg.get("events_per_job", -1))
    qed_shower_by_gamma = (
        "on" if bool(shower_cfg.get("qed_shower_by_gamma", True)) else "off"
    )
    preparation_policy = str(
        shower_cfg.get(
            "lhe_preparation_policy",
            "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3",
        )
    )
    if preparation_policy != "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3":
        raise ValueError(
            "unsupported showering.lhe_preparation_policy: "
            f"{preparation_policy}"
        )

    if not manifest.is_file():
        raise FileNotFoundError(f"sample manifest not found: {manifest}")
    if not settings.is_file():
        raise FileNotFoundError(f"PYTHIA settings not found: {settings}")
    if not args.key4hep_setup.is_file():
        raise FileNotFoundError(f"environment setup not found: {args.key4hep_setup}")
    if args.submit and not executable.is_file():
        raise FileNotFoundError(f"shower executable not built: {executable}")
    if not str(output_root).startswith("/eos/"):
        raise ValueError(f"output root must be on EOS: {output_root}")
    if max_events == 0 or max_events < -1:
        raise ValueError("max-events must be -1 or positive")
    if args.resume and args.force:
        raise ValueError("--resume and --force are mutually exclusive")

    with manifest.open(newline="") as stream:
        records = list(csv.DictReader(stream))
    required = {"sample_id", "status", "merged_final_lhe_path"}
    if not records or not required.issubset(records[0]):
        raise ValueError(f"manifest missing required columns {sorted(required)}: {manifest}")
    records = [row for row in records if row.get("status") == "success"]
    if args.sample:
        records = [row for row in records if any(fnmatch.fnmatch(row["sample_id"], pattern) for pattern in args.sample)]
    if not records:
        raise ValueError("no successful manifest rows match the selection")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    control = repo / "condor/runtime_submissions/qis_shower" / stamp
    provenance = output_root / "manifests/submissions" / stamp
    persistent_dirs = [
        output_root / "hepmc3", output_root / "metadata", output_root / "logs",
        output_root / "preparation", output_root / "manifests",
        output_root / "validation", provenance,
    ]
    local_dirs = [control, control / "stdout", control / "stderr"]
    for directory in (*persistent_dirs, *local_dirs):
        directory.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    seen_seeds: set[int] = set()
    campaign_id = str(campaign_cfg.get("source_campaign_id", records[0].get("campaign_id", "unknown")))

    for row in sorted(records, key=lambda item: item["sample_id"]):
        sample = row["sample_id"]
        input_lhe = Path(row["merged_final_lhe_path"])
        if not input_lhe.is_file():
            raise FileNotFoundError(f"authoritative merged LHE missing for {sample}: {input_lhe}")
        shard_id = "merged"
        output = output_root / "hepmc3" / sample / f"{sample}__{shard_id}.hepmc3"
        metadata = output_root / "metadata" / sample / f"{sample}__{shard_id}.json"
        if args.resume and successful_metadata(metadata, output):
            skipped.append({"sample_id": sample, "reason": "validated output already exists"})
            continue
        if not args.force and not args.resume and (output.exists() or metadata.exists()):
            raise FileExistsError(f"existing output for {sample}; use --resume or --force")
        if args.force:
            output.unlink(missing_ok=True)
            metadata.unlink(missing_ok=True)
        for directory in (
            output.parent, metadata.parent, output_root / "logs" / sample,
            output_root / "preparation" / sample,
            control / "stdout" / sample, control / "stderr" / sample,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        seed = deterministic_seed(args.seed_base, sample, shard_id)
        if seed in seen_seeds:
            raise RuntimeError(f"deterministic seed collision: {seed}")
        seen_seeds.add(seed)
        jobs.append({
            "wrapper": str(repo / "scripts/showering/run_pythia_shard.sh"),
            "input_lhe": str(input_lhe),
            "output_root": str(output_root),
            "sample_id": sample,
            "campaign_id": campaign_id,
            "shard_id": shard_id,
            "seed": str(seed),
            "max_events": str(max_events),
            "shower_executable": str(executable.resolve()),
            "settings_file": str(settings.resolve()),
            "key4hep_setup": str(args.key4hep_setup.resolve()),
            "qed_shower_by_gamma": qed_shower_by_gamma,
            "repo_root": str(repo),
            "stdout_path": str(control / "stdout" / sample / "$(ClusterId).$(ProcId).out"),
            "stderr_path": str(control / "stderr" / sample / "$(ClusterId).$(ProcId).err"),
            "event_log": str(control / "qis_shower.condor.log"),
            "job_cpus": "1",
            "job_memory_mb": str(args.request_memory_mb),
            "job_disk_gb": str(args.request_disk_gb),
            "job_flavour": args.job_flavour,
            "batch_name": f"qis_shower_{campaign_id}",
        })

    if not jobs:
        print(f"Prepared jobs: 0\nSkipped jobs: {len(skipped)}")
        return 0

    itemdata = control / "jobs.itemdata"
    fields = list(jobs[0])
    with itemdata.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=" ", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(jobs)

    template = (repo / "condor/qis/pythia_shower.sub").read_text()
    submit_file = control / "pythia_shower.sub"
    submit_file.write_text(template.replace("$(itemdata)", str(itemdata)))
    submission = {
        "schema_version": 1,
        "created_utc": stamp,
        "config": str(args.config.resolve()),
        "manifest": str(manifest),
        "output_root": str(output_root),
        "lhe_preparation_policy": preparation_policy,
        "qed_shower_by_gamma": qed_shower_by_gamma,
        "jobs": len(jobs),
        "skipped": len(skipped),
        "submit_file": str(submit_file),
        "submitted": False,
    }
    (control / "jobs.json").write_text(json.dumps(jobs, indent=2, sort_keys=True) + "\n")
    (control / "skipped.json").write_text(json.dumps(skipped, indent=2, sort_keys=True) + "\n")
    (control / "submission.json").write_text(json.dumps(submission, indent=2, sort_keys=True) + "\n")
    for file in control.iterdir():
        if file.is_file():
            shutil.copy2(file, provenance / file.name)

    command = ["condor_submit", str(submit_file)]
    print(f"Prepared jobs: {len(jobs)}")
    print(f"Skipped jobs:  {len(skipped)}")
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
        (control / "submission.json").write_text(json.dumps(submission, indent=2, sort_keys=True) + "\n")
        shutil.copy2(control / "submission.json", provenance / "submission.json")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
