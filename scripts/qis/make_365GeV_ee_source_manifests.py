#!/usr/bin/env python3
"""Build validated SC and ISO source manifests for 365 GeV ee transport.

The input is the frozen campaign-level validation record produced for

    paper_spin_365GeV_lhe_matrix_10k_v1

The output manifests intentionally expose the ``merged_final_lhe_path`` and
``status`` columns expected by the generic LHE-sharding infrastructure while
retaining enough generator metadata for provenance and later audits.

No LHE content is modified by this script.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_CAMPAIGN_ID = "paper_spin_365GeV_lhe_matrix_10k_v1"
EXPECTED_INITIAL_STATE = "ee"
EXPECTED_EVENTS_PER_SAMPLE = 10_000
EXPECTED_SQRT_S_GEV = 365.0

DECAY_CHANNELS = ("epmum", "mupem")
POLARIZATIONS = ("LR100", "RL100")
SPIN_MODES = ("sc", "iso")

MANIFEST_FIELDS = [
    "schema_version",
    "campaign_id",
    "sample_id",
    "initial_state",
    "decay_channel",
    "polarization",
    "spin_mode",
    "sqrt_s_GeV",
    "expected_events",
    "generated_events",
    "random_seed",
    "cross_section_pb",
    "cross_section_error_pb",
    "relative_cross_section_error",
    "minimum_mtt_GeV",
    "maximum_mtt_GeV",
    "mean_mtt_GeV",
    "fraction_below_350_GeV",
    "unweighting_efficiency_percent",
    "merged_final_lhe_path",
    "lhe_sha256",
    "lhe_size_bytes",
    "status",
    "updated_utc",
    "source_validation_path",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def count_lhe_events(path: Path) -> int:
    count = 0
    document_closed = False

    with path.open(
        "r",
        encoding="utf-8",
        errors="strict",
        newline="",
    ) as stream:
        for line in stream:
            stripped = line.strip()

            if stripped == "<event>":
                count += 1
            elif stripped == "</LesHouchesEvents>":
                document_closed = True

    if not document_closed:
        raise ValueError(f"LHE document is not closed: {path}")

    return count


def expected_sample_ids() -> set[str]:
    return {
        (
            f"ee_ttbar_{decay}_{polarization}_{spin_mode}"
            "_ISR_365GeV"
        )
        for decay in DECAY_CHANNELS
        for polarization in POLARIZATIONS
        for spin_mode in SPIN_MODES
    }


def add_candidate(
    candidates: list[Path],
    candidate: Path | None,
) -> None:
    if candidate is None:
        return

    text = str(candidate)

    if not text:
        return

    if candidate not in candidates:
        candidates.append(candidate)


def eos_alias(path: Path) -> Path | None:
    text = str(path)

    prefix = "/eos/home-c/cglenn/"

    if text.startswith(prefix):
        return Path(
            "/eos/user/c/cglenn/"
            + text[len(prefix):]
        )

    return None


def resolve_lhe_path(
    *,
    row: dict[str, Any],
    campaign: dict[str, Any],
    validation_path: Path,
) -> Path:
    sample_id = str(row["sample_id"])
    initial_state = str(row["initial_state"])

    candidates: list[Path] = []

    recorded = Path(str(row.get("lhe_path", "")))
    add_candidate(candidates, eos_alias(recorded))
    add_candidate(candidates, recorded)

    campaign_root_text = str(campaign.get("campaign_root", ""))

    if campaign_root_text:
        campaign_root = Path(campaign_root_text)

        add_candidate(
            candidates,
            eos_alias(
                campaign_root
                / initial_state
                / sample_id
                / f"{sample_id}.lhe"
            ),
        )

        add_candidate(
            candidates,
            campaign_root
            / initial_state
            / sample_id
            / f"{sample_id}.lhe",
        )

    # This candidate is useful when the repository's runs/ tree is an AFS
    # path or an AFS-visible link to the authoritative EOS campaign.
    add_candidate(
        candidates,
        validation_path.parent
        / initial_state
        / sample_id
        / f"{sample_id}.lhe",
    )

    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate

    attempted = "\n".join(
        f"  - {candidate}"
        for candidate in candidates
    )

    raise FileNotFoundError(
        f"no readable LHE found for {sample_id}; attempted:\n"
        f"{attempted}"
    )


def load_campaign(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())

    if not isinstance(payload, dict):
        raise ValueError("campaign validation root must be a mapping")

    return payload


def validate_campaign_header(
    campaign: dict[str, Any],
    *,
    expected_campaign_id: str,
) -> None:
    failures: list[str] = []

    if campaign.get("campaign_id") != expected_campaign_id:
        failures.append(
            "campaign_id mismatch: "
            f"{campaign.get('campaign_id')!r} != "
            f"{expected_campaign_id!r}"
        )

    if campaign.get("status") != "pass":
        failures.append(
            f"campaign status is not pass: {campaign.get('status')!r}"
        )

    if int(campaign.get("planned_samples", -1)) != 16:
        failures.append(
            "planned_samples must be 16, found "
            f"{campaign.get('planned_samples')!r}"
        )

    if int(campaign.get("completed_samples", -1)) != 16:
        failures.append(
            "completed_samples must be 16, found "
            f"{campaign.get('completed_samples')!r}"
        )

    if campaign.get("missing_samples"):
        failures.append(
            f"missing samples reported: {campaign['missing_samples']!r}"
        )

    if campaign.get("failed_samples"):
        failures.append(
            f"failed samples reported: {campaign['failed_samples']!r}"
        )

    if failures:
        raise ValueError(
            "campaign-header validation failed:\n"
            + "\n".join(f"  - {failure}" for failure in failures)
        )


def build_rows(
    *,
    campaign: dict[str, Any],
    validation_path: Path,
    expected_campaign_id: str,
    expected_events: int,
    sqrt_s_gev: float,
) -> dict[str, list[dict[str, str]]]:
    samples = campaign.get("sample_results", [])

    if not isinstance(samples, list):
        raise ValueError("sample_results must be a list")

    ee_samples = [
        row
        for row in samples
        if isinstance(row, dict)
        and row.get("initial_state") == EXPECTED_INITIAL_STATE
    ]

    expected_ids = expected_sample_ids()
    actual_ids = {
        str(row.get("sample_id", ""))
        for row in ee_samples
    }

    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        unexpected = sorted(actual_ids - expected_ids)

        raise ValueError(
            "365 GeV ee sample matrix mismatch:\n"
            f"  missing={missing}\n"
            f"  unexpected={unexpected}"
        )

    if len(ee_samples) != 8:
        raise ValueError(
            f"expected exactly 8 ee samples, found {len(ee_samples)}"
        )

    seeds: dict[int, str] = {}
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    rows_by_spin: dict[str, list[dict[str, str]]] = {
        "sc": [],
        "iso": [],
    }

    for source_row in sorted(
        ee_samples,
        key=lambda row: str(row["sample_id"]),
    ):
        sample_id = str(source_row["sample_id"])
        spin_mode = str(source_row.get("spin_mode", ""))
        decay_channel = str(source_row.get("decay_channel", ""))
        polarization = str(source_row.get("polarization", ""))

        failures: list[str] = []

        if spin_mode not in SPIN_MODES:
            failures.append(f"invalid spin_mode={spin_mode!r}")

        if decay_channel not in DECAY_CHANNELS:
            failures.append(
                f"invalid decay_channel={decay_channel!r}"
            )

        if polarization not in POLARIZATIONS:
            failures.append(
                f"invalid polarization={polarization!r}"
            )

        if source_row.get("validation_status") != "pass":
            failures.append(
                "validation_status is not pass: "
                f"{source_row.get('validation_status')!r}"
            )

        events = int(source_row.get("events", -1))

        if events != expected_events:
            failures.append(
                f"events={events}, expected {expected_events}"
            )

        seed = int(source_row.get("random_seed", -1))

        if seed <= 0:
            failures.append(f"invalid random_seed={seed}")

        if seed in seeds:
            failures.append(
                f"duplicate random_seed={seed} also used by "
                f"{seeds[seed]}"
            )

        cross_section = float(
            source_row.get("cross_section_pb", -1.0)
        )

        cross_section_error = float(
            source_row.get("cross_section_error_pb", -1.0)
        )

        if cross_section <= 0.0:
            failures.append(
                f"invalid cross_section_pb={cross_section}"
            )

        if cross_section_error < 0.0:
            failures.append(
                "invalid cross_section_error_pb="
                f"{cross_section_error}"
            )

        if failures:
            raise ValueError(
                f"{sample_id} validation failed:\n"
                + "\n".join(
                    f"  - {failure}"
                    for failure in failures
                )
            )

        lhe_path = resolve_lhe_path(
            row=source_row,
            campaign=campaign,
            validation_path=validation_path,
        )

        actual_sha256 = sha256(lhe_path)
        expected_sha256 = str(source_row.get("lhe_sha256", ""))

        if actual_sha256 != expected_sha256:
            raise ValueError(
                f"{sample_id}: SHA256 mismatch\n"
                f"  expected={expected_sha256}\n"
                f"  actual={actual_sha256}\n"
                f"  path={lhe_path}"
            )

        actual_events = count_lhe_events(lhe_path)

        if actual_events != expected_events:
            raise ValueError(
                f"{sample_id}: readable LHE event count is "
                f"{actual_events}, expected {expected_events}"
            )

        seeds[seed] = sample_id

        manifest_row = {
            "schema_version": "1",
            "campaign_id": expected_campaign_id,
            "sample_id": sample_id,
            "initial_state": EXPECTED_INITIAL_STATE,
            "decay_channel": decay_channel,
            "polarization": polarization,
            "spin_mode": spin_mode,
            "sqrt_s_GeV": f"{sqrt_s_gev:.1f}",
            "expected_events": str(expected_events),
            "generated_events": str(actual_events),
            "random_seed": str(seed),
            "cross_section_pb": str(
                source_row["cross_section_pb"]
            ),
            "cross_section_error_pb": str(
                source_row["cross_section_error_pb"]
            ),
            "relative_cross_section_error": str(
                source_row["relative_cross_section_error"]
            ),
            "minimum_mtt_GeV": str(
                source_row["minimum_mtt_GeV"]
            ),
            "maximum_mtt_GeV": str(
                source_row["maximum_mtt_GeV"]
            ),
            "mean_mtt_GeV": str(
                source_row["mean_mtt_GeV"]
            ),
            "fraction_below_350_GeV": str(
                source_row["fraction_below_350_GeV"]
            ),
            "unweighting_efficiency_percent": str(
                source_row["unweighting_efficiency_percent"]
            ),
            "merged_final_lhe_path": str(lhe_path),
            "lhe_sha256": actual_sha256,
            "lhe_size_bytes": str(lhe_path.stat().st_size),
            "status": "success",
            "updated_utc": now,
            "source_validation_path": str(validation_path),
        }

        rows_by_spin[spin_mode].append(manifest_row)

    for spin_mode in SPIN_MODES:
        rows = rows_by_spin[spin_mode]

        if len(rows) != 4:
            raise ValueError(
                f"expected 4 {spin_mode} rows, found {len(rows)}"
            )

    return rows_by_spin


def write_csv(
    path: Path,
    rows: list[dict[str, str]],
    *,
    force: bool,
) -> None:
    if path.exists() and not force:
        raise FileExistsError(
            f"manifest already exists: {path}; "
            "use --force to replace it"
        )

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(f".{path.name}.partial")

    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=MANIFEST_FIELDS,
        )
        writer.writeheader()
        writer.writerows(rows)

    temporary.replace(path)


def main() -> int:
    repo = Path(__file__).resolve().parents[2]

    default_validation = (
        repo
        / "runs"
        / EXPECTED_CAMPAIGN_ID
        / "campaign_validation.json"
    )

    default_output_dir = default_validation.parent / "manifests"

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--campaign-validation",
        type=Path,
        default=default_validation,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
    )

    parser.add_argument(
        "--campaign-id",
        default=EXPECTED_CAMPAIGN_ID,
    )

    parser.add_argument(
        "--events-per-sample",
        type=int,
        default=EXPECTED_EVENTS_PER_SAMPLE,
    )

    parser.add_argument(
        "--sqrt-s-gev",
        type=float,
        default=EXPECTED_SQRT_S_GEV,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="validate all source inputs without writing manifests",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="replace existing generated manifests",
    )

    args = parser.parse_args()

    validation_path = args.campaign_validation.expanduser()

    if not validation_path.is_file():
        raise FileNotFoundError(validation_path)

    campaign = load_campaign(validation_path)

    validate_campaign_header(
        campaign,
        expected_campaign_id=args.campaign_id,
    )

    rows_by_spin = build_rows(
        campaign=campaign,
        validation_path=validation_path,
        expected_campaign_id=args.campaign_id,
        expected_events=args.events_per_sample,
        sqrt_s_gev=args.sqrt_s_gev,
    )

    sc_path = args.output_dir / "source_manifest_ee_sc.csv"
    iso_path = args.output_dir / "source_manifest_ee_iso.csv"
    summary_path = (
        args.output_dir
        / "source_manifest_ee_summary.json"
    )

    print(
        "365 GEV EE SOURCE VALIDATION PASS "
        f"samples={sum(len(rows) for rows in rows_by_spin.values())} "
        f"sc={len(rows_by_spin['sc'])} "
        f"iso={len(rows_by_spin['iso'])}"
    )

    for spin_mode in SPIN_MODES:
        for row in rows_by_spin[spin_mode]:
            print(
                f"  {spin_mode.upper()} "
                f"{row['sample_id']} "
                f"events={row['generated_events']} "
                f"seed={row['random_seed']} "
                f"path={row['merged_final_lhe_path']}"
            )

    if args.check:
        print("CHECK MODE: no files written")
        print(f"Proposed SC manifest:  {sc_path}")
        print(f"Proposed ISO manifest: {iso_path}")
        return 0

    write_csv(
        sc_path,
        rows_by_spin["sc"],
        force=args.force,
    )

    write_csv(
        iso_path,
        rows_by_spin["iso"],
        force=args.force,
    )

    summary = {
        "schema_version": 1,
        "campaign_id": args.campaign_id,
        "source_validation": str(validation_path),
        "initial_state": EXPECTED_INITIAL_STATE,
        "sqrt_s_GeV": args.sqrt_s_gev,
        "events_per_sample": args.events_per_sample,
        "samples": 8,
        "spin_correlated_samples": 4,
        "isotropic_samples": 4,
        "spin_correlated_manifest": str(sc_path),
        "isotropic_manifest": str(iso_path),
        "sample_ids": {
            spin_mode: [
                row["sample_id"]
                for row in rows_by_spin[spin_mode]
            ]
            for spin_mode in SPIN_MODES
        },
        "created_utc": dt.datetime.now(
            dt.timezone.utc
        ).isoformat(),
    }

    if summary_path.exists() and not args.force:
        raise FileExistsError(
            f"summary already exists: {summary_path}; "
            "use --force to replace it"
        )

    temporary_summary = summary_path.with_name(
        f".{summary_path.name}.partial"
    )

    temporary_summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True)
        + "\n"
    )

    temporary_summary.replace(summary_path)

    print(f"Wrote {sc_path}")
    print(f"Wrote {iso_path}")
    print(f"Wrote {summary_path}")
    print("365 GEV EE SOURCE MANIFEST GENERATION PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
