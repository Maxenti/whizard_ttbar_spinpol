#!/usr/bin/env python3

from __future__ import annotations

import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

SHA_FILE = (
    ROOT
    / "QUALIFICATION_CAPSULE_SHA256SUMS.txt"
)


REQUIRED = [

    ROOT
    / "QUALIFICATION_REPRODUCTION_CONTRACT.md",

    ROOT
    / "REPRODUCTION_ORDER.md",

    ROOT
    / "SOURCE_FILE_MANIFEST.tsv",

    ROOT
    / "SOURCE_TREE_SUMMARY.tsv",

    ROOT
    / "qualification_sources"
    / "phase10A_production_definition",

    ROOT
    / "qualification_sources"
    / "phase11A_integration_qualification",

    ROOT
    / "qualification_sources"
    / "phase11_mpi_integration_qualification_v1",

    ROOT
    / "qualification_sources"
    / "mpi_qualification",

    ROOT
    / "qualification_sources"
    / "phase11_grid_reuse_validation_v1",

    ROOT
    / "qualification_sources"
    / "phase11_production_readiness_v1",

    ROOT
    / "repo_support"
    / "scripts"
    / "production"
    / "build_phase11_lr_integration_qualification.py",

    ROOT
    / "repo_support"
    / "scripts"
    / "production"
    / "run_full6f_production_shard.sh",

    ROOT
    / "repo_support"
    / "scripts"
    / "condor"
    / "run_full6f_production_job.sh",

    ROOT
    / "repo_support"
    / "environments"
    / "setup_whizard_3p1p8_mpi_qualified.sh",
]


def sha256(path: Path) -> str:

    h = hashlib.sha256()

    with path.open("rb") as stream:

        while True:

            block = stream.read(
                1024 * 1024
            )

            if not block:
                break

            h.update(block)

    return h.hexdigest()


for path in REQUIRED:

    if not path.exists():

        raise SystemExit(
            "REQUIRED_PATH_GATE=FAIL: "
            f"{path}"
        )


print(
    "REQUIRED_PATH_GATE=PASS"
)


symlinks = [
    path
    for path in ROOT.rglob("*")
    if path.is_symlink()
]

if symlinks:

    for path in symlinks:
        print(
            f"UNEXPECTED_SYMLINK={path}"
        )

    raise SystemExit(
        "SYMLINK_GATE=FAIL"
    )


print(
    "SYMLINK_GATE=PASS"
)


if not SHA_FILE.is_file():

    raise SystemExit(
        "SHA256_MANIFEST_GATE=FAIL: "
        "manifest missing"
    )


checked = 0


for line in SHA_FILE.read_text().splitlines():

    if not line.strip():
        continue

    expected, rel = line.split(
        None,
        1,
    )

    rel = rel.strip()

    if rel.startswith("./"):
        rel = rel[2:]

    path = ROOT / rel

    if not path.is_file():

        raise SystemExit(
            "SHA256_MANIFEST_GATE=FAIL: "
            f"missing {rel}"
        )

    actual = sha256(path)

    if actual != expected:

        raise SystemExit(
            "SHA256_MANIFEST_GATE=FAIL: "
            f"{rel}\n"
            f"expected={expected}\n"
            f"actual={actual}"
        )

    checked += 1


print(
    f"SHA256_FILES_CHECKED={checked}"
)

print(
    "SHA256_MANIFEST_GATE=PASS"
)


source_manifest = (
    ROOT
    / "SOURCE_FILE_MANIFEST.tsv"
)

rows = (
    source_manifest
    .read_text()
    .splitlines()
)

if len(rows) <= 1:

    raise SystemExit(
        "SOURCE_MANIFEST_GATE=FAIL"
    )


print(
    f"SOURCE_MANIFEST_ROWS={len(rows)-1}"
)

print(
    "SOURCE_MANIFEST_GATE=PASS"
)

print(
    "QUALIFICATION_CAPSULE_VERIFY=PASS"
)
