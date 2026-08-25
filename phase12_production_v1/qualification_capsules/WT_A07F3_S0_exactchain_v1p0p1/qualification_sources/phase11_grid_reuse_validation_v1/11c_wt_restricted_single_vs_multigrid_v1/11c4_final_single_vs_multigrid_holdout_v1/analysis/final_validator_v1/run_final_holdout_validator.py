#!/usr/bin/env python3

"""
Phase-11C final WT A07/F3 holdout validator wrapper.

Purpose
-------
Reuse the previously qualified C5 validator byte-for-byte while changing
only its structural expected event count per legacy interface component:

    old C5:
        10,000 events/component

    final holdout:
        32,000 events/component

The physics/statistical implementation is not modified.

Legacy interface mapping
------------------------
S0_C -> SINGLE_A
S0_D -> SINGLE_B
S1_B -> MULTI_A
S2_B -> MULTI_B

Thus:

    SINGLE = SINGLE_A + SINGLE_B = 64,000
    MULTI  = MULTI_A  + MULTI_B  = 64,000
"""

import hashlib
import importlib.util
import os
from pathlib import Path
import sys


EXPECTED_VALIDATOR_SHA256 = (
    "6ca54d4cce6b33044deb005b6cf7ebeb"
    "1437c33105bf7d48e586ff3b20b3ce9a"
)

EXPECTED_EVENTS_PER_COMPONENT = 32_000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def main() -> int:

    validator_env = os.environ.get(
        "QUALIFIED_C5_VALIDATOR"
    )

    if not validator_env:
        raise SystemExit(
            "ERROR: QUALIFIED_C5_VALIDATOR is not set"
        )

    validator_path = Path(
        validator_env
    ).resolve()

    if not validator_path.is_file():
        raise SystemExit(
            f"ERROR: validator missing: {validator_path}"
        )

    actual_sha = sha256_file(
        validator_path
    )

    if actual_sha != EXPECTED_VALIDATOR_SHA256:
        raise SystemExit(
            "ERROR: qualified validator SHA256 mismatch\n"
            f"expected={EXPECTED_VALIDATOR_SHA256}\n"
            f"actual={actual_sha}"
        )

    spec = importlib.util.spec_from_file_location(
        "qualified_phase11c5_validator",
        validator_path,
    )

    if spec is None or spec.loader is None:
        raise SystemExit(
            "ERROR: unable to load qualified validator"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[
        spec.name
    ] = module

    spec.loader.exec_module(
        module
    )

    old_expected = getattr(
        module,
        "EXPECTED_EVENTS_PER_COMPONENT",
        None,
    )

    if old_expected != 10_000:
        raise SystemExit(
            "ERROR: unexpected original structural "
            "component-size constant: "
            f"{old_expected!r}"
        )

    # The ONLY runtime semantic override.
    module.EXPECTED_EVENTS_PER_COMPONENT = (
        EXPECTED_EVENTS_PER_COMPONENT
    )

    print(
        "FINAL_HOLDOUT_VALIDATOR_WRAPPER=ACTIVE"
    )
    print(
        f"QUALIFIED_VALIDATOR={validator_path}"
    )
    print(
        f"QUALIFIED_VALIDATOR_SHA256={actual_sha}"
    )
    print(
        f"ORIGINAL_EXPECTED_EVENTS_PER_COMPONENT="
        f"{old_expected}"
    )
    print(
        f"FINAL_EXPECTED_EVENTS_PER_COMPONENT="
        f"{module.EXPECTED_EVENTS_PER_COMPONENT}"
    )

    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
