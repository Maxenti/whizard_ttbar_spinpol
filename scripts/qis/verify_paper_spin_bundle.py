#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    manifest = root / "provenance" / "SHA256SUMS.txt"
    failures: list[str] = []
    checked = 0
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(None, 1)
        path = root / relative.strip()
        if not path.is_file():
            failures.append(f"missing: {relative.strip()}")
            continue
        checked += 1
        if sha256_file(path) != expected:
            failures.append(f"checksum mismatch: {relative.strip()}")
    validation = json.loads((root / "paper_spin_validation.json").read_text())
    upgrade = json.loads((root / "provenance" / "v3p1_upgrade_manifest.json").read_text())
    if validation.get("status") != "pass":
        failures.append("validation status is not pass")
    if validation.get("fatal_checks"):
        failures.append("fatal validation checks are present")
    if not upgrade.get("physics_products_byte_identical"):
        failures.append("physics byte-identity certification is false")
    if failures:
        print("Bundle verification: FAIL")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print(f"Checksum entries verified: {checked}")
    print("Validation status: pass")
    print("Fatal checks: none")
    print("Physics products byte-identical to v3: yes")
    print("Bundle verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
