#!/usr/bin/env python3
"""Augment shower metadata with deterministic P6 LHE preparation provenance."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


SUMMARY_ROW_RE = re.compile(
    r"(?m)^\s*\|\s*"
    r"(\d+)\s+"
    r"((?:Warning|Error) in .+?)"
    r"\s+\|\s*$"
)

LIVE_ERROR_RE = re.compile(
    r"(?m)^\s*PYTHIA Error in (.+)$"
)

KNOWN_RECOVERABLE_ERRORS = {
    (
        "Error in MiniStringFragmentation::fragment: "
        "no 1- or 2-body state found above mass threshold"
    ),
    (
        "Error in LundFragmentation::fragment: "
        "ministring fragmentation failed"
    ),
    (
        "Error in Pythia::next: "
        "hadronLevel failed; try again"
    ),
}

HADRON_RETRY_MESSAGE = (
    "Error in Pythia::next: "
    "hadronLevel failed; try again"
)

MEC_WARNING_MESSAGE = (
    "Warning in SimpleTimeShower::findMEcorr: "
    "ME weight above PS one"
)

NEGATIVE_DIPOLE_WARNING_MESSAGE = (
    "Warning in SimpleTimeShower::pTnext: "
    "negative dipole mass"
)

REQUIRED_VALIDATION_MARKERS = (
    "PARTICLE_CONTENT_PRESERVATION",
    "MOTHER_INDEX_REMAP",
    "MOTHER_BEFORE_CHILD",
    "DAUGHTER_CONTIGUITY",
    "HISTORY_SERIALIZATION_VALIDATION",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def parse_summary_counts(
    text: str,
) -> collections.Counter[str]:
    result: collections.Counter[str] = (
        collections.Counter()
    )

    for count, message in SUMMARY_ROW_RE.findall(
        text
    ):
        result[message.strip()] += int(count)

    return result


def occurrence_count(
    summary: collections.Counter[str],
    text: str,
    message: str,
) -> int:
    if message in summary:
        return int(summary[message])

    return text.count(
        f"PYTHIA {message}"
    )


def parse_validation(
    path: Path,
) -> dict[str, object]:
    result: dict[str, object] = {}

    for raw in path.read_text(
        errors="replace"
    ).splitlines():
        if "=" not in raw:
            continue

        key, value = raw.split(
            "=",
            1,
        )

        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if re.fullmatch(
            r"[+-]?\d+",
            value,
        ):
            result[key] = int(value)
        else:
            result[key] = value

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--metadata",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--input-shard",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--input-shard-path",
        required=True,
    )

    parser.add_argument(
        "--input-shard-expected-sha256",
        required=True,
    )

    parser.add_argument(
        "--parent-lhe-path",
        required=True,
    )

    parser.add_argument(
        "--source-event-start",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--source-event-stop-exclusive",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--expected-events",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--canonical-lhe",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--canonical-summary",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--serialized-lhe",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--serializer-summary",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--serialization-validation",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--canonicalizer-tool",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--serializer-tool",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--serialization-validator-tool",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--metadata-augmenter-tool",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--worker-log",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--qed-shower-by-gamma",
        required=True,
        choices=("on", "off"),
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    args = parser.parse_args()

    required_files = (
        args.metadata,
        args.input_shard,
        args.canonical_lhe,
        args.canonical_summary,
        args.serialized_lhe,
        args.serializer_summary,
        args.serialization_validation,
        args.canonicalizer_tool,
        args.serializer_tool,
        args.serialization_validator_tool,
        args.metadata_augmenter_tool,
        args.worker_log,
    )

    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(path)

    if args.expected_events <= 0:
        raise ValueError(
            "expected-events must be positive"
        )

    if args.source_event_start < 0:
        raise ValueError(
            "source-event-start must be non-negative"
        )

    if (
        args.source_event_stop_exclusive
        <= args.source_event_start
    ):
        raise ValueError(
            "source-event-stop-exclusive "
            "must exceed start"
        )

    if (
        args.source_event_stop_exclusive
        - args.source_event_start
        != args.expected_events
    ):
        raise ValueError(
            "source event range does not match "
            "expected-events"
        )

    metadata = json.loads(
        args.metadata.read_text()
    )

    canonical = json.loads(
        args.canonical_summary.read_text()
    )

    serializer = json.loads(
        args.serializer_summary.read_text()
    )

    validation = parse_validation(
        args.serialization_validation
    )

    log_text = args.worker_log.read_text(
        errors="replace"
    )

    actual_shard_sha = sha256(
        args.input_shard
    )

    if (
        actual_shard_sha
        != args.input_shard_expected_sha256
    ):
        raise ValueError(
            "input shard checksum changed between "
            "submit and metadata stages"
        )

    expected = args.expected_events

    status = metadata.get(
        "status"
    )

    return_code = int(
        metadata.get(
            "return_code",
            -1,
        )
    )

    requested = int(
        metadata.get(
            "requested_events",
            -1,
        )
    )

    attempted = int(
        metadata.get(
            "attempted_events",
            -1,
        )
    )

    accepted = int(
        metadata.get(
            "accepted_events",
            -1,
        )
    )

    failed = int(
        metadata.get(
            "failed_events",
            -1,
        )
    )

    canonical_events = int(
        canonical.get(
            "total_events",
            -1,
        )
    )

    serializer_events = int(
        serializer.get(
            "total_events",
            -1,
        )
    )

    validation_events = int(
        validation.get(
            "EVENTS_CHECKED",
            -1,
        )
    )

    event_contract_ok = (
        status == "success"
        and return_code == 0
        and requested == expected
        and attempted == expected
        and accepted == expected
        and failed == 0
        and canonical_events == expected
        and serializer_events == expected
        and validation_events == expected
    )

    if not event_contract_ok:
        raise ValueError(
            "event-count/status contract failure: "
            f"status={status!r} "
            f"return_code={return_code} "
            f"requested={requested} "
            f"attempted={attempted} "
            f"accepted={accepted} "
            f"failed={failed} "
            f"canonical={canonical_events} "
            f"serializer={serializer_events} "
            f"validation={validation_events} "
            f"expected={expected}"
        )

    zero_fields = (
        "particles_added",
        "particles_removed",
        "resonances_added",
        "resonances_removed",
    )

    for field in zero_fields:
        value = int(
            serializer.get(
                field,
                -1,
            )
        )

        if value != 0:
            raise ValueError(
                f"serializer invariant failure: "
                f"{field}={value}"
            )

    for marker in REQUIRED_VALIDATION_MARKERS:
        value = validation.get(
            marker
        )

        if value != "PASS":
            raise ValueError(
                "serialization validation failure: "
                f"{marker}={value!r}"
            )

    summary = parse_summary_counts(
        log_text
    )

    summary_errors = {
        message: int(count)
        for message, count in summary.items()
        if message.startswith(
            "Error in "
        )
    }

    unknown_summary_errors = {
        message: count
        for message, count
        in summary_errors.items()
        if message
        not in KNOWN_RECOVERABLE_ERRORS
    }

    live_errors = [
        f"Error in {message.strip()}"
        for message
        in LIVE_ERROR_RE.findall(
            log_text
        )
    ]

    unknown_live_errors = sorted(
        {
            message
            for message in live_errors
            if message
            not in KNOWN_RECOVERABLE_ERRORS
        }
    )

    if (
        unknown_summary_errors
        or unknown_live_errors
    ):
        raise ValueError(
            "unknown PYTHIA error class observed: "
            f"summary={unknown_summary_errors} "
            f"live={unknown_live_errors}"
        )

    known_recoverable_error_occurrences = sum(
        count
        for message, count
        in summary_errors.items()
        if message
        in KNOWN_RECOVERABLE_ERRORS
    )

    hadron_retries = occurrence_count(
        summary,
        log_text,
        HADRON_RETRY_MESSAGE,
    )

    mec_above_ps = occurrence_count(
        summary,
        log_text,
        MEC_WARNING_MESSAGE,
    )

    negative_dipole_mass = occurrence_count(
        summary,
        log_text,
        NEGATIVE_DIPOLE_WARNING_MESSAGE,
    )

    canonical_sha = sha256(
        args.canonical_lhe
    )

    serialized_sha = sha256(
        args.serialized_lhe
    )

    tool_hashes = {
        "canonicalizer_sha256": sha256(
            args.canonicalizer_tool
        ),
        "serializer_sha256": sha256(
            args.serializer_tool
        ),
        "serialization_validator_sha256": (
            sha256(
                args.serialization_validator_tool
            )
        ),
        "metadata_augmenter_sha256": sha256(
            args.metadata_augmenter_tool
        ),
    }

    metadata.update(
        {
            "source_lhe_path": (
                args.parent_lhe_path
            ),
            "input_shard_lhe_path": (
                args.input_shard_path
            ),
            "input_shard_lhe_sha256": (
                actual_shard_sha
            ),
            "source_event_range": {
                "start": (
                    args.source_event_start
                ),
                "stop_exclusive": (
                    args.source_event_stop_exclusive
                ),
                "events": expected,
            },
            "prepared_lhe_policy": (
                "whizard_extended_isr_to_"
                "canonical_lha_v2_"
                "history_preserving_serializer_v1"
            ),
            "prepared_lhe_sha256": (
                serialized_sha
            ),
            "preparation_event_limit_verified": (
                True
            ),
            "explicit_w_adapter_used": False,
            "qed_shower_by_gamma": (
                args.qed_shower_by_gamma
                == "on"
            ),
            "photon_conversion_policy": (
                "pythia_default_on"
                if args.qed_shower_by_gamma
                == "on"
                else "generator_systematic_off"
            ),
            "preparation": {
                "canonical_isr_v2": (
                    canonical
                ),
                "canonical_isr_lhe_sha256": (
                    canonical_sha
                ),
                "history_serializer_v1": (
                    serializer
                ),
                "history_serialized_lhe_sha256": (
                    serialized_sha
                ),
                "history_serialization_validation": (
                    validation
                ),
                "tool_hashes": tool_hashes,
            },
            "pythia_warning_counts": {
                "me_weight_above_ps": (
                    mec_above_ps
                ),
                "negative_dipole_mass": (
                    negative_dipole_mass
                ),
            },
            "pythia_warning_policy": {
                "me_weight_above_ps": (
                    "count_and_monitor_nonfatal"
                ),
                "negative_dipole_mass": (
                    "count_and_monitor_nonfatal_"
                    "gamma_conversion_trials"
                    if args.qed_shower_by_gamma
                    == "on"
                    else (
                        "expected_zero_when_"
                        "gamma_conversion_is_off"
                    )
                ),
            },
            "pythia_error_counts": {
                "summary_error_occurrences": (
                    sum(
                        summary_errors.values()
                    )
                ),
                "known_recoverable_error_occurrences": (
                    known_recoverable_error_occurrences
                ),
                "hadron_level_retries": (
                    hadron_retries
                ),
                "unknown_error_occurrences": 0,
            },
            "pythia_error_policy": {
                "known_hadronization_retry_chain": (
                    "allowed_if_pythia_returns_"
                    "success_and_no_events_are_lost"
                ),
                "unknown_error_classes": (
                    "rejected_by_metadata_augmenter"
                ),
            },
            "pythia_message_summary": {
                message: int(count)
                for message, count
                in sorted(
                    summary.items()
                )
            },
        }
    )

    output = (
        args.output
        or args.metadata
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = output.with_name(
        f".{output.name}.partial"
    )

    temporary.write_text(
        json.dumps(
            metadata,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    temporary.replace(
        output
    )

    print(
        "METADATA AUGMENTED "
        f"events={expected} "
        f"range=["
        f"{args.source_event_start},"
        f"{args.source_event_stop_exclusive}) "
        f"reordered="
        f"{serializer.get('reordered_events')} "
        f"hadron_retries={hadron_retries} "
        f"mec_above_ps={mec_above_ps} "
        f"qed_shower_by_gamma="
        f"{args.qed_shower_by_gamma} "
        f"output={output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
