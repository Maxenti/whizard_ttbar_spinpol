#!/usr/bin/env python3

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


REPO = Path(
    "/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol"
)

CAMPAIGN_ID = "full6f_365gev_ee_ttbar_spinpol_v1"
PRODUCTION_ID = "phase11_integration_qualification_v1"

DEFINITION_DIR = (
    REPO
    / "campaigns"
    / CAMPAIGN_ID
    / "phase11A_integration_qualification"
)

PHASE10_TEMPLATE_MANIFEST = (
    REPO
    / "campaigns"
    / CAMPAIGN_ID
    / "phase10A_production_definition"
    / "full6f_365gev_epmum_triad_qualification_manifest.jsonl"
)

EOS_BASE = Path(
    "/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol"
    f"/production/{CAMPAIGN_ID}/{PRODUCTION_ID}"
)

TARGET_SAMPLE = "f6f365_ee_LR100_epmum"
TARGET_SUBPROCESS = "epmum"

EVENTS_PER_RUN = 2000
REPLICATES = 3

CANDIDATES = {
    "candidate_A_mid": '5:50000:"gw",5:100000:""',
    "candidate_B_fcc": '10:100000:"gw",10:200000:""',
    # Prepared as a contingency only. Do not submit until A/B are reviewed.
    "candidate_C_strong": '10:200000:"gw",10:500000:""',
}


def deterministic_seed(
    candidate: str,
    replicate: int,
) -> int:
    payload = (
        f"{CAMPAIGN_ID}|"
        f"{PRODUCTION_ID}|"
        f"{TARGET_SAMPLE}|"
        f"{TARGET_SUBPROCESS}|"
        f"{candidate}|"
        f"{replicate}|"
        "whizard"
    ).encode("utf-8")

    digest = hashlib.sha256(payload).digest()

    return (
        int.from_bytes(
            digest[:8],
            byteorder="big",
            signed=False,
        )
        % 2_000_000_000
    ) + 1


def load_records(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8",
        ).splitlines()
        if line.strip()
    ]


def main() -> int:
    if not PHASE10_TEMPLATE_MANIFEST.is_file():
        raise SystemExit(
            "ERROR: missing Phase-10 template manifest: "
            f"{PHASE10_TEMPLATE_MANIFEST}"
        )

    source_records = load_records(
        PHASE10_TEMPLATE_MANIFEST
    )

    matches = [
        record
        for record in source_records
        if (
            record.get("sample_id") == TARGET_SAMPLE
            and record.get("subprocess_id")
            == TARGET_SUBPROCESS
        )
    ]

    if len(matches) != 1:
        raise SystemExit(
            "ERROR: expected exactly one LR100 template "
            f"record; found {len(matches)}"
        )

    template = matches[0]

    required_template_values = {
        "campaign_id": CAMPAIGN_ID,
        "sample_id": TARGET_SAMPLE,
        "subprocess_id": TARGET_SUBPROCESS,
        "physics_mode": "direct_full_six_fermion",
        "polarization": "LR100",
    }

    for key, expected in required_template_values.items():
        observed = template.get(key)

        if observed != expected:
            raise SystemExit(
                f"ERROR: template {key}={observed!r}; "
                f"expected {expected!r}"
            )

    DEFINITION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = {}

    for candidate_name, iterations in CANDIDATES.items():
        candidate_root = (
            EOS_BASE
            / f"lr100_{candidate_name}"
        )

        output_manifest = (
            DEFINITION_DIR
            / f"full6f_365gev_epmum_lr100_{candidate_name}.jsonl"
        )

        records = []

        for replicate in range(REPLICATES):
            record = copy.deepcopy(template)

            seed = deterministic_seed(
                candidate_name,
                replicate,
            )

            record["campaign_id"] = CAMPAIGN_ID
            record["production_id"] = PRODUCTION_ID

            record["campaign_root"] = str(
                candidate_root
            )

            record["events"] = EVENTS_PER_RUN
            record["integration_iterations"] = iterations

            record["n_shards"] = REPLICATES
            record["shard_index"] = replicate
            record["shard_label"] = (
                f"shard_{replicate:04d}"
            )

            record["whizard_seed"] = seed

            # Preserve the WHIZARD scratch workspace so we can
            # identify/reuse the adapted grid after qualification.
            record["archive_workspace"] = 1

            # Keep one CPU to preserve the Phase-10 execution model.
            record["request_cpus"] = 1

            # Slightly conservative memory request for qualification.
            record["request_memory_mb"] = max(
                int(record.get("request_memory_mb", 0)),
                8000,
            )

            record["request_disk_mb"] = max(
                int(record.get("request_disk_mb", 0)),
                10000,
            )

            # Keep the established queue policy from the existing
            # production manifest unless changed deliberately later.
            record["job_flavour"] = record.get(
                "job_flavour",
                "tomorrow",
            )

            # Worker-side timeout. This does not change physics.
            record["timeout_minutes"] = 1380

            record["seed_policy"] = {
                "stage": PRODUCTION_ID,
                "candidate": candidate_name,
                "replicate": replicate,
                "stream": "whizard",
            }

            records.append(record)

        with output_manifest.open(
            "w",
            encoding="utf-8",
        ) as handle:
            for record in records:
                handle.write(
                    json.dumps(
                        record,
                        sort_keys=True,
                    )
                    + "\n"
                )

        summary[candidate_name] = {
            "manifest": str(output_manifest),
            "campaign_root": str(candidate_root),
            "iterations": iterations,
            "events_per_run": EVENTS_PER_RUN,
            "replicates": REPLICATES,
            "seeds": [
                record["whizard_seed"]
                for record in records
            ],
        }

        print()
        print(
            f"CANDIDATE={candidate_name}"
        )
        print(
            f"ITERATIONS={iterations}"
        )
        print(
            f"MANIFEST={output_manifest}"
        )
        print(
            f"CAMPAIGN_ROOT={candidate_root}"
        )

        for record in records:
            print(
                f"  {record['shard_label']} "
                f"seed={record['whizard_seed']} "
                f"events={record['events']}"
            )

    summary_path = (
        DEFINITION_DIR
        / "phase11_lr_integration_candidates.json"
    )

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("PHASE11_MANIFEST_BUILD=PASS")
    print(
        f"SUMMARY={summary_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
