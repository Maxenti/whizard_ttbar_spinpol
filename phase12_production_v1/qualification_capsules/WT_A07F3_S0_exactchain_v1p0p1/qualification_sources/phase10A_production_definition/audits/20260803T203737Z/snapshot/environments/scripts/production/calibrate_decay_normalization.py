#!/usr/bin/env python3
"""Calibrate stable forced-decay branching weights from successful shard logs."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

from production_common import (
    campaign_root as default_campaign_root,
    default_output_root,
    ensure_eos,
    filter_configs,
    inverse_variance_mean,
    read_configs,
    repo_root_from_script,
    utc_now,
    write_csv,
)

CAL_FIELDS = [
    "campaign_id", "decay_channel", "process", "final_state", "measurements",
    "weighted_partial_width_GeV", "weighted_error_GeV", "unweighted_scatter_GeV",
    "preset_total_width_GeV", "branching_fraction", "source_manifest", "updated_utc",
]

WEIGHT_FIELDS = [
    "campaign_id", "sample_id", "decay_channel", "top_partial_width_GeV",
    "top_partial_width_error_GeV", "antitop_partial_width_GeV",
    "antitop_partial_width_error_GeV", "top_total_width_GeV",
    "antitop_total_width_GeV", "top_branching_fraction",
    "antitop_branching_fraction", "forced_decay_weight", "calibration_path",
    "updated_utc",
]


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script(__file__)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=root / "configs/production/production_500GeV_ISR_sc_v1.csv")
    p.add_argument("--campaign-root", type=Path, default=None)
    p.add_argument("--shard-manifest", type=Path, default=None)
    p.add_argument("--sample", action="append", default=[])
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--minimum-measurements", type=int, default=2)
    p.add_argument("--fallback-top-width-GeV", type=float, default=1.523)
    p.add_argument("--allow-non-eos", action="store_true")
    return p.parse_args()


def final_state(channel: str, process: str) -> str:
    mapping = {
        ("epmum", "t_decay"): "t -> b e+ nu_e",
        ("epmum", "tbar_decay"): "tbar -> bbar mu- anti-nu_mu",
        ("mupem", "t_decay"): "t -> b mu+ nu_mu",
        ("mupem", "tbar_decay"): "tbar -> bbar e- anti-nu_e",
    }
    return mapping[(channel, process)]


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ValueError("empty median")
    if n % 2:
        return ordered[n // 2]
    return 0.5 * (ordered[n // 2 - 1] + ordered[n // 2])


def main() -> int:
    args = parse_args()
    configs = filter_configs(read_configs(args.config), args.sample)
    campaign_id = configs[0].campaign_id
    campaign = args.campaign_root or default_campaign_root(default_output_root(), campaign_id, smoke=args.smoke)
    ensure_eos(campaign, allow_non_eos=args.allow_non_eos)
    shard_manifest = args.shard_manifest or campaign / "manifests/shard_manifest.csv"
    if not shard_manifest.exists():
        raise FileNotFoundError(
            f"missing shard manifest: {shard_manifest}; run make_production_manifest.py first"
        )

    with shard_manifest.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    selected_ids = {cfg.sample_id for cfg in configs}
    rows = [row for row in rows if row.get("sample_id") in selected_ids and row.get("status") == "success"]

    measurements: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    preset_widths: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        channel = row["decay_channel"]
        for process, value_key, error_key, preset_key in (
            ("t_decay", "t_decay_width_GeV", "t_decay_width_error_GeV", "preset_top_width_GeV"),
            ("tbar_decay", "tbar_decay_width_GeV", "tbar_decay_width_error_GeV", "preset_antitop_width_GeV"),
        ):
            try:
                value = float(row[value_key])
                error = float(row[error_key])
            except (KeyError, TypeError, ValueError):
                continue
            if math.isfinite(value) and math.isfinite(error) and value > 0 and error > 0:
                measurements[(channel, process)].append((value, error))
            try:
                preset = float(row[preset_key])
            except (KeyError, TypeError, ValueError):
                preset = args.fallback_top_width_GeV
            if math.isfinite(preset) and preset > 0:
                preset_widths[(channel, process)].append(preset)

    calibration_rows: list[dict[str, object]] = []
    calibration_map: dict[tuple[str, str], dict[str, float]] = {}
    for channel in sorted({cfg.decay_channel for cfg in configs}):
        for process in ("t_decay", "tbar_decay"):
            values = measurements[(channel, process)]
            if len(values) < args.minimum_measurements:
                raise ValueError(
                    f"{channel}/{process} has {len(values)} measurements; "
                    f"minimum is {args.minimum_measurements}"
                )
            width, error, scatter = inverse_variance_mean(values)
            presets = preset_widths[(channel, process)] or [args.fallback_top_width_GeV]
            total_width = median(presets)
            if max(abs(value - total_width) for value in presets) > 1e-9:
                raise ValueError(f"inconsistent preset total widths for {channel}/{process}: {presets}")
            branching = width / total_width
            calibration_map[(channel, process)] = {
                "width": width,
                "error": error,
                "total_width": total_width,
                "branching": branching,
            }
            calibration_rows.append({
                "campaign_id": campaign_id,
                "decay_channel": channel,
                "process": process,
                "final_state": final_state(channel, process),
                "measurements": len(values),
                "weighted_partial_width_GeV": f"{width:.12g}",
                "weighted_error_GeV": f"{error:.12g}",
                "unweighted_scatter_GeV": f"{scatter:.12g}",
                "preset_total_width_GeV": f"{total_width:.12g}",
                "branching_fraction": f"{branching:.12g}",
                "source_manifest": str(shard_manifest),
                "updated_utc": utc_now(),
            })

    normalization_dir = campaign / "normalization"
    calibration_path = normalization_dir / "decay_width_calibration.csv"
    write_csv(calibration_path, CAL_FIELDS, calibration_rows)

    weight_rows: list[dict[str, object]] = []
    for cfg in configs:
        top = calibration_map[(cfg.decay_channel, "t_decay")]
        antitop = calibration_map[(cfg.decay_channel, "tbar_decay")]
        weight = top["branching"] * antitop["branching"]
        weight_rows.append({
            "campaign_id": campaign_id,
            "sample_id": cfg.sample_id,
            "decay_channel": cfg.decay_channel,
            "top_partial_width_GeV": f"{top['width']:.12g}",
            "top_partial_width_error_GeV": f"{top['error']:.12g}",
            "antitop_partial_width_GeV": f"{antitop['width']:.12g}",
            "antitop_partial_width_error_GeV": f"{antitop['error']:.12g}",
            "top_total_width_GeV": f"{top['total_width']:.12g}",
            "antitop_total_width_GeV": f"{antitop['total_width']:.12g}",
            "top_branching_fraction": f"{top['branching']:.12g}",
            "antitop_branching_fraction": f"{antitop['branching']:.12g}",
            "forced_decay_weight": f"{weight:.12g}",
            "calibration_path": str(calibration_path),
            "updated_utc": utc_now(),
        })
    weights_path = normalization_dir / "forced_decay_weights.csv"
    write_csv(weights_path, WEIGHT_FIELDS, weight_rows)

    print(f"Wrote {calibration_path}")
    print(f"Wrote {weights_path}")
    for row in calibration_rows:
        print(
            f"{row['decay_channel']:6s} {row['process']:10s} "
            f"Gamma={row['weighted_partial_width_GeV']} GeV "
            f"BR={row['branching_fraction']} n={row['measurements']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
