#!/usr/bin/env python3
"""Build canonical shard- and sample-level manifests for a production campaign."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from production_common import (
    campaign_root as default_campaign_root,
    count_lhe_events,
    default_output_root,
    ensure_eos,
    filter_configs,
    inverse_variance_mean,
    is_lhe,
    load_json,
    parse_excess_weight,
    parse_process_integration,
    read_configs,
    read_lhe_init,
    repo_root_from_script,
    sha256,
    utc_now,
    write_csv,
)

SHARD_FIELDS = [
    "campaign_id", "sample_id", "initial_state", "decay_channel", "polarization",
    "shard_index", "shard_label", "seed", "requested_events", "generated_events",
    "status", "whizard_return_code", "run_directory", "raw_lhe_path", "final_lhe_path",
    "log_path", "raw_lhe_sha256", "final_lhe_sha256", "inclusive_cross_section_fb",
    "inclusive_cross_section_error_fb", "relative_integration_error", "t_decay_width_GeV",
    "t_decay_width_error_GeV", "tbar_decay_width_GeV", "tbar_decay_width_error_GeV",
    "preset_top_width_GeV", "preset_antitop_width_GeV", "excess_weight_events",
    "excess_weight_fraction_percent", "maximum_excess_weight", "input_has_isr",
    "input_has_exact_spin", "input_has_polarized_events", "metadata_path", "notes",
]

SAMPLE_FIELDS = [
    "campaign_id", "sample_id", "initial_state", "decay_channel", "polarization",
    "sqrt_s_GeV", "expected_shards", "successful_shards", "failed_or_missing_shards",
    "events_per_shard", "expected_events", "generated_events", "raw_lhe_files",
    "final_lhe_files", "inclusive_cross_section_fb", "inclusive_cross_section_error_fb",
    "exclusive_cross_section_fb", "forced_decay_weight", "merged_raw_lhe_path",
    "merged_final_lhe_path", "status", "updated_utc",
]


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script(__file__)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=root / "configs/production/production_500GeV_ISR_sc_v1.csv")
    parser.add_argument("--campaign-root", type=Path, default=None)
    parser.add_argument("--sample", action="append", default=[])
    parser.add_argument("--smoke", action="store_true", help="expect only shard 0 per sample")
    parser.add_argument("--allow-non-eos", action="store_true")
    return parser.parse_args()


def find_lhe(base: Path, output_sample: str) -> Path | None:
    if not base.exists():
        return None
    candidates = [p for p in base.iterdir() if p.is_file() and p.name.startswith(output_sample) and is_lhe(p)]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def find_log(campaign: Path, sample_id: str, shard_label: str, run_dir: Path) -> Path | None:
    candidates = [
        run_dir / "whizard.log",
        campaign / "logs" / sample_id / f"{sample_id}__{shard_label}.whizard.log",
        run_dir / "console.log",
        campaign / "logs" / sample_id / f"{sample_id}__{shard_label}.console.log",
    ]
    return next((p for p in candidates if p.exists()), None)


def load_forced_weights(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="") as stream:
        return {row["sample_id"]: row for row in csv.DictReader(stream)}


def main() -> int:
    args = parse_args()
    configs = filter_configs(read_configs(args.config), args.sample)
    campaign_id = configs[0].campaign_id
    campaign = args.campaign_root or default_campaign_root(default_output_root(), campaign_id, smoke=args.smoke)
    ensure_eos(campaign, allow_non_eos=args.allow_non_eos)
    manifests = campaign / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)

    forced = load_forced_weights(campaign / "normalization/forced_decay_weights.csv")
    shard_rows: list[dict[str, object]] = []

    for cfg in configs:
        indices = [0] if args.smoke else list(range(cfg.n_shards))
        for idx in indices:
            label = cfg.shard_label(idx)
            output_sample = cfg.output_sample_name(idx)
            run_dir = campaign / "runs" / cfg.sample_id / label
            metadata_path = run_dir / "run_metadata.json"
            metadata = load_json(metadata_path)
            raw_lhe = find_lhe(campaign / "lhe_raw" / cfg.sample_id, output_sample)
            final_lhe = find_lhe(campaign / "lhe" / cfg.sample_id, output_sample)
            log = find_log(campaign, cfg.sample_id, label, run_dir)

            requested = int(metadata.get("requested_events", cfg.events_per_shard))
            generated = int(metadata.get("generated_events", count_lhe_events(raw_lhe) if raw_lhe else 0))
            status = str(metadata.get("status", "missing" if not run_dir.exists() else "incomplete"))
            rc = metadata.get("whizard_return_code", "")
            notes: list[str] = []

            prod = parse_process_integration(log, "tt_prod", "fb") if log else None
            t_width = parse_process_integration(log, "t_decay", "gev") if log else None
            tb_width = parse_process_integration(log, "tbar_decay", "gev") if log else None
            preset_t = ""
            preset_tb = ""
            if log:
                from production_common import parse_preset_top_widths
                widths = parse_preset_top_widths(log)
                preset_t = widths.get("t", "")
                preset_tb = widths.get("tbar", "")
                excess_count, excess_frac, excess_max = parse_excess_weight(log)
            else:
                excess_count, excess_frac, excess_max = 0, 0.0, 0.0

            input_text = (run_dir / "input.sin").read_text(errors="replace") if (run_dir / "input.sin").exists() else ""
            input_has_isr = "=> isr" in input_text and "?isr_handler = true" in input_text
            input_has_spin = "?isotropic_decay = false" in input_text and "?diagonal_decay = false" in input_text
            input_has_pol = input_text.count("?polarized_events = true") >= 2

            if raw_lhe is None and status == "success":
                status = "missing_raw_lhe"
            if raw_lhe and generated != requested:
                status = "event_count_mismatch"
            if prod is None and log:
                notes.append("tt_prod integration result not parsed")

            relerr = prod.error / prod.value if prod and prod.value else ""
            shard_rows.append({
                "campaign_id": campaign_id,
                "sample_id": cfg.sample_id,
                "initial_state": cfg.initial_state,
                "decay_channel": cfg.decay_channel,
                "polarization": cfg.polarization,
                "shard_index": idx,
                "shard_label": label,
                "seed": metadata.get("seed", cfg.shard_seed(idx)),
                "requested_events": requested,
                "generated_events": generated,
                "status": status,
                "whizard_return_code": rc,
                "run_directory": str(run_dir),
                "raw_lhe_path": str(raw_lhe or ""),
                "final_lhe_path": str(final_lhe or ""),
                "log_path": str(log or ""),
                "raw_lhe_sha256": sha256(raw_lhe) if raw_lhe else "",
                "final_lhe_sha256": sha256(final_lhe) if final_lhe else "",
                "inclusive_cross_section_fb": f"{prod.value:.12g}" if prod else "",
                "inclusive_cross_section_error_fb": f"{prod.error:.12g}" if prod else "",
                "relative_integration_error": f"{relerr:.12g}" if relerr != "" else "",
                "t_decay_width_GeV": f"{t_width.value:.12g}" if t_width else "",
                "t_decay_width_error_GeV": f"{t_width.error:.12g}" if t_width else "",
                "tbar_decay_width_GeV": f"{tb_width.value:.12g}" if tb_width else "",
                "tbar_decay_width_error_GeV": f"{tb_width.error:.12g}" if tb_width else "",
                "preset_top_width_GeV": preset_t,
                "preset_antitop_width_GeV": preset_tb,
                "excess_weight_events": excess_count,
                "excess_weight_fraction_percent": excess_frac,
                "maximum_excess_weight": excess_max,
                "input_has_isr": input_has_isr,
                "input_has_exact_spin": input_has_spin,
                "input_has_polarized_events": input_has_pol,
                "metadata_path": str(metadata_path if metadata_path.exists() else ""),
                "notes": "; ".join(notes),
            })

    shard_manifest = manifests / "shard_manifest.csv"
    write_csv(shard_manifest, SHARD_FIELDS, shard_rows)

    sample_rows: list[dict[str, object]] = []
    for cfg in configs:
        rows = [row for row in shard_rows if row["sample_id"] == cfg.sample_id]
        success = [row for row in rows if row["status"] == "success"]
        values = []
        for row in success:
            try:
                values.append((float(row["inclusive_cross_section_fb"]), float(row["inclusive_cross_section_error_fb"])))
            except (TypeError, ValueError):
                pass
        if values:
            mean, error, _ = inverse_variance_mean(values)
        else:
            mean, error = math.nan, math.nan
        expected_shards = 1 if args.smoke else cfg.n_shards
        expected_events = sum(int(row["requested_events"]) for row in rows)
        generated_events = sum(int(row["generated_events"]) for row in rows)
        force_row = forced.get(cfg.sample_id, {})
        weight = force_row.get("forced_decay_weight", "")
        exclusive = mean * float(weight) if weight and math.isfinite(mean) else ""
        merged_raw = campaign / "lhe_merged/raw" / f"{cfg.sample_id}.lhe"
        merged_final = campaign / "lhe_merged/final" / f"{cfg.sample_id}.lhe"
        overall = "success" if len(success) == expected_shards else ("partial" if success else "missing")
        sample_rows.append({
            "campaign_id": campaign_id,
            "sample_id": cfg.sample_id,
            "initial_state": cfg.initial_state,
            "decay_channel": cfg.decay_channel,
            "polarization": cfg.polarization,
            "sqrt_s_GeV": cfg.sqrt_s_GeV,
            "expected_shards": expected_shards,
            "successful_shards": len(success),
            "failed_or_missing_shards": expected_shards - len(success),
            "events_per_shard": cfg.events_per_shard,
            "expected_events": expected_events,
            "generated_events": generated_events,
            "raw_lhe_files": sum(bool(row["raw_lhe_path"]) for row in rows),
            "final_lhe_files": sum(bool(row["final_lhe_path"]) for row in rows),
            "inclusive_cross_section_fb": f"{mean:.12g}" if math.isfinite(mean) else "",
            "inclusive_cross_section_error_fb": f"{error:.12g}" if math.isfinite(error) else "",
            "exclusive_cross_section_fb": f"{exclusive:.12g}" if exclusive != "" else "",
            "forced_decay_weight": weight,
            "merged_raw_lhe_path": str(merged_raw) if merged_raw.exists() else "",
            "merged_final_lhe_path": str(merged_final) if merged_final.exists() else "",
            "status": overall,
            "updated_utc": utc_now(),
        })

    sample_manifest = manifests / "sample_manifest.csv"
    write_csv(sample_manifest, SAMPLE_FIELDS, sample_rows)

    summary = {
        "campaign_id": campaign_id,
        "campaign_root": str(campaign),
        "updated_utc": utc_now(),
        "expected_shards": len(shard_rows),
        "successful_shards": sum(row["status"] == "success" for row in shard_rows),
        "samples": len(sample_rows),
        "successful_samples": sum(row["status"] == "success" for row in sample_rows),
    }
    (manifests / "manifest_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {shard_manifest}")
    print(f"Wrote {sample_manifest}")
    print(
        f"Shards: success={summary['successful_shards']}/{summary['expected_shards']}; "
        f"samples={summary['successful_samples']}/{summary['samples']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
