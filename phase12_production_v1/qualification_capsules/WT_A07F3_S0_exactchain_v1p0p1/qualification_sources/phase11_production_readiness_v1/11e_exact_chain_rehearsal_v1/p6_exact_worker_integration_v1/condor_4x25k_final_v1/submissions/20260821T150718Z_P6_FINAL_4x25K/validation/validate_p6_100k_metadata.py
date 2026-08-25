#!/usr/bin/env python3

from __future__ import annotations

import collections
import csv
import hashlib
import json
import sys
from pathlib import Path


manifest_path = Path(sys.argv[1])
output_root = Path(sys.argv[2])
sample = sys.argv[3]
snapshot = Path(sys.argv[4])
frozen = Path(sys.argv[5])


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


rows = list(
    csv.DictReader(
        manifest_path.open(),
        delimiter="\t",
    )
)

references = {
    "0": "phase11c_S0_11E_0001_seed311191001",
    "1": "phase11c_S0_11E_0002_seed311191002",
    "2": "phase11c_S0_11E_0003_seed311191003",
    "3": "phase11c_S0_11E_0004_seed311191004",
}

expected_tool_hashes = {
    "canonicalizer_sha256": sha256(
        frozen
        / "helpers"
        / "canonicalize_whizard_lhe_for_pythia.py"
    ),
    "serializer_sha256": sha256(
        frozen
        / "helpers"
        / "reorder_lhe_history_for_pythia_v1.py"
    ),
    "serialization_validator_sha256": sha256(
        frozen
        / "helpers"
        / "validate_lhe_history_serialization_v1.py"
    ),
    "metadata_augmenter_sha256": sha256(
        frozen
        / "helpers"
        / "augment_shower_metadata.py"
    ),
}

required_validation = (
    "PARTICLE_CONTENT_PRESERVATION=PASS",
    "MOTHER_INDEX_REMAP=PASS",
    "MOTHER_BEFORE_CHILD=PASS",
    "DAUGHTER_CONTIGUITY=PASS",
    "HISTORY_SERIALIZATION_VALIDATION=PASS",
)

totals = collections.Counter()
messages = collections.Counter()

overall = len(rows) == 4

print(f"MANIFEST_ROWS={len(rows)}")
print()

