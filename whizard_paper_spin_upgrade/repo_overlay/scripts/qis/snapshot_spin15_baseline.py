#!/usr/bin/env python3
"""Create or verify a SHA-256 snapshot of the validated baseline tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    current = snapshot(root)
    if args.verify:
        reference = json.loads(output.read_text())
        added = sorted(set(current) - set(reference))
        removed = sorted(set(reference) - set(current))
        changed = sorted(
            name for name in set(current) & set(reference)
            if current[name] != reference[name]
        )
        payload = {"added": added, "removed": removed, "changed": changed}
        print(json.dumps(payload, indent=2))
        return 1 if added or removed or changed else 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
