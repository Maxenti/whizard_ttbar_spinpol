#!/usr/bin/env python3
"""Build the WHIZARD sample manifest from steering files and run products."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import re
from pathlib import Path

FIELDS = [
    "sample_id", "initial_state", "sqrt_s_GeV", "decay_channel",
    "polarization", "beam1_helicity", "beam2_helicity",
    "beam1_pol_fraction", "beam2_pol_fraction", "spin_mode",
    "isr_enabled", "beam_spectrum", "model", "seed",
    "requested_events", "generated_events", "cross_section_fb",
    "cross_section_error_fb", "relative_integration_error",
    "sindarin_path", "run_directory", "lhe_path", "log_path", "sha256",
    "status", "return_code", "notes",
]

META_RE = re.compile(r"^!\s*META\s+([A-Za-z0-9_]+)=(.*)$")
FLOAT = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    p.add_argument("--repo-root", type=Path, default=default_root)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--checksums", action="store_true")
    return p.parse_args()


def relative(path: Path | None, root: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def parse_meta(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in path.read_text(errors="replace").splitlines():
        match = META_RE.match(line.strip())
        if match:
            meta[match.group(1)] = match.group(2).strip()
    meta.setdefault("sample_id", path.stem)
    return meta


def parse_key_values(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def to_float(text: str) -> float | None:
    try:
        return float(text.replace("D", "E").replace("d", "e"))
    except (TypeError, ValueError, AttributeError):
        return None


def parse_cross_section(
    log_path: Path | None,
) -> tuple[float | None, float | None, str]:
    """Extract the final combined tt_prod cross section from WHIZARD.

    Cascade runs contain both decay-width integrations in GeV and the hard
    production integration in fb.  WHIZARD may also print process-summary
    lines containing additional numerical columns.  The robust source is the
    final combined row of the Integral[fb]/Error[fb] table belonging
    specifically to:

        Starting integration for process 'tt_prod'

    This avoids confusing decay widths, process indices, or intermediate
    integration iterations with the final production result.
    """
    if log_path is None or not log_path.exists():
        return None, None, ""

    lines = log_path.read_text(errors="replace").splitlines()

    row_re = re.compile(
        rf"^\s*(\d+)\s+(\d+)\s+({FLOAT})\s+({FLOAT})(?:\s|$)"
    )

    in_tt_prod = False
    in_fb_table = False
    candidates: list[tuple[float, float, str]] = []

    for line in lines:
        if "Starting integration for process 'tt_prod'" in line:
            in_tt_prod = True
            in_fb_table = False
            candidates = []
            continue

        if not in_tt_prod:
            continue

        lower = line.lower()

        if "integral[fb]" in lower and "error[fb]" in lower:
            in_fb_table = True
            continue

        if not in_fb_table:
            continue

        # End of the production integration section.
        if (
            "time estimate for generating" in lower
            or "unstable particle" in lower
            or "starting simulation" in lower
            or "initializing integration for process" in lower
        ):
            break

        cleaned = line.strip().strip("|").strip()
        match = row_re.match(cleaned)

        if not match:
            continue

        cross = to_float(match.group(3))
        error = to_float(match.group(4))

        if (
            cross is not None
            and error is not None
            and cross >= 0.0
            and error >= 0.0
        ):
            candidates.append((cross, error, cleaned))

    if not candidates:
        return None, None, ""

    # The final numerical row is WHIZARD's combined result for the last
    # integration stage, not an individual iteration.
    return candidates[-1]


def find_log(root: Path, sample_id: str, run_dir: Path) -> Path | None:
    for path in (run_dir / "whizard.log", root / "logs" / f"{sample_id}.log"):
        if path.exists():
            return path
    return None


def find_lhe(root: Path, initial: str, sample_id: str, run_dir: Path) -> Path | None:
    patterns = ("*.lhe", "*.lhe.gz", "*.lhef", "*.lhef.gz")

    # Central output directories can contain many samples; require an exact
    # sample-name prefix there to avoid assigning another sample's file.
    central_candidates: list[Path] = []
    for base in (root / "lhe" / initial, root / "lhe"):
        if not base.exists():
            continue
        for pattern in patterns:
            central_candidates.extend(
                path for path in base.glob(pattern) if path.name.startswith(sample_id)
            )
    if central_candidates:
        return max(central_candidates, key=lambda path: path.stat().st_mtime)

    # The run directory is isolated per sample, so any LHE file inside it is
    # safe even if a WHIZARD version chooses an unexpected output basename.
    run_candidates: list[Path] = []
    if run_dir.exists():
        for pattern in patterns:
            run_candidates.extend(run_dir.glob(pattern))
            run_candidates.extend(run_dir.glob(f"*/{pattern}"))
    return max(run_candidates, key=lambda path: path.stat().st_mtime) if run_candidates else None


def count_lhe_events(path: Path | None) -> int | None:
    if path is None or not path.exists():
        return None
    opener = gzip.open if path.name.endswith(".gz") else open
    count = 0
    with opener(path, "rt", errors="replace") as stream:
        for line in stream:
            if line.lstrip().startswith("<event"):
                count += 1
    return count


def checksum(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(run_dir: Path, log: Path | None, lhe: Path | None,
             return_code: str, requested: int | None,
             generated: int | None) -> tuple[str, str]:
    if not run_dir.exists():
        return "not_run", ""
    if return_code == "RUNNING":
        return "running_or_interrupted", "run_metadata still says RUNNING"
    if return_code:
        try:
            if int(return_code) != 0:
                return "failed", f"WHIZARD return code {return_code}"
        except ValueError:
            pass
    if log is None:
        return "incomplete", "run directory exists but no log was found"
    if lhe is None:
        return "incomplete", "log exists but no LHE/LHEF output was found"
    if requested is not None and generated is not None and requested != generated:
        return "partial", f"requested {requested}, found {generated} LHE events"
    return "success", ""


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    output = args.output or root / "metadata" / "sample_manifest.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for sin in sorted((root / "sindarin").glob("*/*.sin")):
        meta = parse_meta(sin)
        sample_id = meta["sample_id"]
        initial = meta.get("initial_state", sin.parent.name)
        run_dir = root / "runs" / initial / sample_id
        run_meta = parse_key_values(run_dir / "run_metadata.txt")
        log = find_log(root, sample_id, run_dir)
        lhe = find_lhe(root, initial, sample_id, run_dir)
        generated = count_lhe_events(lhe)
        cross, error, source = parse_cross_section(log)
        requested_text = meta.get("requested_events", "")
        requested = int(requested_text) if requested_text.isdigit() else None
        return_code = run_meta.get("return_code", "")
        status, note = classify(run_dir, log, lhe, return_code, requested, generated)
        if source:
            note = "; ".join(x for x in (note, f"cross-section source: {source}") if x)
        relerr = error / cross if cross not in (None, 0.0) and error is not None else None

        row = {field: "" for field in FIELDS}
        for field in FIELDS:
            if field in meta:
                row[field] = meta[field]
        row.update({
            "sample_id": sample_id,
            "initial_state": initial,
            "generated_events": "" if generated is None else str(generated),
            "cross_section_fb": "" if cross is None else f"{cross:.12g}",
            "cross_section_error_fb": "" if error is None else f"{error:.12g}",
            "relative_integration_error": "" if relerr is None else f"{relerr:.12g}",
            "sindarin_path": relative(sin, root),
            "run_directory": relative(run_dir, root),
            "lhe_path": relative(lhe, root),
            "log_path": relative(log, root),
            "sha256": checksum(lhe) if args.checksums else "",
            "status": status,
            "return_code": return_code,
            "notes": note,
        })
        rows.append(row)

    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"Wrote {len(rows)} rows to {output}")
    print("Status summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
