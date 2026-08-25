#!/usr/bin/env python3
"""Phase 7 shower-handoff and HepMC identity/runtime validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ttbar_spinpol.genchain.identity import global_event_id
from ttbar_spinpol.genchain.phase_records import write_phase_record
from ttbar_spinpol.genchain.yamlio import load_yaml


def count_lhe_events(path: Path) -> int:
    return sum(
        1
        for line in path.open("r", encoding="utf-8", errors="replace")
        if "<event>" in line
    )


def count_hepmc_events(path: Path) -> int:
    return sum(
        1
        for line in path.open("r", encoding="utf-8", errors="replace")
        if line.startswith("E ")
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--lhe", type=Path, default=None)
    parser.add_argument("--canonical-summary", type=Path, default=None)
    parser.add_argument("--hepmc", type=Path, default=None)
    parser.add_argument("--metadata", type=Path, default=None)
    args = parser.parse_args()

    repo = args.repo.resolve()

    handoff = load_yaml(repo / "analysis_contracts/shower_handoff_contract.yaml")
    identity = load_yaml(repo / "analysis_contracts/hepmc_event_identity_contract.yaml")

    errors: list[str] = []
    warnings: list[str] = []

    if handoff.get("handoff_policy", {}).get("output_format") != "HepMC3":
        errors.append("handoff output format must be HepMC3")

    if not handoff.get("handoff_policy", {}).get("event_identity_preservation_required"):
        errors.append("event identity preservation must be required")

    if global_event_id("campaign", "sample", "sub", "unpol", "shard", 1) != global_event_id(
        "campaign", "sample", "sub", "unpol", "shard", 1
    ):
        errors.append("global event ID not deterministic")

    runtime_status = "INCOMPLETE_LHE_INPUT"

    lhe_events = None
    hepmc_events = None
    canonical_summary = None
    metadata = None

    if args.lhe is None:
        warnings.append("no LHE file supplied; runtime handoff validation remains incomplete")
    elif not args.lhe.is_file():
        runtime_status = "FAIL"
        errors.append(f"LHE file does not exist: {args.lhe}")
    else:
        runtime_status = "STATIC_LHE_PRESENT_NOT_SHOWERED"
        lhe_events = count_lhe_events(args.lhe)

    if args.canonical_summary is not None:
        if not args.canonical_summary.is_file():
            errors.append(f"canonical summary does not exist: {args.canonical_summary}")
        else:
            canonical_summary = load_json(args.canonical_summary)
            if canonical_summary.get("total_events") != lhe_events:
                errors.append(
                    "canonical summary total_events does not match LHE event count: "
                    f"{canonical_summary.get('total_events')} != {lhe_events}"
                )
            if canonical_summary.get("max_abs_closure_gev", 0.0) > 1.0e-5:
                warnings.append(
                    "canonical summary has max_abs_closure_gev above conservative bridge threshold: "
                    f"{canonical_summary.get('max_abs_closure_gev')}"
                )

    if args.hepmc is not None or args.metadata is not None:
        runtime_status = "HEPMC_RUNTIME_BRIDGE_PRESENT"

        if args.hepmc is None or not args.hepmc.is_file():
            errors.append(f"HepMC file does not exist: {args.hepmc}")
        else:
            hepmc_events = count_hepmc_events(args.hepmc)

        if args.metadata is None or not args.metadata.is_file():
            errors.append(f"HepMC metadata file does not exist: {args.metadata}")
        else:
            metadata = load_json(args.metadata)

    if metadata is not None:
        if metadata.get("status") != "success":
            errors.append(f"metadata status is not success: {metadata.get('status')}")
        if metadata.get("return_code") != 0:
            errors.append(f"metadata return_code is not 0: {metadata.get('return_code')}")
        if metadata.get("accepted_events", 0) <= 0:
            errors.append("metadata accepted_events is not positive")
        if metadata.get("failed_events", 0) != 0:
            warnings.append(f"metadata failed_events is nonzero: {metadata.get('failed_events')}")

        if hepmc_events is not None and metadata.get("accepted_events") != hepmc_events:
            errors.append(
                "HepMC event count does not match metadata accepted_events: "
                f"{hepmc_events} != {metadata.get('accepted_events')}"
            )

        if lhe_events is not None and metadata.get("accepted_events") != lhe_events:
            warnings.append(
                "metadata accepted_events does not match supplied LHE event count: "
                f"{metadata.get('accepted_events')} != {lhe_events}"
            )

        if metadata.get("pythia_version") != "8.316":
            errors.append(f"unexpected PYTHIA version: {metadata.get('pythia_version')}")
        if metadata.get("hepmc_version") != "3.03.01":
            errors.append(f"unexpected HepMC3 version: {metadata.get('hepmc_version')}")

    status = "PASS" if not errors else "FAIL"

    out = write_phase_record(
        repo,
        "phase7_shower_handoff_static",
        status,
        {
            "runtime_status": runtime_status,
            "errors": errors,
            "warnings": warnings,
            "identity_algorithm": identity.get("global_event_id", {}).get("algorithm"),
            "lhe": str(args.lhe) if args.lhe else None,
            "lhe_events": lhe_events,
            "canonical_summary": str(args.canonical_summary) if args.canonical_summary else None,
            "hepmc": str(args.hepmc) if args.hepmc else None,
            "hepmc_events": hepmc_events,
            "metadata": str(args.metadata) if args.metadata else None,
            "metadata_status": metadata.get("status") if metadata else None,
            "accepted_events": metadata.get("accepted_events") if metadata else None,
            "pythia_version": metadata.get("pythia_version") if metadata else None,
            "hepmc_version": metadata.get("hepmc_version") if metadata else None,
        },
        [
            "PHASE 7 SHOWER/HepMC IDENTITY AND RUNTIME VALIDATION",
            "=" * 72,
            f"STATUS: {status}",
            f"RUNTIME_STATUS: {runtime_status}",
            f"LHE_EVENTS: {lhe_events}",
            f"HEPMC_EVENTS: {hepmc_events}",
            f"ERRORS: {len(errors)}",
            f"WARNINGS: {len(warnings)}",
        ],
    )

    print(out)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
