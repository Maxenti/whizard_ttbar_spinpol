#!/usr/bin/env python3
"""Validate PYTHIA8/HepMC3 shower products and preparation provenance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

EXPECTED_PREPARATION_POLICY = (
    "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3"
)


def configured_root(config_path: Path) -> tuple[Path, int, dict[str, Any]]:
    payload: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
    campaign = payload.get("campaign", {})
    inputs = payload.get("inputs", {})
    showering = payload.get("showering", {})
    root = Path(str(campaign["output_root"])) / "shower"
    expected = (
        len(inputs.get("allowed_initial_states", []))
        * len(inputs.get("allowed_polarizations", []))
        * len(inputs.get("allowed_decay_channels", []))
    )
    return root, expected, showering


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qis/level_a_500GeV_ISR_sc_v1.yaml"),
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument("--expected", type=int)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--checksums", action="store_true")
    args = parser.parse_args()

    config_root, config_expected, shower_cfg = configured_root(args.config)
    root = args.root or config_root
    expected = args.expected if args.expected is not None else config_expected
    expected_qed_gamma = bool(shower_cfg.get("qed_shower_by_gamma", True))
    expected_policy = str(
        shower_cfg.get("lhe_preparation_policy", EXPECTED_PREPARATION_POLICY)
    )
    expected_events = int(shower_cfg.get("events_per_job", -1))

    metadata_paths = sorted((root / "metadata").glob("*/*.json"))
    output_paths = sorted((root / "hepmc3").glob("*/*.hepmc3"))
    output_by_sample = {path.parent.name: path for path in output_paths}
    checks: list[dict[str, object]] = []

    def add(
        check: str,
        sample: str,
        passed: bool,
        value: object,
        detail: str,
    ) -> None:
        checks.append(
            {
                "check": check,
                "sample_id": sample,
                "verdict": "PASS" if passed else "FAIL",
                "value": value,
                "detail": detail,
            }
        )

    add(
        "metadata_count",
        "—",
        len(metadata_paths) == expected,
        len(metadata_paths),
        f"expected {expected}",
    )
    add(
        "output_count",
        "—",
        len(output_paths) == expected,
        len(output_paths),
        f"expected {expected}",
    )

    warning_totals = {
        "me_weight_above_ps": 0,
        "negative_dipole_mass": 0,
    }

    for metadata_path in metadata_paths:
        sample = metadata_path.parent.name
        try:
            data = json.loads(metadata_path.read_text())
        except Exception as exc:
            add("metadata_parse", sample, False, type(exc).__name__, str(exc))
            continue

        output = output_by_sample.get(sample)
        add(
            "metadata_status",
            sample,
            data.get("status") == "success",
            data.get("status"),
            "must be success",
        )
        add(
            "return_code",
            sample,
            int(data.get("return_code", 1)) == 0,
            data.get("return_code"),
            "must be zero",
        )
        accepted = int(data.get("accepted_events", 0))
        requested = int(data.get("requested_events", -1))
        add("accepted_events", sample, accepted > 0, accepted, "must be positive")
        if requested > 0:
            add(
                "requested_events",
                sample,
                accepted == requested,
                f"{accepted}/{requested}",
                "accepted must equal requested",
            )
        if expected_events > 0:
            add(
                "configured_events",
                sample,
                accepted == expected_events,
                f"{accepted}/{expected_events}",
                "accepted must equal showering.events_per_job",
            )
        add(
            "output_exists",
            sample,
            output is not None and output.is_file() and output.stat().st_size > 0,
            str(output) if output else "missing",
            "non-empty HepMC3 required",
        )
        add(
            "version_metadata",
            sample,
            bool(data.get("pythia_version")) and bool(data.get("hepmc_version")),
            f"PYTHIA={data.get('pythia_version')} "
            f"HepMC={data.get('hepmc_version')}",
            "both versions required",
        )
        add(
            "source_lhe_provenance",
            sample,
            bool(data.get("source_lhe_path"))
            and len(str(data.get("source_lhe_sha256", ""))) == 64,
            data.get("source_lhe_path", "missing"),
            "persistent source path and SHA256 required",
        )
        add(
            "prepared_lhe_policy",
            sample,
            data.get("prepared_lhe_policy") == expected_policy,
            data.get("prepared_lhe_policy"),
            f"expected {expected_policy}",
        )
        add(
            "qed_shower_by_gamma",
            sample,
            bool(data.get("qed_shower_by_gamma")) == expected_qed_gamma,
            data.get("qed_shower_by_gamma"),
            f"expected {expected_qed_gamma}",
        )

        preparation = data.get("preparation", {})
        canonical = preparation.get("canonical_v2", {}) if isinstance(preparation, dict) else {}
        explicit_w = preparation.get("explicit_w_v3", {}) if isinstance(preparation, dict) else {}
        canonical_events = int(canonical.get("total_events", -1))
        v3_events = int(explicit_w.get("total_events", -1))
        inserted_w = int(explicit_w.get("inserted_w_resonances", -1))
        add(
            "canonical_v2_events",
            sample,
            canonical_events == accepted,
            canonical_events,
            f"must equal accepted events {accepted}",
        )
        add(
            "explicit_w_v3_events",
            sample,
            v3_events == accepted,
            v3_events,
            f"must equal accepted events {accepted}",
        )
        add(
            "inserted_w_resonances",
            sample,
            inserted_w == 2 * accepted,
            inserted_w,
            f"expected {2 * accepted}",
        )
        add(
            "canonical_closure",
            sample,
            float(canonical.get("max_rel_closure", float("inf"))) <= 1.0e-7,
            canonical.get("max_rel_closure"),
            "max relative closure must be <= 1e-7",
        )
        add(
            "explicit_w_vertex_closure",
            sample,
            float(explicit_w.get("max_vertex_rel_closure", float("inf")))
            <= 1.0e-7,
            explicit_w.get("max_vertex_rel_closure"),
            "max relative vertex closure must be <= 1e-7",
        )

        warning_counts = data.get("pythia_warning_counts", {})
        me_warnings = int(warning_counts.get("me_weight_above_ps", -1))
        negative_warnings = int(warning_counts.get("negative_dipole_mass", -1))
        if me_warnings >= 0:
            warning_totals["me_weight_above_ps"] += me_warnings
        if negative_warnings >= 0:
            warning_totals["negative_dipole_mass"] += negative_warnings
        add(
            "explicit_w_me_warning_count",
            sample,
            me_warnings == 0,
            me_warnings,
            "explicit-W v3 must remove findMEcorr warnings",
        )
        add(
            "negative_dipole_warning_count",
            sample,
            negative_warnings >= 0
            and (expected_qed_gamma or negative_warnings == 0),
            negative_warnings,
            (
                "counted nonfatal gamma-conversion trials"
                if expected_qed_gamma
                else "must be zero with QEDshowerByGamma=off"
            ),
        )

        base = metadata_path.stem
        prep_dir = root / "preparation" / sample
        add(
            "canonical_summary_staged",
            sample,
            (prep_dir / f"{base}.canonical_v2.json").is_file(),
            str(prep_dir / f"{base}.canonical_v2.json"),
            "staged preparation summary required",
        )
        add(
            "explicit_w_summary_staged",
            sample,
            (prep_dir / f"{base}.explicit_w_v3.json").is_file(),
            str(prep_dir / f"{base}.explicit_w_v3.json"),
            "staged preparation summary required",
        )

    failures = [row for row in checks if row["verdict"] == "FAIL"]
    validation_dir = root / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    csv_path = validation_dir / "showering_validation.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["check", "sample_id", "verdict", "value", "detail"],
        )
        writer.writeheader()
        writer.writerows(checks)

    if args.checksums:
        checksum_path = root / "manifests/hepmc3_sha256.txt"
        checksum_path.parent.mkdir(parents=True, exist_ok=True)
        checksum_path.write_text(
            "".join(f"{sha256(path)}  {path}\n" for path in output_paths)
        )

    report = validation_dir / "showering_validation.md"
    report.write_text(
        "# Shower validation\n\n"
        f"- Root: `{root}`\n"
        f"- Expected samples: {expected}\n"
        f"- Metadata files: {len(metadata_paths)}\n"
        f"- HepMC3 files: {len(output_paths)}\n"
        f"- Preparation policy: `{expected_policy}`\n"
        f"- `TimeShower:QEDshowerByGamma`: "
        f"`{'on' if expected_qed_gamma else 'off'}`\n"
        f"- Total ME warnings: {warning_totals['me_weight_above_ps']}\n"
        f"- Total negative-dipole warnings: "
        f"{warning_totals['negative_dipole_mass']}\n"
        f"- Checks: {len(checks)}\n"
        f"- PASS: {len(checks) - len(failures)}\n"
        f"- FAIL: {len(failures)}\n\n"
        + (
            "All checks passed.\n"
            if not failures
            else "## Failures\n\n"
            + "\n".join(
                f"- `{row['sample_id']}` {row['check']}: "
                f"{row['value']} ({row['detail']})"
                for row in failures
            )
            + "\n"
        )
    )
    print(f"Wrote {csv_path}")
    print(f"Wrote {report}")
    print(
        f"Checks={len(checks)} PASS={len(checks)-len(failures)} "
        f"FAIL={len(failures)}"
    )
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
