#!/usr/bin/env python3
"""Augment shower metadata with deterministic LHE-shard provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def warning_count(text: str, message: str) -> int:
    pattern = re.compile(
        rf"^\s*\|\s*(\d+)\s+Warning in {re.escape(message)}",
        re.MULTILINE,
    )
    found = pattern.findall(text)
    if found:
        return int(found[-1])
    return text.count(f"Warning in {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--input-shard", required=True, type=Path)
    parser.add_argument("--input-shard-path", required=True)
    parser.add_argument("--input-shard-expected-sha256", required=True)
    parser.add_argument("--parent-lhe-path", required=True)
    parser.add_argument("--source-event-start", required=True, type=int)
    parser.add_argument("--source-event-stop-exclusive", required=True, type=int)
    parser.add_argument("--expected-events", required=True, type=int)
    parser.add_argument("--canonical-summary", required=True, type=Path)
    parser.add_argument("--explicit-w-summary", required=True, type=Path)
    parser.add_argument("--worker-log", required=True, type=Path)
    parser.add_argument(
        "--qed-shower-by-gamma", required=True, choices=("on", "off")
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    for path in (
        args.metadata,
        args.input_shard,
        args.canonical_summary,
        args.explicit_w_summary,
        args.worker_log,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.source_event_start < 0:
        raise ValueError("source-event-start must be non-negative")
    if args.source_event_stop_exclusive <= args.source_event_start:
        raise ValueError("source-event-stop-exclusive must exceed start")
    if (
        args.source_event_stop_exclusive - args.source_event_start
        != args.expected_events
    ):
        raise ValueError("source event range does not match expected-events")

    metadata = json.loads(args.metadata.read_text())
    canonical = json.loads(args.canonical_summary.read_text())
    explicit_w = json.loads(args.explicit_w_summary.read_text())
    log_text = args.worker_log.read_text(errors="replace")
    actual_shard_sha = sha256(args.input_shard)
    if actual_shard_sha != args.input_shard_expected_sha256:
        raise ValueError(
            "input shard checksum changed between submit and metadata stages"
        )

    accepted = int(metadata.get("accepted_events", -1))
    requested = int(metadata.get("requested_events", -1))
    canonical_events = int(canonical.get("total_events", -1))
    explicit_events = int(explicit_w.get("total_events", -1))
    if not (
        accepted
        == requested
        == canonical_events
        == explicit_events
        == args.expected_events
    ):
        raise ValueError(
            "event-count contract failure: "
            f"accepted={accepted} requested={requested} "
            f"canonical={canonical_events} explicit_w={explicit_events} "
            f"expected={args.expected_events}"
        )

    metadata.update(
        {
            "source_lhe_path": args.parent_lhe_path,
            "input_shard_lhe_path": args.input_shard_path,
            "input_shard_lhe_sha256": actual_shard_sha,
            "source_event_range": {
                "start": args.source_event_start,
                "stop_exclusive": args.source_event_stop_exclusive,
                "events": args.expected_events,
            },
            "prepared_lhe_policy": (
                "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3"
            ),
            "preparation_event_limit_verified": True,
            "qed_shower_by_gamma": args.qed_shower_by_gamma == "on",
            "photon_conversion_policy": (
                "pythia_default_on"
                if args.qed_shower_by_gamma == "on"
                else "generator_systematic_off"
            ),
            "preparation": {
                "canonical_v2": canonical,
                "explicit_w_v3": explicit_w,
            },
            "pythia_warning_counts": {
                "me_weight_above_ps": warning_count(
                    log_text,
                    "SimpleTimeShower::findMEcorr: ME weight above PS one",
                ),
                "negative_dipole_mass": warning_count(
                    log_text,
                    "SimpleTimeShower::pTnext: negative dipole mass",
                ),
            },
            "pythia_warning_policy": {
                "me_weight_above_ps": "must_be_zero_for_explicit_w_v3",
                "negative_dipole_mass": (
                    "count_and_monitor_nonfatal_gamma_conversion_trials"
                    if args.qed_shower_by_gamma == "on"
                    else "must_be_zero_when_gamma_conversion_is_off"
                ),
            },
        }
    )

    output = args.output or args.metadata
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.partial")
    temporary.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    temporary.replace(output)
    print(
        "METADATA AUGMENTED "
        f"events={args.expected_events} "
        f"range=[{args.source_event_start},{args.source_event_stop_exclusive}) "
        f"inserted_w={explicit_w.get('inserted_w_resonances')} "
        f"qed_shower_by_gamma={args.qed_shower_by_gamma} "
        f"output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
