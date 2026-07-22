#!/usr/bin/env python3
"""Prepare all 16 qualified ISR SINDARIN inputs for the 365 GeV LHE campaign."""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paper_spin_365_matrix_common import (  # noqa: E402
    build_matrix,
    sha256,
    transform_template,
    write_json,
)


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def resolve(repo: Path, path: Path) -> Path:
    return path.expanduser().resolve() if path.is_absolute() else (repo / path).resolve()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    result.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_lhe_matrix.yaml"),
    )
    result.add_argument(
        "--profile",
        choices=("pilot", "production_10k"),
        default="pilot",
    )
    result.add_argument("--campaign-id")
    result.add_argument("--events", type=int)
    result.add_argument("--seed-base", type=int)
    result.add_argument("--output-root", type=Path)
    result.add_argument("--template-root", type=Path)
    result.add_argument("--force", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    repo = args.repo_root.expanduser().resolve()
    config_path = resolve(repo, args.config)
    config = load_yaml(config_path)

    profiles = config.get("profiles", {})
    if args.profile not in profiles:
        raise KeyError(f"Missing profile {args.profile!r} in {config_path}")
    profile = dict(profiles[args.profile])

    campaign_id = args.campaign_id or str(profile["campaign_id"])
    events = args.events if args.events is not None else int(profile["events_per_sample"])
    seed_base = args.seed_base if args.seed_base is not None else int(profile["seed_base"])
    output_root_value = args.output_root or Path(str(profile["output_root"]))
    output_root = resolve(repo, output_root_value)
    template_root_value = args.template_root or Path(str(config["template_root"]))
    template_root = resolve(repo, template_root_value)

    if output_root.exists():
        if not args.force:
            raise FileExistsError(
                f"Refusing to overwrite existing campaign root: {output_root}\n"
                "Use --force only when intentionally rebuilding this campaign."
            )
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True)
    (output_root / "logs").mkdir()
    (output_root / "condor").mkdir()
    (output_root / "provenance").mkdir()

    # Preserve the logical repository paths in the matrix definition.  The
    # user's ``runs`` directory may be a symlink into EOS; calling
    # ``relative_to(repo)`` on its resolved target would therefore fail.
    logical_output_root = str(output_root_value)
    logical_template_root = str(template_root_value)
    matrix = build_matrix(
        events=events,
        seed_base=seed_base,
        output_root=logical_output_root,
        template_root=logical_template_root,
        source_energy_GeV=int(config["source_sqrt_s_GeV"]),
        target_energy_GeV=int(config["nominal_sqrt_s_GeV"]),
    )

    created_utc = datetime.now(timezone.utc).isoformat()
    sample_rows: list[dict[str, Any]] = []
    missing_templates: list[str] = []

    for sample in matrix:
        template_candidate = Path(sample.template_relative_path)
        run_candidate = Path(sample.run_relative_path)
        template = (
            template_candidate.expanduser().resolve()
            if template_candidate.is_absolute()
            else (repo / template_candidate).resolve()
        )
        run_dir = (
            run_candidate.expanduser().resolve()
            if run_candidate.is_absolute()
            else (repo / run_candidate).resolve()
        )
        if not template.is_file():
            missing_templates.append(str(template))
            continue

        run_dir.mkdir(parents=True, exist_ok=False)
        source_text = template.read_text()
        transformed, counts, contract_checks = transform_template(
            source_text,
            campaign_id,
            sample,
        )

        input_path = run_dir / "input.sin"
        input_path.write_text(transformed)
        patch_path = run_dir / "input_500_to_365.patch"
        patch_path.write_text(
            "".join(
                difflib.unified_diff(
                    source_text.splitlines(keepends=True),
                    transformed.splitlines(keepends=True),
                    fromfile=str(template),
                    tofile=str(input_path),
                )
            )
        )

        sample_manifest = {
            "schema_version": 1,
            "campaign_id": campaign_id,
            "profile": args.profile,
            "created_utc": created_utc,
            **sample.as_dict(),
            "template_path": str(template),
            "template_sha256": sha256(template),
            "run_dir": str(run_dir),
            "input_path": str(input_path),
            "input_sha256": sha256(input_path),
            "patch_path": str(patch_path),
            "replacement_counts": counts,
            "contract_checks": contract_checks,
            "contract_status": "pass",
            "source_template_modified": False,
        }
        write_json(run_dir / "preparation_manifest.json", sample_manifest)

        row = {
            "index": sample.index,
            "sample_id": sample.sample_id,
            "source_sample_id": sample.source_sample_id,
            "initial_state": sample.initial_state,
            "decay_channel": sample.decay_channel,
            "polarization": sample.polarization,
            "spin_mode": sample.spin_mode,
            "events": sample.events,
            "random_seed": sample.random_seed,
            "template_path": str(template),
            "template_sha256": sha256(template),
            "run_dir": str(run_dir),
            "input_path": str(input_path),
            "input_sha256": sha256(input_path),
            "expected_lhe_path": str(run_dir / f"{sample.sample_id}.lhe"),
            "sample_validation_path": str(run_dir / "sample_validation.json"),
            "sample_complete_path": str(run_dir / "sample_complete.json"),
        }
        sample_rows.append(row)

    if missing_templates:
        shutil.rmtree(output_root)
        rendered = "\n".join(f"  - {path}" for path in missing_templates)
        raise FileNotFoundError(
            "The complete qualified 500 GeV ISR template matrix is required.\n"
            f"Missing templates:\n{rendered}"
        )

    if len(sample_rows) != 16:
        shutil.rmtree(output_root)
        raise RuntimeError(f"Expected 16 prepared samples, produced {len(sample_rows)}")

    fieldnames = list(sample_rows[0].keys())
    csv_path = output_root / "campaign_samples.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_rows)

    tsv_path = output_root / "campaign_samples.tsv"
    with tsv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(sample_rows)

    (output_root / "sample_ids.txt").write_text(
        "\n".join(str(row["sample_id"]) for row in sample_rows) + "\n"
    )

    config_snapshot = output_root / "campaign_config_snapshot.yaml"
    snapshot = {
        **config,
        "resolved_profile": args.profile,
        "resolved_campaign_id": campaign_id,
        "resolved_events_per_sample": events,
        "resolved_seed_base": seed_base,
        "resolved_output_root": str(output_root),
        "resolved_template_root": str(template_root),
    }
    config_snapshot.write_text(yaml.safe_dump(snapshot, sort_keys=False))

    campaign_manifest = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "profile": args.profile,
        "created_utc": created_utc,
        "repo_root": str(repo),
        "config_path": str(config_path),
        "config_sha256": sha256(config_path),
        "config_snapshot": str(config_snapshot),
        "source_sqrt_s_GeV": float(config["source_sqrt_s_GeV"]),
        "nominal_sqrt_s_GeV": float(config["nominal_sqrt_s_GeV"]),
        "events_per_sample": events,
        "seed_base": seed_base,
        "output_root": str(output_root),
        "template_root": str(template_root),
        "expected_samples": 16,
        "prepared_samples": 16,
        "sample_ids": [row["sample_id"] for row in sample_rows],
        "campaign_samples_csv": str(csv_path),
        "campaign_samples_tsv": str(tsv_path),
        "status": "prepared",
    }
    write_json(output_root / "campaign_manifest.json", campaign_manifest)

    print(json.dumps(campaign_manifest, indent=2))
    print()
    print(f"Prepared 16 samples under: {output_root}")
    print(f"Sample table:              {tsv_path}")
    print("No WHIZARD jobs were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
