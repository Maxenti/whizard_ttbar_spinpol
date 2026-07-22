#!/usr/bin/env python3
"""Collect and validate the complete 16-sample 365 GeV ISR LHE matrix."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def comparison(
    *,
    name: str,
    left: dict[str, Any],
    right: dict[str, Any],
    maximum_pull: float,
) -> dict[str, Any]:
    left_xs = float(left["cross_section_pb"])
    right_xs = float(right["cross_section_pb"])
    left_err = float(left["cross_section_error_pb"])
    right_err = float(right["cross_section_error_pb"])
    delta = left_xs - right_xs
    standard_error = math.sqrt(left_err * left_err + right_err * right_err)
    pull = delta / standard_error if standard_error > 0.0 else (0.0 if delta == 0.0 else math.inf)
    return {
        "comparison": name,
        "left_sample_id": left["sample_id"],
        "right_sample_id": right["sample_id"],
        "left_cross_section_pb": left_xs,
        "right_cross_section_pb": right_xs,
        "delta_pb": delta,
        "standard_error_pb": standard_error,
        "pull": pull,
        "maximum_allowed_abs_pull": maximum_pull,
        "status": "pass" if math.isfinite(pull) and abs(pull) <= maximum_pull else "fail",
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    result.add_argument("--campaign-root", type=Path, required=True)
    result.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_lhe_matrix.yaml"),
    )
    result.add_argument("--strict", action="store_true")
    return result


def resolve(repo: Path, path: Path) -> Path:
    return path.expanduser().resolve() if path.is_absolute() else (repo / path).resolve()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parser().parse_args()
    repo = args.repo_root.expanduser().resolve()
    campaign_root = resolve(repo, args.campaign_root)
    config = load_yaml(resolve(repo, args.config))
    validation_config = config["validation"]
    manifest = load_json(campaign_root / "campaign_manifest.json")

    with (campaign_root / "campaign_samples.tsv").open(newline="") as stream:
        planned_rows = list(csv.DictReader(stream, delimiter="\t"))

    sample_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    failed: list[str] = []

    for planned in planned_rows:
        sample_id = planned["sample_id"]
        validation_path = Path(planned["sample_validation_path"])
        complete_path = Path(planned["sample_complete_path"])
        lhe_path = Path(planned["expected_lhe_path"])
        if not validation_path.is_file() or not complete_path.is_file() or not lhe_path.is_file():
            missing.append(sample_id)
            continue

        sample_validation = load_json(validation_path)
        sample_complete = load_json(complete_path)
        if sample_validation.get("status") != "pass" or sample_complete.get("status") != "pass":
            failed.append(sample_id)

        row = {
            "sample_id": sample_id,
            "initial_state": planned["initial_state"],
            "decay_channel": planned["decay_channel"],
            "polarization": planned["polarization"],
            "spin_mode": planned["spin_mode"],
            "events": int(planned["events"]),
            "random_seed": int(planned["random_seed"]),
            "cross_section_pb": float(sample_validation["header"]["cross_section_pb"]),
            "cross_section_error_pb": float(
                sample_validation["header"]["cross_section_error_pb"]
            ),
            "relative_cross_section_error": float(
                sample_validation["header"]["relative_cross_section_error"]
            ),
            "minimum_mtt_GeV": float(sample_validation["mtt_GeV"]["minimum"]),
            "maximum_mtt_GeV": float(sample_validation["mtt_GeV"]["maximum"]),
            "mean_mtt_GeV": float(sample_validation["mtt_GeV"]["mean"]),
            "fraction_below_350_GeV": float(
                sample_validation["fraction_below_350_GeV"]
            ),
            "unweighting_efficiency_percent": None,
            "lhe_path": str(lhe_path),
            "lhe_sha256": sha256(lhe_path),
            "validation_status": sample_validation["status"],
        }

        console = Path(planned["run_dir"]) / "console.log"
        if console.is_file():
            import re

            match = re.search(
                r"actual unweighting efficiency\s*=\s*([0-9.+\-Ee]+)\s*%",
                console.read_text(errors="replace"),
            )
            if match:
                row["unweighting_efficiency_percent"] = float(match.group(1))
        sample_rows.append(row)

    lookup = {
        (
            row["initial_state"],
            row["decay_channel"],
            row["polarization"],
            row["spin_mode"],
        ): row
        for row in sample_rows
    }
    comparisons: list[dict[str, Any]] = []
    maximum_pull = float(validation_config["maximum_consistency_pull"])

    # Spin-correlated and isotropic decays have the same hard-process rate.
    for initial_state in ("ee", "mumu"):
        for decay_channel in ("epmum", "mupem"):
            for polarization in ("LR100", "RL100"):
                left = lookup.get((initial_state, decay_channel, polarization, "sc"))
                right = lookup.get((initial_state, decay_channel, polarization, "iso"))
                if left and right:
                    comparisons.append(
                        comparison(
                            name="sc_vs_iso_cross_section",
                            left=left,
                            right=right,
                            maximum_pull=maximum_pull,
                        )
                    )

    # Swapping e/mu between t and tbar should preserve the integrated rate.
    for initial_state in ("ee", "mumu"):
        for polarization in ("LR100", "RL100"):
            for spin_mode in ("sc", "iso"):
                left = lookup.get((initial_state, "epmum", polarization, spin_mode))
                right = lookup.get((initial_state, "mupem", polarization, spin_mode))
                if left and right:
                    comparisons.append(
                        comparison(
                            name="epmum_vs_mupem_cross_section",
                            left=left,
                            right=right,
                            maximum_pull=maximum_pull,
                        )
                    )

    campaign_checks = [
        {
            "check": "planned_sample_count",
            "status": "pass" if len(planned_rows) == 16 else "fail",
            "message": f"planned samples={len(planned_rows)}, expected=16",
        },
        {
            "check": "completed_sample_count",
            "status": "pass" if len(sample_rows) == 16 else "fail",
            "message": f"completed samples={len(sample_rows)}, expected=16",
        },
        {
            "check": "all_sample_validations",
            "status": "pass" if not failed else "fail",
            "message": f"failed sample validations={failed}",
        },
        {
            "check": "all_samples_present",
            "status": "pass" if not missing else "fail",
            "message": f"missing samples={missing}",
        },
        {
            "check": "unique_random_seeds",
            "status": "pass"
            if len({int(row["random_seed"]) for row in planned_rows}) == 16
            else "fail",
            "message": "all 16 sample seeds must be unique",
        },
        {
            "check": "integration_precision",
            "status": "pass"
            if sample_rows
            and all(
                float(row["relative_cross_section_error"])
                <= float(validation_config["maximum_relative_cross_section_error"])
                for row in sample_rows
            )
            else "fail",
            "message": "all relative cross-section errors satisfy the configured limit",
        },
        {
            "check": "cross_section_consistency",
            "status": "pass"
            if len(comparisons) == 16
            and all(row["status"] == "pass" for row in comparisons)
            else "fail",
            "message": f"passing comparisons={sum(row['status'] == 'pass' for row in comparisons)}/{len(comparisons)}",
        },
    ]

    status = (
        "pass"
        if all(check["status"] == "pass" for check in campaign_checks)
        else "fail"
    )

    write_csv(campaign_root / "cross_sections.csv", sample_rows)
    write_csv(campaign_root / "cross_section_consistency_checks.csv", comparisons)

    payload = {
        "schema_version": 1,
        "campaign_id": manifest["campaign_id"],
        "profile": manifest["profile"],
        "collected_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_root": str(campaign_root),
        "planned_samples": len(planned_rows),
        "completed_samples": len(sample_rows),
        "missing_samples": missing,
        "failed_samples": failed,
        "sample_results": sample_rows,
        "cross_section_consistency_checks": comparisons,
        "checks": campaign_checks,
        "status": status,
    }
    (campaign_root / "campaign_validation.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )

    summary_lines = [
        f"# {manifest['campaign_id']}",
        "",
        f"- Profile: `{manifest['profile']}`",
        f"- Samples completed: `{len(sample_rows)}/16`",
        f"- Campaign validation: `{status}`",
        f"- Events per sample: `{manifest['events_per_sample']}`",
        f"- Nominal energy: `{manifest['nominal_sqrt_s_GeV']} GeV`",
        "",
        "## Validation checks",
        "",
    ]
    for check in campaign_checks:
        summary_lines.append(
            f"- **{check['check']}**: `{check['status']}` — {check['message']}"
        )
    summary_lines.extend(
        [
            "",
            "## Scope",
            "",
            "This is a polarized, ISR-enabled, tree-level continuum ttbar LHE campaign.",
            "It does not include threshold resummation or nonresonant W+b W-bbar backgrounds.",
            "",
        ]
    )
    (campaign_root / "CAMPAIGN_SUMMARY.md").write_text("\n".join(summary_lines))

    checksum_paths: list[Path] = [
        campaign_root / "campaign_manifest.json",
        campaign_root / "campaign_config_snapshot.yaml",
        campaign_root / "campaign_samples.csv",
        campaign_root / "campaign_samples.tsv",
        campaign_root / "sample_ids.txt",
        campaign_root / "campaign_validation.json",
        campaign_root / "cross_sections.csv",
        campaign_root / "cross_section_consistency_checks.csv",
        campaign_root / "CAMPAIGN_SUMMARY.md",
    ]
    for planned in planned_rows:
        run_dir = Path(planned["run_dir"])
        checksum_paths.extend(
            [
                run_dir / "input.sin",
                run_dir / "input_500_to_365.patch",
                run_dir / "preparation_manifest.json",
                Path(planned["expected_lhe_path"]),
                Path(planned["sample_validation_path"]),
                Path(planned["sample_complete_path"]),
                run_dir / "console.log",
            ]
        )

    checksum_lines: list[str] = []
    for path in checksum_paths:
        if path.is_file():
            checksum_lines.append(f"{sha256(path)}  {path.relative_to(campaign_root)}")
    (campaign_root / "CAMPAIGN_SHA256SUMS.txt").write_text(
        "\n".join(checksum_lines) + "\n"
    )

    print(json.dumps(payload, indent=2))
    return 1 if args.strict and status != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
