#!/usr/bin/env python3
"""Strictly validate sharded PYTHIA8/HepMC3 products and provenance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

EXPECTED_POLICY = "whizard_extended_isr_to_canonical_lha_v2_explicit_w_v3"


def load_config(path: Path) -> tuple[Path, dict[str, Any]]:
    payload: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    root = Path(str(payload["campaign"]["output_root"])) / "shower"
    showering = payload.get("showering", {})
    if not isinstance(showering, dict):
        raise ValueError("showering section must be a mapping")
    return root, showering


def sha256(
    path: Path,
    attempts: int = 5,
    initial_delay_s: float = 5.0,
) -> str:
    """Return SHA256 with bounded retries for transient EOS read errors."""

    last_error: OSError | None = None

    for attempt in range(1, attempts + 1):
        digest = hashlib.sha256()

        try:
            with path.open("rb") as stream:
                for block in iter(
                    lambda: stream.read(1024 * 1024),
                    b"",
                ):
                    digest.update(block)

        except OSError as exc:
            last_error = exc

            if attempt >= attempts:
                break

            delay_s = initial_delay_s * attempt

            print(
                "WARNING: checksum read failed; "
                f"attempt={attempt}/{attempts} "
                f"path={path} "
                f"error={exc}; "
                f"retrying_in={delay_s:.0f}s"
            )

            time.sleep(delay_s)
            continue

        return digest.hexdigest()

    raise RuntimeError(
        "Unable to checksum file after "
        f"{attempts} attempts: {path}; "
        f"last_error={last_error}"
    ) from last_error


def count_hepmc_events(path: Path) -> int:
    try:
        import pyhepmc
    except ImportError as exc:
        raise RuntimeError("pyhepmc is required for strict event counting") from exc
    count = 0
    with pyhepmc.open(path) as reader:
        for _ in reader:
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--shard-manifest", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--checksums", action="store_true")
    parser.add_argument("--skip-hepmc-event-count", action="store_true")
    args = parser.parse_args()

    config_root, shower_cfg = load_config(args.config)
    root = args.root or config_root
    manifest_path = (
        args.shard_manifest
        or root / "manifests/lhe_shard_manifest.csv"
    )
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    with manifest_path.open(newline="") as stream:
        manifest_rows = list(csv.DictReader(stream))
    if not manifest_rows:
        raise ValueError(f"empty shard manifest: {manifest_path}")

    total_events_per_sample = int(
        shower_cfg.get("total_events_per_sample", 10000)
    )
    expected_qed_gamma = bool(shower_cfg.get("qed_shower_by_gamma", True))
    expected_policy = str(shower_cfg.get("lhe_preparation_policy", EXPECTED_POLICY))

    expected_by_key: dict[tuple[str, str], dict[str, str]] = {}
    rows_by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in manifest_rows:
        if row.get("status") != "ready":
            continue
        key = (row["sample_id"], row["shard_id"])
        if key in expected_by_key:
            raise ValueError(f"duplicate manifest key: {key}")
        expected_by_key[key] = row
        rows_by_sample[row["sample_id"]].append(row)
    if not expected_by_key:
        raise ValueError("no ready rows in shard manifest")

    metadata_paths = sorted((root / "metadata").glob("*/*.json"))
    output_paths = sorted((root / "hepmc3").glob("*/*.hepmc3"))
    metadata_by_key = {
        (path.parent.name, path.stem.split("__", 1)[1]): path
        for path in metadata_paths
        if "__" in path.stem
    }
    output_by_key = {
        (path.parent.name, path.stem.split("__", 1)[1]): path
        for path in output_paths
        if "__" in path.stem
    }

    checks: list[dict[str, object]] = []

    def add(
        check: str,
        sample: str,
        shard: str,
        passed: bool,
        value: object,
        detail: str,
    ) -> None:
        checks.append(
            {
                "check": check,
                "sample_id": sample,
                "shard_id": shard,
                "verdict": "PASS" if passed else "FAIL",
                "value": value,
                "detail": detail,
            }
        )

    expected_keys = set(expected_by_key)
    metadata_keys = set(metadata_by_key)
    output_keys = set(output_by_key)
    add(
        "metadata_count",
        "—",
        "—",
        metadata_keys == expected_keys and len(metadata_paths) == len(expected_keys),
        len(metadata_paths),
        f"expected exact key set of {len(expected_keys)} shards",
    )
    add(
        "output_count",
        "—",
        "—",
        output_keys == expected_keys and len(output_paths) == len(expected_keys),
        len(output_paths),
        f"expected exact key set of {len(expected_keys)} shards",
    )

    for sample, rows in sorted(rows_by_sample.items()):
        ordered = sorted(rows, key=lambda row: int(row["shard_index"]))
        indices = [int(row["shard_index"]) for row in ordered]
        starts = [int(row["source_event_start"]) for row in ordered]
        stops = [int(row["source_event_stop_exclusive"]) for row in ordered]
        counts = [int(row["requested_events"]) for row in ordered]
        contiguous = (
            indices == list(range(len(ordered)))
            and starts[0] == 0
            and all(stops[i] == starts[i + 1] for i in range(len(ordered) - 1))
            and stops[-1] == total_events_per_sample
            and sum(counts) == total_events_per_sample
            and all(stop - start == count for start, stop, count in zip(starts, stops, counts))
        )
        add(
            "source_event_partition",
            sample,
            "aggregate",
            contiguous,
            f"shards={len(ordered)} events={sum(counts)} range=[{starts[0]},{stops[-1]})",
            f"must partition [0,{total_events_per_sample}) without gaps/overlap",
        )
        shard_paths = [Path(row["shard_lhe_path"]) for row in ordered]
        files_ok = all(
            path.is_file() and path.stat().st_size > 0
            for path in shard_paths
        )
        add(
            "input_shard_files",
            sample,
            "aggregate",
            files_ok,
            len([path for path in shard_paths if path.is_file()]),
            f"expected {len(ordered)} non-empty input shards",
        )
        checksum_matches = files_ok and all(
            sha256(path) == row["shard_lhe_sha256"]
            for path, row in zip(shard_paths, ordered)
        )
        add(
            "input_shard_checksums_match",
            sample,
            "aggregate",
            checksum_matches,
            checksum_matches,
            "every persistent input shard must match its manifest SHA256",
        )
        selected_window_digests = {
            row["selected_event_window_sha256"] for row in ordered
        }
        add(
            "selected_window_digest_consistent",
            sample,
            "aggregate",
            len(selected_window_digests) == 1,
            len(selected_window_digests),
            "all shards from one sample must reference one selected-event window",
        )

    warning_totals = {"me_weight_above_ps": 0, "negative_dipole_mass": 0}
    accepted_by_sample: dict[str, int] = defaultdict(int)
    seeds: dict[int, tuple[str, str]] = {}

    for key, manifest_row in sorted(expected_by_key.items()):
        sample, shard = key
        metadata_path = metadata_by_key.get(key)
        output_path = output_by_key.get(key)
        requested = int(manifest_row["requested_events"])
        if metadata_path is None:
            add("metadata_exists", sample, shard, False, "missing", "metadata required")
            continue
        try:
            data = json.loads(metadata_path.read_text())
        except Exception as exc:
            add("metadata_parse", sample, shard, False, type(exc).__name__, str(exc))
            continue

        add("metadata_exists", sample, shard, True, str(metadata_path), "metadata required")
        add("metadata_status", sample, shard, data.get("status") == "success", data.get("status"), "must be success")
        add("return_code", sample, shard, int(data.get("return_code", 1)) == 0, data.get("return_code"), "must be zero")
        add("sample_id", sample, shard, data.get("sample_id") == sample, data.get("sample_id"), sample)
        add("shard_id", sample, shard, data.get("shard_id") == shard, data.get("shard_id"), shard)
        accepted = int(data.get("accepted_events", 0))
        requested_meta = int(data.get("requested_events", -1))
        accepted_by_sample[sample] += max(accepted, 0)
        add("accepted_events", sample, shard, accepted == requested, accepted, f"expected {requested}")
        add("requested_events", sample, shard, requested_meta == requested, requested_meta, f"expected {requested}")

        add(
            "output_exists",
            sample,
            shard,
            output_path is not None and output_path.is_file() and output_path.stat().st_size > 0,
            str(output_path) if output_path else "missing",
            "non-empty HepMC3 required",
        )
        if output_path is not None and output_path.is_file() and not args.skip_hepmc_event_count:
            try:
                actual_events = count_hepmc_events(output_path)
            except Exception as exc:
                add(
                    "hepmc_event_count",
                    sample,
                    shard,
                    False,
                    type(exc).__name__,
                    str(exc),
                )
            else:
                add(
                    "hepmc_event_count",
                    sample,
                    shard,
                    actual_events == requested,
                    actual_events,
                    f"expected {requested}",
                )

        add(
            "version_metadata",
            sample,
            shard,
            bool(data.get("pythia_version")) and bool(data.get("hepmc_version")),
            f"PYTHIA={data.get('pythia_version')} HepMC={data.get('hepmc_version')}",
            "both versions required",
        )
        add(
            "parent_lhe_provenance",
            sample,
            shard,
            data.get("source_lhe_path") == manifest_row["source_lhe_path"],
            data.get("source_lhe_path"),
            manifest_row["source_lhe_path"],
        )
        add(
            "input_shard_path",
            sample,
            shard,
            data.get("input_shard_lhe_path") == manifest_row["shard_lhe_path"],
            data.get("input_shard_lhe_path"),
            manifest_row["shard_lhe_path"],
        )
        add(
            "input_shard_sha256",
            sample,
            shard,
            data.get("input_shard_lhe_sha256") == manifest_row["shard_lhe_sha256"],
            data.get("input_shard_lhe_sha256"),
            manifest_row["shard_lhe_sha256"],
        )
        source_range = data.get("source_event_range", {})
        expected_range = {
            "start": int(manifest_row["source_event_start"]),
            "stop_exclusive": int(manifest_row["source_event_stop_exclusive"]),
            "events": requested,
        }
        add("source_event_range", sample, shard, source_range == expected_range, source_range, str(expected_range))
        add(
            "preparation_event_limit_verified",
            sample,
            shard,
            data.get("preparation_event_limit_verified") is True,
            data.get("preparation_event_limit_verified"),
            "must be true",
        )
        add("prepared_lhe_policy", sample, shard, data.get("prepared_lhe_policy") == expected_policy, data.get("prepared_lhe_policy"), expected_policy)
        add("qed_shower_by_gamma", sample, shard, bool(data.get("qed_shower_by_gamma")) == expected_qed_gamma, data.get("qed_shower_by_gamma"), f"expected {expected_qed_gamma}")

        preparation = data.get("preparation", {})
        canonical = preparation.get("canonical_v2", {}) if isinstance(preparation, dict) else {}
        explicit_w = preparation.get("explicit_w_v3", {}) if isinstance(preparation, dict) else {}
        canonical_events = int(canonical.get("total_events", -1))
        explicit_events = int(explicit_w.get("total_events", -1))
        inserted_w = int(explicit_w.get("inserted_w_resonances", -1))
        add("canonical_v2_events", sample, shard, canonical_events == requested, canonical_events, f"expected {requested}; unused parent events must not be processed")
        add("explicit_w_v3_events", sample, shard, explicit_events == requested, explicit_events, f"expected {requested}")
        add("inserted_w_resonances", sample, shard, inserted_w == 2 * requested, inserted_w, f"expected {2 * requested}")
        add("canonical_closure", sample, shard, float(canonical.get("max_rel_closure", float("inf"))) <= 1.0e-7, canonical.get("max_rel_closure"), "must be <=1e-7")
        add("explicit_w_vertex_closure", sample, shard, float(explicit_w.get("max_vertex_rel_closure", float("inf"))) <= 1.0e-7, explicit_w.get("max_vertex_rel_closure"), "must be <=1e-7")

        seed = int(data.get("seed", -1))
        duplicate_seed = seed in seeds
        add("unique_seed", sample, shard, seed > 0 and not duplicate_seed, seed, f"collision with {seeds.get(seed)}" if duplicate_seed else "must be positive and globally unique")
        if seed > 0 and not duplicate_seed:
            seeds[seed] = key

        warning_counts = data.get("pythia_warning_counts", {})
        me_warnings = int(warning_counts.get("me_weight_above_ps", -1))
        negative_warnings = int(warning_counts.get("negative_dipole_mass", -1))
        if me_warnings >= 0:
            warning_totals["me_weight_above_ps"] += me_warnings
        if negative_warnings >= 0:
            warning_totals["negative_dipole_mass"] += negative_warnings
        add("explicit_w_me_warning_count", sample, shard, me_warnings == 0, me_warnings, "must be zero")
        add("negative_dipole_warning_count", sample, shard, negative_warnings >= 0 and (expected_qed_gamma or negative_warnings == 0), negative_warnings, "counted nonfatal trials" if expected_qed_gamma else "must be zero")

        base = f"{sample}__{shard}"
        prep_dir = root / "preparation" / sample
        add("canonical_summary_staged", sample, shard, (prep_dir / f"{base}.canonical_v2.json").is_file(), str(prep_dir / f"{base}.canonical_v2.json"), "required")
        add("explicit_w_summary_staged", sample, shard, (prep_dir / f"{base}.explicit_w_v3.json").is_file(), str(prep_dir / f"{base}.explicit_w_v3.json"), "required")

    for sample in sorted(rows_by_sample):
        add("aggregate_accepted_events", sample, "aggregate", accepted_by_sample[sample] == total_events_per_sample, accepted_by_sample[sample], f"expected {total_events_per_sample}")

    failures = [row for row in checks if row["verdict"] == "FAIL"]
    validation_dir = root / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    csv_path = validation_dir / "showering_validation.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["check", "sample_id", "shard_id", "verdict", "value", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    if args.checksums:
        checksum_path = root / "manifests/hepmc3_sha256.txt"
        checksum_path.write_text("".join(f"{sha256(path)}  {path}\n" for path in output_paths))

    report = validation_dir / "showering_validation.md"
    report.write_text(
        "# Sharded shower validation\n\n"
        f"- Root: `{root}`\n"
        f"- Shard manifest: `{manifest_path}`\n"
        f"- Samples: **{len(rows_by_sample)}**\n"
        f"- Expected shower jobs: **{len(expected_keys)}**\n"
        f"- Metadata files: **{len(metadata_paths)}**\n"
        f"- HepMC3 files: **{len(output_paths)}**\n"
        f"- Events per sample: **{total_events_per_sample}**\n"
        f"- Preparation policy: `{expected_policy}`\n"
        f"- `TimeShower:QEDshowerByGamma`: `{'on' if expected_qed_gamma else 'off'}`\n"
        f"- Total ME warnings: **{warning_totals['me_weight_above_ps']}**\n"
        f"- Total negative-dipole warnings: **{warning_totals['negative_dipole_mass']}**\n"
        f"- Checks: **{len(checks)}**\n"
        f"- PASS: **{len(checks) - len(failures)}**\n"
        f"- FAIL: **{len(failures)}**\n\n"
        + (
            "All checks passed.\n"
            if not failures
            else "## Failures\n\n"
            + "\n".join(
                f"- `{row['sample_id']}/{row['shard_id']}` {row['check']}: {row['value']} ({row['detail']})"
                for row in failures
            )
            + "\n"
        )
    )
    print(f"Wrote {csv_path}")
    print(f"Wrote {report}")
    print(f"Checks={len(checks)} PASS={len(checks)-len(failures)} FAIL={len(failures)}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
