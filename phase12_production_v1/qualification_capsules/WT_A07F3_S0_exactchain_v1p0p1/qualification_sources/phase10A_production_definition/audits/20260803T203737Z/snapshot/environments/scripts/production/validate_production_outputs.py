#!/usr/bin/env python3
"""Strict generator/sample-integrity validation for WHIZARD production shards."""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

from production_common import (
    campaign_root as default_campaign_root,
    default_output_root,
    ensure_eos,
    expected_final_state,
    filter_configs,
    final_state_pdgs_from_block,
    iter_lhe_event_blocks,
    read_configs,
    read_lhe_init,
    repo_root_from_script,
    sha256,
    utc_now,
    write_csv,
)

FIELDS = [
    "check", "group", "sample_id", "shard_label", "verdict", "value", "limit", "detail",
]


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script(__file__)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=root / "configs/production/production_500GeV_ISR_sc_v1.csv")
    p.add_argument("--campaign-root", type=Path, default=None)
    p.add_argument("--sample", action="append", default=[])
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--stage", choices=("raw", "final"), default="raw")
    p.add_argument("--scan-events", type=int, default=100, help="0 scans all events")
    p.add_argument("--max-relative-integration-error", type=float, default=0.005)
    p.add_argument("--max-excess-weight-percent", type=float, default=0.1)
    p.add_argument("--max-shard-cross-section-pull", type=float, default=5.0)
    p.add_argument("--max-shard-cross-section-relative-spread", type=float, default=0.01)
    p.add_argument("--require-merged", action="store_true")
    p.add_argument("--allow-incomplete", action="store_true")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--allow-non-eos", action="store_true")
    return p.parse_args()


def check(rows: list[dict[str, object]], name: str, group: str, sample: str, shard: str,
          verdict: str, value: object = "", limit: object = "", detail: str = "") -> None:
    rows.append({
        "check": name,
        "group": group,
        "sample_id": sample,
        "shard_label": shard,
        "verdict": verdict,
        "value": value,
        "limit": limit,
        "detail": detail,
    })


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def log_polarization_evidence(text: str, polarization: str) -> bool:
    beam1 = re.search(r"polarization \(beam 1\):(?P<body>.*?)(?:polarization \(beam 2\):)", text, re.S)
    beam2 = re.search(r"polarization \(beam 2\):(?P<body>.*?)(?:polarization degree|Beam data)", text, re.S)
    if not beam1 or not beam2:
        return False
    expected1, expected2 = (("@(-1: -1:", "@(+1: +1:"),
                            ("@(+1: +1:", "@(-1: -1:"))[polarization == "RL100"]
    return expected1 in beam1.group("body") and expected2 in beam2.group("body")


def scan_final_state(path: Path, channel: str, maximum: int) -> tuple[int, int, str]:
    expected = set(expected_final_state(channel))
    scanned = 0
    failures = 0
    first_detail = ""
    for block in iter_lhe_event_blocks(path):
        scanned += 1
        final = final_state_pdgs_from_block(block)
        missing = sorted(expected.difference(final))
        if missing:
            failures += 1
            if not first_detail:
                first_detail = f"missing PDGs {missing}; final={final}"
        if maximum and scanned >= maximum:
            break
    return scanned, failures, first_detail


