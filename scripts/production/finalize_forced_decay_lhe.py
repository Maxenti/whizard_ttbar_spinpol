#!/usr/bin/env python3
"""Create finalized LHE files with physical forced-decay normalization.

Raw WHIZARD LHE files remain untouched under lhe_raw/.  Finalized files are
written under lhe/ with XSECUP, XERRUP and xsecinfo/totxsec multiplied by the
campaign-level forced-decay branching weight.  Unit event weights are kept.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import re
import tempfile
from pathlib import Path

from production_common import (
    campaign_root as default_campaign_root,
    count_lhe_events,
    default_output_root,
    ensure_eos,
    filter_configs,
    open_text,
    read_configs,
    read_lhe_init,
    repo_root_from_script,
    sha256,
    utc_now,
)


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script(__file__)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=root / "configs/production/production_500GeV_ISR_sc_v1.csv")
    p.add_argument("--campaign-root", type=Path, default=None)
    p.add_argument("--shard-manifest", type=Path, default=None)
    p.add_argument("--weights", type=Path, default=None)
    p.add_argument("--sample", action="append", default=[])
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--gzip", action="store_true", help="write .lhe.gz instead of .lhe")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--allow-non-eos", action="store_true")
    return p.parse_args()


def load_weights(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    return {row["sample_id"]: row for row in rows}


def load_shards(path: Path, selected: set[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    return [
        row for row in rows
        if row.get("sample_id") in selected and row.get("status") == "success" and row.get("raw_lhe_path")
    ]


def output_path(campaign: Path, sample_id: str, raw: Path, gzip_output: bool) -> Path:
    name = raw.name
    for suffix in (".lhef.gz", ".lhe.gz", ".lhef", ".lhe"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return campaign / "lhe" / sample_id / f"{name}.lhe{'.gz' if gzip_output else ''}"


def rewrite_lhe(raw: Path, destination: Path, weight: float, weight_row: dict[str, str]) -> dict[str, object]:
    before = read_lhe_init(raw)
    new_xsec = before.cross_section_pb * weight
    new_error = before.cross_section_error_pb * weight
    raw_sha = sha256(raw)

    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    if destination.name.endswith(".gz"):
        out = gzip.open(tmp, "wt", encoding="utf-8")
    else:
        out = tmp.open("w", encoding="utf-8")

    init_numeric_line = 0
    in_init = False
    inserted_header = False
    marker = "whizard_ttbar_spinpol forced_decay_normalization"
    try:
        with open_text(raw) as src, out:
            for line in src:
                stripped = line.strip()
                if stripped == "<header>":
                    out.write(line)
                    out.write(
                        "<!-- whizard_ttbar_spinpol forced_decay_normalization\n"
                        f"     raw_sha256={raw_sha}\n"
                        f"     inclusive_cross_section_pb={before.cross_section_pb:.12g}\n"
                        f"     forced_decay_weight={weight:.12g}\n"
                        f"     exclusive_cross_section_pb={new_xsec:.12g}\n"
                        f"     calibration_path={weight_row.get('calibration_path', '')}\n"
                        "-->\n"
                    )
                    inserted_header = True
                    continue
                if stripped == "<init>":
                    in_init = True
                    init_numeric_line = 0
                    out.write(line)
                    continue
                if stripped == "</init>":
                    in_init = False
                    out.write(line)
                    continue
                if in_init and stripped.startswith("<xsecinfo"):
                    updated = re.sub(
                        r'totxsec="[^"]+"',
                        f'totxsec="{new_xsec:.10E}"',
                        line,
                    )
                    out.write(updated)
                    continue
                if in_init and stripped and not stripped.startswith("<"):
                    init_numeric_line += 1
                    if init_numeric_line == 2:
                        fields = line.split()
                        if len(fields) < 4:
                            raise ValueError(f"malformed process line in {raw}: {line!r}")
                        fields[0] = f"{new_xsec:.10E}"
                        fields[1] = f"{new_error:.10E}"
                        out.write("  " + "  ".join(fields) + "\n")
                        continue
                out.write(line)
        if not inserted_header:
            raise ValueError(f"LHE file has no <header> block: {raw}")
        os.replace(tmp, destination)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

    after = read_lhe_init(destination)
    raw_events = count_lhe_events(raw)
    final_events = count_lhe_events(destination)
    if raw_events != final_events:
        destination.unlink(missing_ok=True)
        raise ValueError(f"event count changed while finalizing {raw}: {raw_events} -> {final_events}")
    tolerance = max(1e-12, abs(new_xsec) * 1e-9)
    if abs(after.cross_section_pb - new_xsec) > tolerance:
        destination.unlink(missing_ok=True)
        raise ValueError(f"final cross section mismatch in {destination}")

    return {
        "created_utc": utc_now(),
        "raw_lhe_path": str(raw),
        "raw_lhe_sha256": raw_sha,
        "final_lhe_path": str(destination),
        "final_lhe_sha256": sha256(destination),
        "events": final_events,
        "inclusive_cross_section_pb": before.cross_section_pb,
        "inclusive_cross_section_error_pb": before.cross_section_error_pb,
        "forced_decay_weight": weight,
        "exclusive_cross_section_pb": after.cross_section_pb,
        "exclusive_cross_section_error_pb": after.cross_section_error_pb,
        "top_branching_fraction": float(weight_row["top_branching_fraction"]),
        "antitop_branching_fraction": float(weight_row["antitop_branching_fraction"]),
        "calibration_path": weight_row.get("calibration_path", ""),
    }


def main() -> int:
    args = parse_args()
    configs = filter_configs(read_configs(args.config), args.sample)
    selected = {cfg.sample_id for cfg in configs}
    campaign_id = configs[0].campaign_id
    campaign = args.campaign_root or default_campaign_root(default_output_root(), campaign_id, smoke=args.smoke)
    ensure_eos(campaign, allow_non_eos=args.allow_non_eos)
    shard_manifest = args.shard_manifest or campaign / "manifests/shard_manifest.csv"
    weights_path = args.weights or campaign / "normalization/forced_decay_weights.csv"
    weights = load_weights(weights_path)
    shards = load_shards(shard_manifest, selected)
    if not shards:
        raise ValueError("no successful raw LHE shards found")

    completed = 0
    skipped = 0
    for row in shards:
        sample_id = row["sample_id"]
        if sample_id not in weights:
            raise KeyError(f"missing forced-decay weight for {sample_id}")
        raw = Path(row["raw_lhe_path"])
        destination = output_path(campaign, sample_id, raw, args.gzip)
        sidecar = destination.with_name(destination.name + ".normalization.json")
        if destination.exists() and not args.overwrite:
            if sidecar.exists():
                payload = json.loads(sidecar.read_text())
                expected_raw = sha256(raw)
                expected_weight = float(weights[sample_id]["forced_decay_weight"])
                if payload.get("raw_lhe_sha256") == expected_raw and abs(float(payload.get("forced_decay_weight", -1)) - expected_weight) < 1e-15:
                    print(f"SKIP {destination} (already finalized from current raw file and weight)")
                    skipped += 1
                    continue
            raise FileExistsError(f"final LHE exists but provenance does not match: {destination}; use --overwrite")
        payload = rewrite_lhe(raw, destination, float(weights[sample_id]["forced_decay_weight"]), weights[sample_id])
        sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"WROTE {destination} events={payload['events']} xsec_pb={payload['exclusive_cross_section_pb']:.8g}")
        completed += 1

    print(f"Finalized={completed} skipped={skipped} total={len(shards)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
