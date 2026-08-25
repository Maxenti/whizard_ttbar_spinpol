#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STATES = {
    "unpol": "f6f365_ee_unpol_epmum/epmum",
    "LR100": "f6f365_ee_LR100_epmum/epmum",
    "RL100": "f6f365_ee_RL100_epmum/epmum",
}

COMMON_FILES = (
    "common/model.inc",
    "common/beams.inc",
    "common/isr.inc",
    "common/integration.inc",
    "common/event_output.inc",
)


def normalized_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    # Generated cards contain state-dependent absolute include roots.
    text = re.sub(
        r'/afs/cern\.ch/user/c/cglenn/FCCWork/whizard/'
        r'whizard_ttbar_spinpol/sindarin/generated/'
        r'full6f_365gev_ee_ttbar_spinpol_v1/'
        r'f6f365_ee_(?:unpol|LR100|RL100)_epmum/epmum/',
        "<CARD_ROOT>/",
        text,
    )

    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-root", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    generated_root = Path(args.generated_root).resolve()
    roots = {
        state: generated_root / relative
        for state, relative in STATES.items()
    }

    failures: list[dict[str, object]] = []
    checks: list[dict[str, object]] = []

    for state, root in roots.items():
        if not root.is_dir():
            failures.append({
                "check": "state_root_exists",
                "state": state,
                "path": str(root),
            })

    for relative in COMMON_FILES:
        values = {
            state: normalized_text(root / relative)
            for state, root in roots.items()
        }

        passed = len(set(values.values())) == 1

        checks.append({
            "check": "common_file_identical",
            "file": relative,
            "passed": passed,
            "values": values,
        })

        if not passed:
            failures.append({
                "check": "common_file_identical",
                "file": relative,
                "values": values,
            })

    expected_process = (
        "process proc_epmum = e1, E1 => "
        "b, bbar, E1, n1, e2, N2"
    )

    for state, root in roots.items():
        process = (root / "process.sin").read_text(encoding="utf-8")
        passed = expected_process in process

        checks.append({
            "check": "expected_process",
            "state": state,
            "passed": passed,
        })

        if not passed:
            failures.append({
                "check": "expected_process",
                "state": state,
            })

    process_text = {
        state: (root / "process.sin").read_text(encoding="utf-8")
        for state, root in roots.items()
    }

    polarization_include = {
        state: "common/polarization.inc" in text
        for state, text in process_text.items()
    }

    expected_include = {
        "unpol": False,
        "LR100": True,
        "RL100": True,
    }

    if polarization_include != expected_include:
        failures.append({
            "check": "polarization_include_pattern",
            "expected": expected_include,
            "observed": polarization_include,
        })

    polarization_text = {
        state: normalized_text(root / "common/polarization.inc")
        for state, root in roots.items()
    }

    expected_polarization = {
        "unpol": "polarization = 0.0, 0.0",
        "LR100": (
            "beams_pol_density = @(-1), @(+1)\n"
            "beams_pol_fraction = 100%, 100%"
        ),
        "RL100": (
            "beams_pol_density = @(+1), @(-1)\n"
            "beams_pol_fraction = 100%, 100%"
        ),
    }

    for state in STATES:
        passed = polarization_text[state] == expected_polarization[state]

        checks.append({
            "check": "polarization_definition",
            "state": state,
            "passed": passed,
            "observed": polarization_text[state],
        })

        if not passed:
            failures.append({
                "check": "polarization_definition",
                "state": state,
                "expected": expected_polarization[state],
                "observed": polarization_text[state],
            })

    payload = {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "generated_root": str(generated_root),
        "checks": checks,
        "failures": failures,
        "interpretation": {
            "unpol": "default unpolarized beams; inactive directory polarization file",
            "LR100": "electron helicity -1, positron helicity +1",
            "RL100": "electron helicity +1, positron helicity -1"
        },
    }

    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"PHASE10A_EPMUM_TRIAD_VALIDATION_STATUS={payload['status']}")
    print(f"N_CHECKS={len(checks)}")
    print(f"N_FAILURES={len(failures)}")
    print(f"WROTE={output}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
