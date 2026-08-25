#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SEED_RE = re.compile(r"(?m)^\s*seed\s*=\s*(\d+)\s*$")
RNG_RE = re.compile(
    r"RNG: Setting seed for random-number generator to\s+(\d+)"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def count_lhe_events(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(
        re.findall(
            r"(?m)^\s*<event(?:\s|>)",
            text,
        )
    )


def load_run(root: Path) -> dict[str, object]:
    metadata_paths = sorted(root.glob("runs/**/run_metadata.json"))
    lhe_paths = sorted(root.glob("lhe_raw/**/*.lhe"))

    if len(metadata_paths) != 1:
        raise RuntimeError(
            f"{root}: expected one metadata file, "
            f"found {len(metadata_paths)}"
        )

    if len(lhe_paths) != 1:
        raise RuntimeError(
            f"{root}: expected one LHE file, found {len(lhe_paths)}"
        )

    metadata_path = metadata_paths[0]
    lhe_path = lhe_paths[0]
    run_dir = metadata_path.parent

    integration_path = (
        run_dir / "effective_common" / "integration.inc"
    )
    process_path = run_dir / "effective_process.sin"
    console_path = run_dir / "console.log"
    success_path = run_dir / "SUCCESS"

    for path in (
        integration_path,
        process_path,
        console_path,
        success_path,
    ):
        if not path.exists():
            raise RuntimeError(f"{root}: missing required artifact {path}")

    metadata = json.loads(
        metadata_path.read_text(encoding="utf-8")
    )
    integration_text = integration_path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    process_text = process_path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    console_text = console_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    seed_matches = SEED_RE.findall(integration_text)
    rng_sequence = [
        int(value)
        for value in RNG_RE.findall(console_text)
    ]

    return {
        "root": str(root),
        "metadata_path": str(metadata_path),
        "lhe_path": str(lhe_path),
        "run_dir": str(run_dir),
        "metadata": metadata,
        "lhe_sha256": sha256(lhe_path),
        "lhe_event_count": count_lhe_events(lhe_path),
        "effective_seed_assignments": [
            int(value)
            for value in seed_matches
        ],
        "rng_sequence": rng_sequence,
        "success_marker": success_path.is_file(),
        "localized_process_card": (
            "/sindarin/generated/" not in process_text
            and 'include("common/integration.inc")' in process_text
            and 'include("common/event_output.inc")' in process_text
        ),
        "whizard_finished": "WHIZARD run finished." in console_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate same-seed and different-seed replay behavior for "
            "the Phase 10A direct-full6f production worker."
        )
    )
    parser.add_argument("--run-a", type=Path, required=True)
    parser.add_argument("--run-b", type=Path, required=True)
    parser.add_argument("--run-c", type=Path, required=True)
    parser.add_argument("--expected-seed-ab", type=int, required=True)
    parser.add_argument("--expected-seed-c", type=int, required=True)
    parser.add_argument("--expected-events", type=int, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    runs = {
        "A": load_run(args.run_a.resolve()),
        "B": load_run(args.run_b.resolve()),
        "C": load_run(args.run_c.resolve()),
    }

    checks: dict[str, bool] = {}

    for label, run in runs.items():
        metadata = run["metadata"]
        expected_seed = (
            args.expected_seed_ab
            if label in {"A", "B"}
            else args.expected_seed_c
        )

        checks[f"{label}_metadata_success"] = (
            metadata.get("status") == "success"
        )
        checks[f"{label}_production_mode_full6f"] = (
            metadata.get("production_mode")
            == "direct_full_six_fermion"
        )
        checks[f"{label}_whizard_version_3_1_8"] = (
            "3.1.8"
            in metadata.get("runtime", {}).get(
                "whizard_version",
                "",
            )
        )
        checks[f"{label}_requested_seed_recorded"] = (
            metadata.get("random_streams", {}).get(
                "whizard_seed"
            )
            == expected_seed
        )
        checks[f"{label}_effective_seed_exact"] = (
            run["effective_seed_assignments"]
            == [expected_seed]
        )
        checks[f"{label}_event_count"] = (
            run["lhe_event_count"] == args.expected_events
            and metadata.get("generated_events")
            == args.expected_events
        )
        checks[f"{label}_localized_process_card"] = bool(
            run["localized_process_card"]
        )
        checks[f"{label}_success_marker"] = bool(
            run["success_marker"]
        )
        checks[f"{label}_whizard_finished"] = bool(
            run["whizard_finished"]
        )

    checks["same_seed_lhe_byte_identical"] = (
        runs["A"]["lhe_sha256"] == runs["B"]["lhe_sha256"]
    )
    checks["different_seed_changes_lhe"] = (
        runs["A"]["lhe_sha256"] != runs["C"]["lhe_sha256"]
    )
    checks["same_seed_rng_sequences_identical"] = (
        runs["A"]["rng_sequence"] == runs["B"]["rng_sequence"]
    )
    checks["different_seed_rng_sequences_differ"] = (
        runs["A"]["rng_sequence"] != runs["C"]["rng_sequence"]
    )

    status = "PASS" if all(checks.values()) else "FAIL"

    payload = {
        "schema_version": 1,
        "status": status,
        "test": "Phase 10A full6f worker deterministic replay",
        "expected": {
            "seed_ab": args.expected_seed_ab,
            "seed_c": args.expected_seed_c,
            "events": args.expected_events,
        },
        "runs": runs,
        "checks": checks,
        "failed_checks": [
            name
            for name, passed in checks.items()
            if not passed
        ],
    }

    output = args.output_json.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    for name, passed in checks.items():
        print(f"{name}={'PASS' if passed else 'FAIL'}")

    print(f"PHASE10A_FULL6F_WORKER_REPLAY_STATUS={status}")
    print(f"A_SHA256={runs['A']['lhe_sha256']}")
    print(f"B_SHA256={runs['B']['lhe_sha256']}")
    print(f"C_SHA256={runs['C']['lhe_sha256']}")
    print(f"A_RNG_SEQUENCE={runs['A']['rng_sequence']}")
    print(f"B_RNG_SEQUENCE={runs['B']['rng_sequence']}")
    print(f"C_RNG_SEQUENCE={runs['C']['rng_sequence']}")
    print(f"WROTE={output}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
