#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


manifest_path = Path(sys.argv[1])
output_root = Path(sys.argv[2])
sample_id = sys.argv[3]

EXPECTED_EVENTS = 25000
EXPECTED_SEED = 812100001
EXPECTED_SHA = (
    "8f4ea4e309d1169eb4697dc658361e417"
    "d6ef894ca2332871d278d07d4f47ff7"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


rows = list(
    csv.DictReader(
        manifest_path.open(),
        delimiter="\t",
    )
)

overall = True
summary = []

for row in rows:

    variant = row["variant"]
    gamma_expected = row["gamma_conversion"] == "on"
    hadron_expected = row["hadron_level_qed"]

    root = output_root / variant

    metadata_dir = root / "metadata" / sample_id
    hepmc_dir = root / "hepmc3" / sample_id

    metadata_files = sorted(metadata_dir.glob("*.json"))
    hepmc_files = sorted(hepmc_dir.glob("*.hepmc3"))

    file_ok = (
        len(metadata_files) == 1
        and len(hepmc_files) == 1
    )

    if not file_ok:
        print(
            f"{variant}: FILE_CONTRACT=FAIL "
            f"metadata={len(metadata_files)} "
            f"hepmc={len(hepmc_files)}"
        )
        overall = False
        continue

    meta_path = metadata_files[0]
    hepmc_path = hepmc_files[0]

    meta = json.loads(meta_path.read_text())

    metadata_ok = all(
        [
            meta.get("status") == "success",
            int(meta.get("return_code", -1)) == 0,
            int(meta.get("requested_events", -1))
            == EXPECTED_EVENTS,
            int(meta.get("attempted_events", -1))
            == EXPECTED_EVENTS,
            int(meta.get("accepted_events", -1))
            == EXPECTED_EVENTS,
            int(meta.get("failed_events", -1)) == 0,
            int(meta.get("seed", -1)) == EXPECTED_SEED,
            meta.get("input_shard_lhe_sha256")
            == EXPECTED_SHA,
            bool(meta.get("qed_shower_by_gamma"))
            == gamma_expected,
            int(
                meta.get(
                    "pythia_error_counts",
                    {},
                ).get(
                    "unknown_error_occurrences",
                    -1,
                )
            )
            == 0,
        ]
    )

    card_path = Path(meta["settings_path"])

    card_text = (
        card_path.read_text()
        if card_path.is_file()
        else ""
    )

    gamma_line = (
        "TimeShower:QEDshowerByGamma = "
        + ("on" if gamma_expected else "off")
    )

    hadron_line = (
        "HadronLevel:QED = "
        + hadron_expected
    )

    card_ok = (
        gamma_line in card_text
        and hadron_line in card_text
    )

    prep = meta.get("preparation", {})
    serializer = prep.get(
        "history_serializer_v1",
        {},
    )

    validation = prep.get(
        "history_serialization_validation",
        {},
    )

    preparation_ok = all(
        [
            int(
                serializer.get(
                    "total_events",
                    -1,
                )
            )
            == EXPECTED_EVENTS,
            int(
                serializer.get(
                    "particles_added",
                    -1,
                )
            )
            == 0,
            int(
                serializer.get(
                    "particles_removed",
                    -1,
                )
            )
            == 0,
            int(
                serializer.get(
                    "resonances_added",
                    -1,
                )
            )
            == 0,
            int(
                serializer.get(
                    "resonances_removed",
                    -1,
                )
            )
            == 0,
            validation.get(
                "HISTORY_SERIALIZATION_VALIDATION"
            )
            == "PASS",
        ]
    )

    variant_ok = (
        metadata_ok
        and card_ok
        and preparation_ok
        and hepmc_path.stat().st_size > 0
    )

    overall &= variant_ok

    entry = {
        "variant": variant,
        "gamma_conversion": row["gamma_conversion"],
        "hadron_level_qed": hadron_expected,
        "metadata_pass": metadata_ok,
        "settings_pass": card_ok,
        "preparation_pass": preparation_ok,
        "accepted_events": meta.get("accepted_events"),
        "failed_events": meta.get("failed_events"),
        "seed": meta.get("seed"),
        "hepmc_bytes": hepmc_path.stat().st_size,
        "hepmc_sha256": sha256(hepmc_path),
        "me_weight_above_ps": (
            meta.get(
                "pythia_warning_counts",
                {},
            ).get(
                "me_weight_above_ps",
                0,
            )
        ),
        "negative_dipole_mass": (
            meta.get(
                "pythia_warning_counts",
                {},
            ).get(
                "negative_dipole_mass",
                0,
            )
        ),
        "hadron_level_retries": (
            meta.get(
                "pythia_error_counts",
                {},
            ).get(
                "hadron_level_retries",
                0,
            )
        ),
        "pass": variant_ok,
    }

    summary.append(entry)

    print(
        f"{variant}: "
        f"PASS={variant_ok} "
        f"accepted={entry['accepted_events']} "
        f"failed={entry['failed_events']} "
        f"seed={entry['seed']} "
        f"MEwarn={entry['me_weight_above_ps']} "
        f"negDipole={entry['negative_dipole_mass']} "
        f"hadRetry={entry['hadron_level_retries']}"
    )


summary_path = (
    output_root
    / "qed_systematics_validation_summary.json"
)

summary_path.write_text(
    json.dumps(
        {
            "overall_pass": overall,
            "variants": summary,
        },
        indent=2,
        sort_keys=True,
    )
    + "\n"
)

print()
print(
    "QED_SYSTEMATICS_VALIDATION="
    + ("PASS" if overall else "FAIL")
)
print(f"SUMMARY={summary_path}")

raise SystemExit(
    0 if overall else 1
)