for row in rows:
    proc = row["proc"]
    shard = row["shard_id"]

    expected_start = int(row["start"])
    expected_stop = int(row["stop"])
    expected_events = expected_stop - expected_start

    base = f"{sample}__{shard}"

    meta_path = (
        output_root
        / "metadata"
        / sample
        / f"{base}.json"
    )

    prep = (
        output_root
        / "preparation"
        / sample
    )

    canon_summary_path = (
        prep
        / f"{base}.canonical_isr_v2.json"
    )

    serializer_summary_path = (
        prep
        / f"{base}.history_serializer_v1.json"
    )

    validation_path = (
        prep
        / f"{base}.history_serialization_validation.txt"
    )

    hashes_path = (
        prep
        / f"{base}.preparation_hashes.txt"
    )

    hepmc_path = (
        output_root
        / "hepmc3"
        / sample
        / f"{base}.hepmc3"
    )

    ref_stem = references[proc]

    canonical_ref = (
        snapshot
        / "phase11e_relaxed_canonical_100k"
        / "lhe"
        / f"{ref_stem}.canonical_relaxed.lhe"
    )

    serialized_ref = (
        snapshot
        / "phase11e_serialized_candidate_v1"
        / "lhe"
        / f"{ref_stem}.serialized_v1.lhe"
    )

    print("=" * 72)
    print(f"PROC={proc} SHARD={shard}")
    print("=" * 72)

    required_files = (
        meta_path,
        canon_summary_path,
        serializer_summary_path,
        validation_path,
        hashes_path,
        hepmc_path,
        canonical_ref,
        serialized_ref,
    )

    missing = [
        str(path)
        for path in required_files
        if not path.is_file()
    ]

    if missing:
        overall = False

        for path in missing:
            print(f"MISSING={path}")

        print("SHARD_GATE=FAIL")
        continue

    meta = json.loads(
        meta_path.read_text()
    )

    canonical = json.loads(
        canon_summary_path.read_text()
    )

    serializer = json.loads(
        serializer_summary_path.read_text()
    )

    validation = validation_path.read_text()

    prep_hashes = {}

    for line in hashes_path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            prep_hashes[key.strip()] = value.strip()

    ref_canonical_sha = sha256(canonical_ref)
    ref_serialized_sha = sha256(serialized_ref)

    checks = {
        "status_success":
            meta.get("status") == "success",

        "return_code_zero":
            int(meta.get("return_code", -1)) == 0,

        "requested_25000":
            int(meta.get("requested_events", -1))
            == expected_events,

        "attempted_25000":
            int(meta.get("attempted_events", -1))
            == expected_events,

        "accepted_25000":
            int(meta.get("accepted_events", -1))
            == expected_events,

        "failed_zero":
            int(meta.get("failed_events", -1))
            == 0,

        "input_sha":
            meta.get("input_shard_lhe_sha256")
            == row["input_sha256"],

        "explicit_w_off":
            meta.get("explicit_w_adapter_used")
            is False,

        "qed_gamma_off":
            meta.get("qed_shower_by_gamma")
            is False,

        "canonical_events":
            int(canonical.get("total_events", -1))
            == expected_events,

        "serializer_events":
            int(serializer.get("total_events", -1))
            == expected_events,

        "particles_added_zero":
            int(serializer.get("particles_added", -1))
            == 0,

        "particles_removed_zero":
            int(serializer.get("particles_removed", -1))
            == 0,

        "resonances_added_zero":
            int(serializer.get("resonances_added", -1))
            == 0,

        "resonances_removed_zero":
            int(serializer.get("resonances_removed", -1))
            == 0,

        "strict_validation":
            all(
                marker in validation
                for marker in required_validation
            ),

        "canonical_sha_reference":
            prep_hashes.get(
                "canonical_isr_v2_sha256"
            )
            == ref_canonical_sha,

        "serialized_sha_reference":
            prep_hashes.get(
                "history_serialized_v1_sha256"
            )
            == ref_serialized_sha,

        "metadata_prepared_sha_reference":
            meta.get("prepared_lhe_sha256")
            == ref_serialized_sha,

        "unknown_errors_zero":
            int(
                meta["pythia_error_counts"].get(
                    "unknown_error_occurrences",
                    -1,
                )
            )
            == 0,
    }

    source_range = meta.get(
        "source_event_range",
        {},
    )

    checks["source_range"] = (
        int(source_range.get("start", -1))
        == expected_start
        and int(
            source_range.get(
                "stop_exclusive",
                -1,
            )
        )
        == expected_stop
        and int(
            source_range.get("events", -1)
        )
        == expected_events
    )

    tool_hashes = (
        meta
        .get("preparation", {})
        .get("tool_hashes", {})
    )

    checks["frozen_tool_hashes"] = all(
        tool_hashes.get(key) == expected
        for key, expected
        in expected_tool_hashes.items()
    )

    shard_ok = all(checks.values())
    overall &= shard_ok

    for name, passed in checks.items():
        print(
            f"{name}="
            + ("PASS" if passed else "FAIL")
        )

    print(
        "SHARD_GATE="
        + ("PASS" if shard_ok else "FAIL")
    )

    requested = int(meta["requested_events"])
    attempted = int(meta["attempted_events"])
    accepted = int(meta["accepted_events"])
    failed = int(meta["failed_events"])

    pythia_errors = meta["pythia_error_counts"]

    totals["requested"] += requested
    totals["attempted"] += attempted
    totals["accepted"] += accepted
    totals["failed"] += failed

    totals["mec"] += int(
        meta["pythia_warning_counts"].get(
            "me_weight_above_ps",
            0,
        )
    )

    totals["retries"] += int(
        pythia_errors.get(
            "hadron_level_retries",
            0,
        )
    )

    totals["recoverable_errors"] += int(
        pythia_errors.get(
            "known_recoverable_error_occurrences",
            0,
        )
    )

    totals["unknown_errors"] += int(
        pythia_errors.get(
            "unknown_error_occurrences",
            0,
        )
    )

    for message, count in (
        meta
        .get("pythia_message_summary", {})
        .items()
    ):
        messages[message] += int(count)

    print()


print("=" * 72)
print("100K AGGREGATE")
print("=" * 72)

print(f"TOTAL_REQUESTED={totals['requested']}")
print(f"TOTAL_ATTEMPTED={totals['attempted']}")
print(f"TOTAL_ACCEPTED={totals['accepted']}")
print(f"TOTAL_FAILED={totals['failed']}")
print(f"TOTAL_MEC_ABOVE_PS={totals['mec']}")
print(f"TOTAL_HADRON_LEVEL_RETRIES={totals['retries']}")
print(
    "TOTAL_RECOVERABLE_ERROR_OCCURRENCES="
    f"{totals['recoverable_errors']}"
)
print(
    "TOTAL_UNKNOWN_ERROR_OCCURRENCES="
    f"{totals['unknown_errors']}"
)

if totals["accepted"]:
    print(
        "MEC_ABOVE_PS_RATE="
        f"{totals['mec'] / totals['accepted']:.8f}"
    )
    print(
        "HADRON_RETRY_RATE="
        f"{totals['retries'] / totals['accepted']:.8e}"
    )

print()
print("PYTHIA_MESSAGE_SUMMARY")

for message, count in sorted(
    messages.items(),
    key=lambda item: (-item[1], item[0]),
):
    print(f"{count:8d}  {message}")

aggregate_ok = (
    totals["requested"] == 100000
    and totals["attempted"] == 100000
    and totals["accepted"] == 100000
    and totals["failed"] == 0
    and totals["unknown_errors"] == 0
)

overall &= aggregate_ok

print()
print(
    "P6_100K_METADATA_PREPARATION_GATE="
    + ("PASS" if overall else "FAIL")
)

raise SystemExit(
    0 if overall else 1
)
