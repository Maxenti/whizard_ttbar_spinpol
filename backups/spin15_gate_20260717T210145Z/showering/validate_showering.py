#!/usr/bin/env python3
"""Validate PYTHIA8/HepMC3 shower products and run metadata."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def configured_root(config_path: Path) -> tuple[Path, int]:
    payload: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
    campaign = payload.get("campaign", {})
    inputs = payload.get("inputs", {})
    root = Path(str(campaign["output_root"])) / "shower"
    expected = (
        len(inputs.get("allowed_initial_states", []))
        * len(inputs.get("allowed_polarizations", []))
        * len(inputs.get("allowed_decay_channels", []))
    )
    return root, expected


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/qis/level_a_500GeV_ISR_sc_v1.yaml"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--expected", type=int)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--checksums", action="store_true")
    args = parser.parse_args()
    config_root, config_expected = configured_root(args.config)
    root = args.root or config_root
    expected = args.expected if args.expected is not None else config_expected

    metadata_paths = sorted((root / "metadata").glob("*/*.json"))
    output_paths = sorted((root / "hepmc3").glob("*/*.hepmc3"))
    output_by_sample = {path.parent.name: path for path in output_paths}
    checks: list[dict[str, object]] = []

    def add(check: str, sample: str, passed: bool, value: object, detail: str) -> None:
        checks.append({"check": check, "sample_id": sample, "verdict": "PASS" if passed else "FAIL", "value": value, "detail": detail})

    add("metadata_count", "—", len(metadata_paths) == expected, len(metadata_paths), f"expected {expected}")
    add("output_count", "—", len(output_paths) == expected, len(output_paths), f"expected {expected}")

    for metadata_path in metadata_paths:
        sample = metadata_path.parent.name
        try:
            data = json.loads(metadata_path.read_text())
        except Exception as exc:
            add("metadata_parse", sample, False, type(exc).__name__, str(exc))
            continue
        output = output_by_sample.get(sample)
        add("metadata_status", sample, data.get("status") == "success", data.get("status"), "must be success")
        add("return_code", sample, int(data.get("return_code", 1)) == 0, data.get("return_code"), "must be zero")
        accepted = int(data.get("accepted_events", 0))
        requested = int(data.get("requested_events", -1))
        add("accepted_events", sample, accepted > 0, accepted, "must be positive")
        if requested > 0:
            add("requested_events", sample, accepted == requested, f"{accepted}/{requested}", "accepted must equal requested")
        add("output_exists", sample, output is not None and output.is_file() and output.stat().st_size > 0,
            str(output) if output else "missing", "non-empty HepMC3 required")
        add("version_metadata", sample, bool(data.get("pythia_version")) and bool(data.get("hepmc_version")),
            f"PYTHIA={data.get('pythia_version')} HepMC={data.get('hepmc_version')}", "both versions required")

    failures = [row for row in checks if row["verdict"] == "FAIL"]
    validation_dir = root / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    csv_path = validation_dir / "showering_validation.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["check", "sample_id", "verdict", "value", "detail"])
        writer.writeheader()
        writer.writerows(checks)
    if args.checksums:
        checksum_path = root / "manifests/hepmc3_sha256.txt"
        checksum_path.parent.mkdir(parents=True, exist_ok=True)
        checksum_path.write_text("".join(f"{sha256(path)}  {path}\n" for path in output_paths))
    report = validation_dir / "showering_validation.md"
    report.write_text(
        "# Shower validation\n\n"
        f"- Root: `{root}`\n"
        f"- Expected samples: {expected}\n"
        f"- Metadata files: {len(metadata_paths)}\n"
        f"- HepMC3 files: {len(output_paths)}\n"
        f"- Checks: {len(checks)}\n"
        f"- PASS: {len(checks) - len(failures)}\n"
        f"- FAIL: {len(failures)}\n\n"
        + ("All checks passed.\n" if not failures else "## Failures\n\n" + "\n".join(f"- `{x['sample_id']}` {x['check']}: {x['value']} ({x['detail']})" for x in failures) + "\n")
    )
    print(f"Wrote {csv_path}")
    print(f"Wrote {report}")
    print(f"Checks={len(checks)} PASS={len(checks)-len(failures)} FAIL={len(failures)}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
