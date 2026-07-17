#!/usr/bin/env python3
"""Create a one-row-per-sample release manifest for QIS production products.

The script combines the accepted production sample manifest with checksums for
merged LHE files and, optionally, merged HepMC3 files.  It intentionally does
not infer missing physics metadata; absent files are reported explicitly in
status columns so downstream release checks can fail deterministically.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from pathlib import Path
from typing import Iterable


_CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    """Return the hexadecimal SHA-256 digest of *path*."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(_CHUNK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit(repo_root: Path) -> str:
    """Return the current Git commit, or an empty string outside a repository."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"sample manifest contains no rows: {path}")
    if "sample_id" not in rows[0]:
        raise ValueError(f"sample manifest lacks sample_id: {path}")
    return rows


def resolve_lhe_path(row: dict[str, str]) -> Path:
    """Resolve the canonical merged final LHE field used by supported manifests."""
    for field in ("merged_final_lhe_path", "final_merged_lhe_path", "merged_lhe_path"):
        value = row.get(field, "").strip()
        if value:
            return Path(value).expanduser()
    raise ValueError(
        f"{row.get('sample_id', '<unknown>')}: no merged final LHE path in manifest"
    )


def output_rows(
    source_rows: Iterable[dict[str, str]],
    *,
    shower_root: Path | None,
    commit: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in source_rows:
        sample_id = source["sample_id"].strip()
        if not sample_id:
            raise ValueError("encountered an empty sample_id")

        lhe_path = resolve_lhe_path(source)
        lhe_exists = lhe_path.is_file()

        hepmc_path: Path | None = None
        if shower_root is not None:
            hepmc_path = shower_root / "hepmc3_merged" / f"{sample_id}.hepmc3"
        hepmc_exists = bool(hepmc_path and hepmc_path.is_file())

        row = dict(source)
        row.update(
            {
                "release_lhe_path": str(lhe_path),
                "release_lhe_exists": str(lhe_exists).lower(),
                "release_lhe_size_bytes": str(lhe_path.stat().st_size) if lhe_exists else "",
                "release_lhe_sha256": sha256_file(lhe_path) if lhe_exists else "",
                "release_hepmc3_path": str(hepmc_path) if hepmc_path else "",
                "release_hepmc3_exists": str(hepmc_exists).lower(),
                "release_hepmc3_size_bytes": (
                    str(hepmc_path.stat().st_size) if hepmc_exists and hepmc_path else ""
                ),
                "release_hepmc3_sha256": (
                    sha256_file(hepmc_path) if hepmc_exists and hepmc_path else ""
                ),
                "git_commit": commit,
            }
        )
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)

    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--shower-root",
        type=Path,
        help="Optional shower campaign root containing hepmc3_merged/<sample>.hepmc3",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root used to record the Git commit",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any merged LHE or requested HepMC3 product is missing",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_rows = read_csv(args.sample_manifest.expanduser().resolve())
    shower_root = args.shower_root.expanduser().resolve() if args.shower_root else None
    rows = output_rows(
        source_rows,
        shower_root=shower_root,
        commit=git_commit(args.repo_root.expanduser().resolve()),
    )

    missing_lhe = [row["sample_id"] for row in rows if row["release_lhe_exists"] != "true"]
    missing_hepmc = [
        row["sample_id"]
        for row in rows
        if shower_root is not None and row["release_hepmc3_exists"] != "true"
    ]

    write_csv(args.output.expanduser().resolve(), rows)
    print(f"Wrote {args.output}")
    print(f"Samples: {len(rows)}")
    print(f"Missing merged LHE: {len(missing_lhe)}")
    if shower_root is not None:
        print(f"Missing merged HepMC3: {len(missing_hepmc)}")

    if args.strict and (missing_lhe or missing_hepmc):
        for sample_id in missing_lhe:
            print(f"ERROR missing LHE: {sample_id}")
        for sample_id in missing_hepmc:
            print(f"ERROR missing HepMC3: {sample_id}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