def main() -> int:
    args = parse_args()
    configs = filter_configs(read_configs(args.config), args.sample)
    selected = {cfg.sample_id: cfg for cfg in configs}
    campaign_id = configs[0].campaign_id
    campaign = args.campaign_root or default_campaign_root(default_output_root(), campaign_id, smoke=args.smoke)
    ensure_eos(campaign, allow_non_eos=args.allow_non_eos)
    shard_rows = [row for row in load_rows(campaign / "manifests/shard_manifest.csv") if row["sample_id"] in selected]
    sample_rows = {row["sample_id"]: row for row in load_rows(campaign / "manifests/sample_manifest.csv") if row["sample_id"] in selected}

    checks: list[dict[str, object]] = []
    seed_owner: dict[int, str] = {}
    checksum_owner: dict[str, str] = {}

    for row in shard_rows:
        cfg = selected[row["sample_id"]]
        sample = cfg.sample_id
        shard = row["shard_label"]
        status_ok = row["status"] == "success"
        check(checks, "shard_status", "shard", sample, shard,
              "PASS" if status_ok else ("WARN" if args.allow_incomplete else "FAIL"),
              row["status"], "success")

        rc_ok = str(row["whizard_return_code"]) in {"0", "0.0"}
        check(checks, "whizard_return_code", "shard", sample, shard,
              "PASS" if rc_ok else "FAIL", row["whizard_return_code"], 0)

        try:
            seed = int(row["seed"])
            owner = seed_owner.get(seed)
            unique = owner is None
            if unique:
                seed_owner[seed] = f"{sample}/{shard}"
            check(checks, "unique_seed", "campaign", sample, shard,
                  "PASS" if unique else "FAIL", seed, "globally unique",
                  "" if unique else f"already used by {owner}")
        except ValueError:
            check(checks, "unique_seed", "campaign", sample, shard, "FAIL", row["seed"], "integer")

        requested = int(row["requested_events"] or 0)
        generated = int(row["generated_events"] or 0)
        check(checks, "event_count", "shard", sample, shard,
              "PASS" if requested == generated and requested > 0 else "FAIL",
              generated, requested)

        isr_enabled = str(row["input_has_isr"]).lower() == "true"
        check(
            checks,
            "sindarin_isr_enabled",
            "configuration",
            sample,
            shard,
            "PASS" if isr_enabled else "FAIL",
            row["input_has_isr"],
            True,
        )

        exact_spin_enabled = str(row["input_has_exact_spin"]).lower() == "true"
        expected_exact_spin = cfg.spin_correlated
        check(
            checks,
            "sindarin_spin_mode",
            "configuration",
            sample,
            shard,
            "PASS" if exact_spin_enabled == expected_exact_spin else "FAIL",
            exact_spin_enabled,
            expected_exact_spin,
            (
                "spin-correlated sample requires isotropic_decay=false"
                if cfg.spin_correlated
                else "isotropic control requires isotropic_decay=true"
            ),
        )

        polarized_events = str(row["input_has_polarized_events"]).lower() == "true"
        check(
            checks,
            "sindarin_polarized_events",
            "configuration",
            sample,
            shard,
            "PASS" if polarized_events else "FAIL",
            row["input_has_polarized_events"],
            True,
        )

        run_dir = Path(row["run_directory"]) if row.get("run_directory") else None
        input_path = run_dir / "input.sin" if run_dir else None
        input_text = (
            input_path.read_text(errors="replace")
            if input_path and input_path.exists()
            else ""
        )
        expected_isotropic = "false" if cfg.spin_correlated else "true"
        isotropic_token = f"?isotropic_decay = {expected_isotropic}"
        diagonal_token = "?diagonal_decay = false"
        check(
            checks,
            "sindarin_isotropic_decay_contract",
            "configuration",
            sample,
            shard,
            "PASS" if isotropic_token in input_text else "FAIL",
            isotropic_token in input_text,
            isotropic_token,
            str(input_path or "missing input.sin"),
        )
        check(
            checks,
            "sindarin_diagonal_decay_disabled",
            "configuration",
            sample,
            shard,
            "PASS" if diagonal_token in input_text else "FAIL",
            diagonal_token in input_text,
            diagonal_token,
            str(input_path or "missing input.sin"),
        )

        log_path = Path(row["log_path"]) if row.get("log_path") else None
        log_text = log_path.read_text(errors="replace") if log_path and log_path.exists() else ""
        exact_decay_count = log_text.count("Decay options: helicity treated exactly")
        if cfg.spin_correlated:
            exact_decay_ok = exact_decay_count >= 2
            exact_decay_limit = ">=2"
            exact_decay_detail = "spin-correlated decay must be treated exactly"
        else:
            exact_decay_ok = True
            exact_decay_limit = "not required"
            exact_decay_detail = (
                "isotropic-decay control is validated by the rendered "
                "SINDARIN contract"
            )
        check(
            checks,
            "log_exact_decay_spin",
            "configuration",
            sample,
            shard,
            "PASS" if exact_decay_ok else "FAIL",
            exact_decay_count,
            exact_decay_limit,
            exact_decay_detail,
        )
        pol_evidence = log_polarization_evidence(log_text, cfg.polarization)
        check(checks, "log_polarization_evidence", "configuration", sample, shard,
              "PASS" if pol_evidence else "FAIL", pol_evidence, True)
        isr_evidence = "isr" in log_text.lower()
        check(checks, "log_isr_evidence", "configuration", sample, shard,
              "PASS" if isr_evidence else "WARN", isr_evidence, True,
              "SINDARIN ISR check remains authoritative if this WHIZARD build prints no ISR label")

        try:
            relerr = float(row["relative_integration_error"])
            ok = relerr <= args.max_relative_integration_error
            check(checks, "integration_precision", "integration", sample, shard,
                  "PASS" if ok else "FAIL", f"{relerr:.6g}", args.max_relative_integration_error)
        except ValueError:
            check(checks, "integration_precision", "integration", sample, shard,
                  "FAIL", row["relative_integration_error"], args.max_relative_integration_error)

        try:
            excess = float(row["excess_weight_fraction_percent"] or 0)
            ok = excess <= args.max_excess_weight_percent
            check(checks, "excess_weight_fraction", "events", sample, shard,
                  "PASS" if ok else "FAIL", excess, args.max_excess_weight_percent)
        except ValueError:
            check(checks, "excess_weight_fraction", "events", sample, shard,
                  "FAIL", row["excess_weight_fraction_percent"], args.max_excess_weight_percent)

        raw_path = Path(row["raw_lhe_path"]) if row.get("raw_lhe_path") else None
        chosen_path = raw_path if args.stage == "raw" else (Path(row["final_lhe_path"]) if row.get("final_lhe_path") else None)
        exists = chosen_path is not None and chosen_path.exists()
        check(checks, f"{args.stage}_lhe_exists", "files", sample, shard,
              "PASS" if exists else "FAIL", str(chosen_path or ""), "existing file")
        if not exists:
            continue

        digest = sha256(chosen_path)
        owner = checksum_owner.get(digest)
        unique = owner is None
        if unique:
            checksum_owner[digest] = f"{sample}/{shard}"
        check(checks, f"{args.stage}_lhe_unique_checksum", "files", sample, shard,
              "PASS" if unique else "FAIL", digest, "unique",
              "" if unique else f"same checksum as {owner}")

        init = read_lhe_init(chosen_path)
        expected_incoming = (11, -11) if cfg.initial_state == "ee" else (13, -13)
        incoming_ok = (init.incoming_pdg1, init.incoming_pdg2) == expected_incoming
        check(checks, "incoming_beam_pdg", "lhe", sample, shard,
              "PASS" if incoming_ok else "FAIL",
              f"{init.incoming_pdg1},{init.incoming_pdg2}", f"{expected_incoming[0]},{expected_incoming[1]}")

        scanned, failures, detail = scan_final_state(chosen_path, cfg.decay_channel, args.scan_events)
        check(checks, "forced_decay_final_state", "lhe", sample, shard,
              "PASS" if scanned > 0 and failures == 0 else "FAIL",
              f"scanned={scanned}; failures={failures}", "failures=0", detail)

        if args.stage == "final":
            if raw_path is None or not raw_path.exists():
                check(checks, "final_normalization", "normalization", sample, shard, "FAIL", "", "raw LHE available")
            else:
                raw_init = read_lhe_init(raw_path)
                sample_row = sample_rows[sample]
                try:
                    weight = float(sample_row["forced_decay_weight"])
                    ratio = init.cross_section_pb / raw_init.cross_section_pb
                    ok = abs(ratio - weight) <= max(1e-12, abs(weight) * 1e-8)
                    check(checks, "final_normalization", "normalization", sample, shard,
                          "PASS" if ok else "FAIL", f"{ratio:.12g}", f"{weight:.12g}")
                except (ValueError, ZeroDivisionError):
                    check(checks, "final_normalization", "normalization", sample, shard,
                          "FAIL", "unparsable", "finite forced-decay weight")

    # Ensure every configured shard has a manifest row.
    by_pair = {(row["sample_id"], row["shard_label"]) for row in shard_rows}
    for cfg in configs:
        indices = [0] if args.smoke else range(cfg.n_shards)
        for idx in indices:
            pair = (cfg.sample_id, cfg.shard_label(idx))
            if pair not in by_pair:
                check(checks, "expected_shard_present", "campaign", pair[0], pair[1],
                      "WARN" if args.allow_incomplete else "FAIL", False, True)

    # Shard cross sections should be statistically/relatively consistent within each sample.
    for cfg in configs:
        rows = [row for row in shard_rows if row["sample_id"] == cfg.sample_id and row["status"] == "success"]
        values: list[tuple[str, float, float]] = []
        for row in rows:
            try:
                values.append((row["shard_label"], float(row["inclusive_cross_section_fb"]), float(row["inclusive_cross_section_error_fb"])))
            except ValueError:
                pass
        if len(values) >= 2:
            weights = [1.0 / (error * error) for _, _, error in values if error > 0]
            mean = sum(value * weight for (_, value, error), weight in zip(values, weights)) / sum(weights)
            for label, value, error in values:
                relative = abs(value - mean) / abs(mean) if mean else math.inf
                pull = abs(value - mean) / error if error else math.inf
                ok = relative <= args.max_shard_cross_section_relative_spread or pull <= args.max_shard_cross_section_pull
                check(checks, "shard_cross_section_consistency", "integration", cfg.sample_id, label,
                      "PASS" if ok else "FAIL", f"relative={relative:.6g}; pull={pull:.6g}",
                      f"relative<={args.max_shard_cross_section_relative_spread} OR pull<={args.max_shard_cross_section_pull}")

        if args.require_merged:
            merged = campaign / "lhe_merged" / args.stage / f"{cfg.sample_id}.lhe"
            merged_gz = campaign / "lhe_merged" / args.stage / f"{cfg.sample_id}.lhe.gz"
            candidate = merged if merged.exists() else merged_gz
            ok = candidate.exists()
            check(checks, "merged_lhe_exists", "collection", cfg.sample_id, "",
                  "PASS" if ok else "FAIL", str(candidate if ok else ""), "existing merged LHE")

    output_dir = campaign / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = output_dir / f"production_validation_{args.stage}.csv"
    out_md = output_dir / f"production_validation_{args.stage}.md"
    write_csv(out_csv, FIELDS, checks)
    counts = {verdict: sum(row["verdict"] == verdict for row in checks) for verdict in ("PASS", "WARN", "FAIL")}
    lines = [
        f"# WHIZARD production validation: {args.stage}", "",
        f"- Campaign: `{campaign}`",
        f"- Updated: `{utc_now()}`",
        f"- Checks: **{len(checks)}**",
        f"- PASS: **{counts['PASS']}**",
        f"- WARN: **{counts['WARN']}**",
        f"- FAIL: **{counts['FAIL']}**", "",
        "| Check | Sample | Shard | Verdict | Value | Limit/detail |",
        "|---|---|---|---|---|---|",
    ]
    for row in checks:
        if row["verdict"] != "PASS":
            lines.append(
                f"| {row['check']} | `{row['sample_id']}` | `{row['shard_label']}` | "
                f"**{row['verdict']}** | {row['value']} | {row['limit']} {row['detail']} |"
            )
    if counts["WARN"] == 0 and counts["FAIL"] == 0:
        lines.append("| — | — | — | **All checks passed** | — | — |")
    lines.append("")
    out_md.write_text("\n".join(lines))
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print(f"Checks={len(checks)} PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    return 1 if args.strict and counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
