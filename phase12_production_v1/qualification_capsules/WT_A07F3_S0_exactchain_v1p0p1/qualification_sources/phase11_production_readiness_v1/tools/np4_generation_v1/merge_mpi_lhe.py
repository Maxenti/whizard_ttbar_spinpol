#!/usr/bin/env python3

"""
Merge WHIZARD MPI rank-local LHE files into one canonical LHE file.

WHIZARD 3.1.8 MPI event generation writes one complete LHE document per
MPI rank:

    <basename>_0.lhe
    <basename>_1.lhe
    ...
    <basename>_<N-1>.lhe

The requested n_events is global across the MPI world, not per rank.

This helper:

  * requires exactly the expected rank files,
  * verifies that all files are complete LHE documents,
  * verifies equal headers / <init> blocks byte-for-byte,
  * verifies xsecinfo neve against the requested global event count,
  * verifies the summed physical <event> count,
  * merges events in deterministic ascending-rank order,
  * writes exactly one common LHE header and closing tag,
  * writes the output atomically,
  * writes a JSON rank-level provenance manifest atomically.

It is intentionally streaming: event payloads are never loaded into memory
as one giant object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ROOT_OPEN_PREFIX = b"<LesHouchesEvents"
ROOT_CLOSE = b"</LesHouchesEvents>"
EVENT_CLOSE = b"</event>"

EVENT_OPEN_RE = re.compile(
    rb"^<event(?:\s[^>]*)?>$"
)

XSEC_NEVE_RE = re.compile(
    rb"""<xsecinfo\b[^>]*\bneve\s*=\s*["'](\d+)["']""",
    re.IGNORECASE,
)


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"ERROR: {message}")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def scan_rank_file(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()

    header = bytearray()

    size_bytes = 0
    event_open_count = 0
    event_close_count = 0
    root_open_count = 0
    root_close_count = 0

    header_complete = False
    root_closed = False
    trailing_nonwhitespace = False

    with path.open("rb") as handle:
        for raw_line in handle:
            digest.update(raw_line)
            size_bytes += len(raw_line)

            stripped = raw_line.strip()

            if root_closed:
                if stripped:
                    trailing_nonwhitespace = True
                continue

            if stripped.startswith(ROOT_OPEN_PREFIX):
                root_open_count += 1

            is_event_open = bool(
                EVENT_OPEN_RE.fullmatch(stripped)
            )

            if not header_complete:
                if is_event_open or stripped == ROOT_CLOSE:
                    header_complete = True
                else:
                    header.extend(raw_line)

            if is_event_open:
                event_open_count += 1

            if stripped == EVENT_CLOSE:
                event_close_count += 1

            if stripped == ROOT_CLOSE:
                root_close_count += 1
                root_closed = True

    if root_open_count != 1:
        fail(
            f"{path}: expected one <LesHouchesEvents> root opening, "
            f"found {root_open_count}"
        )

    if root_close_count != 1:
        fail(
            f"{path}: expected one </LesHouchesEvents> closing tag, "
            f"found {root_close_count}"
        )

    if trailing_nonwhitespace:
        fail(
            f"{path}: non-whitespace content exists after "
            "</LesHouchesEvents>"
        )

    if event_open_count != event_close_count:
        fail(
            f"{path}: event-tag mismatch: "
            f"open={event_open_count}, close={event_close_count}"
        )

    header_bytes = bytes(header)

    neve_matches = XSEC_NEVE_RE.findall(header_bytes)

    if len(neve_matches) != 1:
        fail(
            f"{path}: expected exactly one xsecinfo neve attribute, "
            f"found {len(neve_matches)}"
        )

    xsecinfo_neve = int(neve_matches[0])

    return {
        "path": path,
        "filename": path.name,
        "size_bytes": size_bytes,
        "sha256": digest.hexdigest(),
        "header": header_bytes,
        "header_sha256": hashlib.sha256(
            header_bytes
        ).hexdigest(),
        "events": event_open_count,
        "xsecinfo_neve": xsecinfo_neve,
    }


def discover_rank_files(
    input_dir: Path,
    basename: str,
    expected_ranks: int,
) -> list[Path]:
    rank_pattern = re.compile(
        rf"^{re.escape(basename)}_(\d+)\.lhe$"
    )

    discovered: dict[int, Path] = {}

    for path in input_dir.glob(f"{basename}_*.lhe"):
        match = rank_pattern.fullmatch(path.name)

        if match is None:
            continue

        rank = int(match.group(1))

        if rank in discovered:
            fail(
                f"duplicate rank {rank} for basename {basename}"
            )

        discovered[rank] = path

    expected = set(range(expected_ranks))
    observed = set(discovered)

    missing = sorted(expected - observed)
    extra = sorted(observed - expected)

    if missing:
        fail(
            "missing MPI LHE ranks: "
            + ",".join(str(rank) for rank in missing)
        )

    if extra:
        fail(
            "unexpected MPI LHE ranks: "
            + ",".join(str(rank) for rank in extra)
        )

    return [
        discovered[rank]
        for rank in range(expected_ranks)
    ]


def write_json_atomic(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_name(
        f"{path.name}.tmp.{os.getpid()}"
    )

    try:
        temp.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        os.replace(temp, path)

    finally:
        if temp.exists():
            temp.unlink()


def merge_rank_files(
    infos: list[dict[str, Any]],
    output: Path,
) -> tuple[str, int]:
    reference_header = infos[0]["header"]

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = output.with_name(
        f"{output.name}.tmp.{os.getpid()}"
    )

    merged_digest = hashlib.sha256()
    merged_size = 0

    def emit(
        handle,
        payload: bytes,
    ) -> None:
        nonlocal merged_size

        handle.write(payload)
        merged_digest.update(payload)
        merged_size += len(payload)

    try:
        with temp.open("wb") as target:
            emit(
                target,
                reference_header,
            )

            for info in infos:
                source_path: Path = info["path"]

                with source_path.open("rb") as source:
                    observed_header = source.read(
                        len(reference_header)
                    )

                    if observed_header != reference_header:
                        fail(
                            f"{source_path}: header changed between "
                            "validation and merge"
                        )

                    found_root_close = False

                    for raw_line in source:
                        stripped = raw_line.strip()

                        if stripped == ROOT_CLOSE:
                            found_root_close = True
                            break

                        emit(
                            target,
                            raw_line,
                        )

                    if not found_root_close:
                        fail(
                            f"{source_path}: root closing tag vanished "
                            "during merge"
                        )

            closing = b"</LesHouchesEvents>\n"

            emit(
                target,
                closing,
            )

            target.flush()
            os.fsync(target.fileno())

        os.replace(
            temp,
            output,
        )

    finally:
        if temp.exists():
            temp.unlink()

    return (
        merged_digest.hexdigest(),
        merged_size,
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-dir",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--basename",
        required=True,
    )

    parser.add_argument(
        "--expected-ranks",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--expected-events",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    if args.expected_ranks <= 1:
        fail(
            "--expected-ranks must be >1 for MPI merge"
        )

    if args.expected_events <= 0:
        fail(
            "--expected-events must be positive"
        )

    if not args.input_dir.is_dir():
        fail(
            f"input directory does not exist: "
            f"{args.input_dir}"
        )

    rank_paths = discover_rank_files(
        input_dir=args.input_dir,
        basename=args.basename,
        expected_ranks=args.expected_ranks,
    )

    infos = [
        scan_rank_file(path)
        for path in rank_paths
    ]

    reference_header = infos[0]["header"]
    reference_header_sha256 = infos[0][
        "header_sha256"
    ]

    for rank, info in enumerate(infos):
        if info["header"] != reference_header:
            fail(
                f"rank {rank}: LHE header differs from rank 0"
            )

        if (
            info["xsecinfo_neve"]
            != args.expected_events
        ):
            fail(
                f"rank {rank}: xsecinfo neve="
                f"{info['xsecinfo_neve']} but expected "
                f"{args.expected_events}"
            )

    total_events = sum(
        int(info["events"])
        for info in infos
    )

    if total_events != args.expected_events:
        fail(
            f"MPI rank files contain {total_events} events "
            f"but requested {args.expected_events}"
        )

    merged_sha256, merged_size = merge_rank_files(
        infos=infos,
        output=args.output,
    )

    rank_records = []

    for rank, info in enumerate(infos):
        rank_records.append(
            {
                "rank": rank,
                "filename": info["filename"],
                "events": int(info["events"]),
                "size_bytes": int(
                    info["size_bytes"]
                ),
                "sha256": info["sha256"],
            }
        )

    manifest = {
        "schema_version": 1,
        "layout": "whizard_mpi_rank_merge",
        "mpi_ranks": args.expected_ranks,
        "requested_events": args.expected_events,
        "observed_rank_events": total_events,
        "rank_order": "ascending_numeric_rank",
        "common_header_sha256": (
            reference_header_sha256
        ),
        "xsecinfo_neve": args.expected_events,
        "rank_files": rank_records,
        "merged": {
            "filename": args.output.name,
            "events": total_events,
            "size_bytes": merged_size,
            "sha256": merged_sha256,
        },
    }

    write_json_atomic(
        args.manifest,
        manifest,
    )

    print("MPI_LHE_MERGE=PASS")
    print(
        f"MPI_RANK_FILES={len(rank_paths)}"
    )
    print(
        f"MPI_TOTAL_EVENTS={total_events}"
    )
    print(
        f"MPI_COMMON_HEADER_SHA256="
        f"{reference_header_sha256}"
    )
    print(
        f"MERGED_LHE={args.output}"
    )
    print(
        f"MERGED_LHE_SHA256={merged_sha256}"
    )
    print(
        f"LHE_RANK_MANIFEST={args.manifest}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
