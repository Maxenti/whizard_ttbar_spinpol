#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


EXPECTED = {
    "GF": 1.16639e-5,
    "mZ": 91.1882,
    "mW": 80.419,
    "mH": 125.0,
    "alphas": 0.1178,
    "me": 0.000510997,
    "mmu": 0.105658389,
    "mtau": 1.77705,
    "ms": 0.095,
    "mc": 1.2,
    "mb": 4.2,
    "mtop": 173.1,
    "wtop": 1.523,
    "wZ": 2.443,
    "wW": 2.049,
    "wH": 0.004143,
}

EXPECTED_HASHES = {
    "SM.mdl": (
        "f6cba9141f9405bbe4dcf604fe4b28b30dd697f1243ea558dbda0d25f435aede"
    ),
    "SM_hadrons.mdl": (
        "f9fdbb9a2b61785a1414bab5cfc63650d0eb7ebbf15ca32dcd6018a322d23efd"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def parse_parameters(path: Path) -> dict[str, float]:
    pattern = re.compile(
        r"^\s*parameter\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    )

    values: dict[str, float] = {}

    for line in path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines():
        match = pattern.match(line)

        if match:
            values[match.group(1)] = float(match.group(2))

    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sm-model", required=True)
    parser.add_argument("--sm-hadrons-model", required=True)
    parser.add_argument("--baseline-json", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    sm = Path(args.sm_model).resolve()
    hadrons = Path(args.sm_hadrons_model).resolve()
    baseline_path = Path(args.baseline_json).resolve()

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    failures: list[dict[str, object]] = []
    checks: list[dict[str, object]] = []

    actual_hashes = {
        "SM.mdl": sha256(sm),
        "SM_hadrons.mdl": sha256(hadrons),
    }

    for name, expected_hash in EXPECTED_HASHES.items():
        passed = actual_hashes[name] == expected_hash

        checks.append({
            "check": "model_sha256",
            "file": name,
            "expected": expected_hash,
            "observed": actual_hashes[name],
            "passed": passed,
        })

        if not passed:
            failures.append(checks[-1])

    sm_parameters = parse_parameters(sm)
    hadron_parameters = parse_parameters(hadrons)

    for parameter, expected in EXPECTED.items():
        for source, values in (
            ("SM.mdl", sm_parameters),
            ("SM_hadrons.mdl", hadron_parameters),
        ):
            observed = values.get(parameter)
            passed = (
                observed is not None
                and abs(observed - expected) <= 1.0e-12
            )

            check = {
                "check": "parameter_value",
                "source": source,
                "parameter": parameter,
                "expected": expected,
                "observed": observed,
                "passed": passed,
            }

            checks.append(check)

            if not passed:
                failures.append(check)

    model_text = sm.read_text(encoding="utf-8", errors="replace")

    required_fragments = [
        'model "SM"',
        "Standard Model with trivial CKM matrix",
        "derived v     = 1 / sqrt (sqrt (2.) * GF)",
        "derived cw    = mW / mZ",
        "derived sw    = sqrt (1-cw**2)",
        "derived ee    = 2 * sw * mW / v",
        "mass mtop  width wtop",
        "mass mZ  width wZ",
        "mass mW  width wW",
    ]

    for fragment in required_fragments:
        passed = fragment in model_text

        check = {
            "check": "required_model_fragment",
            "fragment": fragment,
            "passed": passed,
        }

        checks.append(check)

        if not passed:
            failures.append(check)

    baseline_hashes = {
        name: record["sha256"]
        for name, record in baseline["model_files"].items()
    }

    for name, observed in baseline_hashes.items():
        expected = EXPECTED_HASHES[name]
        passed = observed == expected

        check = {
            "check": "baseline_json_hash",
            "file": name,
            "expected": expected,
            "observed": observed,
            "passed": passed,
        }

        checks.append(check)

        if not passed:
            failures.append(check)

    output = {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "sm_model": str(sm),
        "sm_hadrons_model": str(hadrons),
        "baseline_json": str(baseline_path),
        "checks": checks,
        "failures": failures,
    }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        f"PHASE10A_WHIZARD_SM_BASELINE_VALIDATION_STATUS="
        f"{output['status']}"
    )
    print(f"N_CHECKS={len(checks)}")
    print(f"N_FAILURES={len(failures)}")
    print(f"WROTE={output_path}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
