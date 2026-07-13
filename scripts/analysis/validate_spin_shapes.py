#!/usr/bin/env python3
"""Validate LHE parsing, observable integrity, and expected shape behavior."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

CHECK_FIELDS = [
    "check_type",
    "group_id",
    "sample_a",
    "sample_b",
    "observable",
    "value",
    "threshold",
    "verdict",
    "detail",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--parse-summary", type=Path, default=None)
    parser.add_argument("--observable-summary", type=Path, default=None)
    parser.add_argument("--comparison-summary", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--max-cosine-excess", type=float, default=1.0e-8)
    parser.add_argument("--max-control-js", type=float, default=0.02)
    parser.add_argument("--min-control-ks-pvalue", type=float, default=1.0e-4)
    parser.add_argument("--min-signal-js", type=float, default=1.0e-4)
    parser.add_argument("--max-signal-ks-pvalue", type=float, default=0.01)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--strict-warnings", action="store_true")
    return parser.parse_args()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def as_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def check(
    check_type: str,
    group_id: str,
    verdict: str,
    detail: str,
    *,
    sample_a: str = "",
    sample_b: str = "",
    observable: str = "",
    value: str = "",
    threshold: str = "",
) -> dict[str, str]:
    return {
        "check_type": check_type,
        "group_id": group_id,
        "sample_a": sample_a,
        "sample_b": sample_b,
        "observable": observable,
        "value": value,
        "threshold": threshold,
        "verdict": verdict,
        "detail": detail,
    }


def validate_parse(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for row in rows:
        sample = row.get("sample_id", "")
        parsed = as_int(row.get("parsed_events"))
        valid = as_int(row.get("valid_events"))
        invalid = as_int(row.get("invalid_events"))
        manifest = as_int(row.get("manifest_generated_events"))
        status = row.get("status", "")
        passed = (
            status == "PASS"
            and parsed is not None
            and valid == parsed
            and invalid == 0
            and (manifest is None or parsed == manifest)
        )
        checks.append(check(
            "lhe_parse_integrity",
            sample,
            "PASS" if passed else "FAIL",
            f"status={status}; parsed={parsed}; valid={valid}; invalid={invalid}; manifest={manifest}",
            sample_a=sample,
            value=str(parsed if parsed is not None else ""),
            threshold="all generated events valid",
        ))

        required_norm = [
            row.get("top_decay_br", ""),
            row.get("antitop_decay_br", ""),
            row.get("forced_decay_weight", ""),
            row.get("exclusive_cross_section_fb", ""),
        ]
        norm_ok = all(as_float(value) is not None for value in required_norm)
        checks.append(check(
            "forced_decay_normalization",
            sample,
            "PASS" if norm_ok else "WARN",
            "forced-decay branching fractions and exclusive cross section available"
            if norm_ok else "one or more forced-decay normalization fields are unavailable",
            sample_a=sample,
            threshold="all normalization fields finite",
        ))
    return checks


def validate_observables(rows: list[dict[str, str]], cosine_excess: float) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    limit = 1.0 + cosine_excess
    for row in rows:
        sample = row.get("sample_id", "")
        status = row.get("status", "")
        nonfinite = as_int(row.get("nonfinite_events"))
        checks.append(check(
            "observable_finiteness",
            sample,
            "PASS" if status == "PASS" and nonfinite == 0 else "FAIL",
            f"status={status}; nonfinite_events={nonfinite}",
            sample_a=sample,
            threshold="zero non-finite events",
        ))
        for key in ("max_abs_cos_theta_t", "max_abs_cos_theta_star_plus", "max_abs_cos_theta_star_minus"):
            value = as_float(row.get(key))
            passed = value is not None and value <= limit
            checks.append(check(
                "cosine_range",
                f"{sample}:{key}",
                "PASS" if passed else "FAIL",
                f"{key}={value}",
                sample_a=sample,
                observable=key,
                value="" if value is None else f"{value:.12g}",
                threshold=f"<= {limit:.12g}",
            ))
    return checks


def metric_passes_control(row: dict[str, str], max_js: float, min_ks_p: float) -> bool:
    js = as_float(row.get("js_divergence"))
    ks_p = as_float(row.get("ks_pvalue"))
    return (js is not None and js <= max_js) or (ks_p is not None and ks_p >= min_ks_p)


def metric_has_signal(row: dict[str, str], min_js: float, max_ks_p: float) -> bool:
    js = as_float(row.get("js_divergence"))
    ks_p = as_float(row.get("ks_pvalue"))
    return (js is not None and js >= min_js) and (ks_p is None or ks_p <= max_ks_p)


def validate_comparisons(
    rows: list[dict[str, str]],
    max_control_js: float,
    min_control_ks_p: float,
    min_signal_js: float,
    max_signal_ks_p: float,
) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("comparison_type", ""), row.get("sample_a", ""), row.get("sample_b", ""))].append(row)

    production_controls = {"cos_theta_t", "top_pt_GeV", "top_rapidity", "m_tt_GeV"}
    spin_signals = {
        "delta_phi_ll",
        "cos_opening_ll",
        "cos_theta_star_plus",
        "cos_theta_star_minus",
        "cos_theta_star_product",
        "cos_theta_star_plus__vs__cos_theta_star_minus",
    }
    ee_mumu_controls = production_controls | spin_signals | {"delta_R_ll", "m_ll_GeV"}

    for (comparison_type, sample_a, sample_b), pair_rows in sorted(grouped.items()):
        pair_id = f"{comparison_type}:{sample_a}:vs:{sample_b}"
        by_obs = {row.get("observable", ""): row for row in pair_rows}

        if comparison_type == "sc_vs_iso":
            failed_controls = [
                obs for obs in production_controls
                if obs in by_obs and not metric_passes_control(by_obs[obs], max_control_js, min_control_ks_p)
            ]
            checks.append(check(
                "sc_vs_iso_production_controls",
                pair_id,
                "PASS" if not failed_controls else "FAIL",
                "all production controls compatible" if not failed_controls else f"failed controls: {', '.join(sorted(failed_controls))}",
                sample_a=sample_a,
                sample_b=sample_b,
                threshold=f"JS<={max_control_js:g} OR KS p>={min_control_ks_p:g}",
            ))

            signaled = [
                obs for obs in spin_signals
                if obs in by_obs and metric_has_signal(by_obs[obs], min_signal_js, max_signal_ks_p)
            ]
            checks.append(check(
                "sc_vs_iso_spin_signal",
                pair_id,
                "PASS" if signaled else "FAIL",
                f"signal observables: {', '.join(sorted(signaled))}" if signaled else "no configured spin-sensitive observable passed the signal threshold",
                sample_a=sample_a,
                sample_b=sample_b,
                threshold=f"at least one observable with JS>={min_signal_js:g} AND KS p<={max_signal_ks_p:g}",
            ))

        elif comparison_type == "ee_vs_mumu":
            failed = [
                obs for obs in ee_mumu_controls
                if obs in by_obs and not metric_passes_control(by_obs[obs], max_control_js, min_control_ks_p)
            ]
            checks.append(check(
                "ee_vs_mumu_shape_control",
                pair_id,
                "PASS" if not failed else "FAIL",
                "all checked shapes compatible" if not failed else f"failed observables: {', '.join(sorted(failed))}",
                sample_a=sample_a,
                sample_b=sample_b,
                threshold=f"JS<={max_control_js:g} OR KS p>={min_control_ks_p:g}",
            ))

        elif comparison_type == "polarization":
            # LR-vs-RL is the strongest and least ambiguous polarization test.
            if ("LR100" in sample_a and "RL100" in sample_b) or ("RL100" in sample_a and "LR100" in sample_b):
                target = by_obs.get("cos_theta_t")
                has_signal = target is not None and metric_has_signal(target, min_signal_js, max_signal_ks_p)
                checks.append(check(
                    "lr_vs_rl_production_signal",
                    pair_id,
                    "PASS" if has_signal else "WARN",
                    "top production-angle polarization signal detected" if has_signal else "cos_theta_t did not pass the configured signal threshold",
                    sample_a=sample_a,
                    sample_b=sample_b,
                    observable="cos_theta_t",
                    threshold=f"JS>={min_signal_js:g} AND KS p<={max_signal_ks_p:g}",
                ))
    return checks


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CHECK_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, checks: list[dict[str, str]], inputs: dict[str, Path]) -> None:
    counts = {verdict: sum(row["verdict"] == verdict for row in checks) for verdict in ("PASS", "WARN", "FAIL")}
    lines = [
        "# WHIZARD angular/spin-shape validation",
        "",
        f"- Parse summary: `{inputs['parse']}`",
        f"- Observable summary: `{inputs['observables']}`",
        f"- Comparison summary: `{inputs['comparisons']}`",
        f"- Completed checks: **{len(checks)}**",
        f"- Passed: **{counts['PASS']}**",
        f"- Warnings: **{counts['WARN']}**",
        f"- Failed: **{counts['FAIL']}**",
        "",
        "| Check | Group | Sample A | Sample B | Observable | Verdict | Detail |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in checks:
        detail = row["detail"].replace("|", "\\|")
        lines.append(
            f"| {row['check_type']} | `{row['group_id']}` | `{row['sample_a']}` | `{row['sample_b']}` | "
            f"{row['observable'] or '—'} | **{row['verdict']}** | {detail} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Parse and finiteness failures indicate malformed event records or an observable-construction bug.",
        "- `sc_vs_iso_production_controls` tests that changing only decay spin treatment does not alter top production shapes.",
        "- `sc_vs_iso_spin_signal` requires a visible difference in at least one charged-lepton or helicity observable.",
        "- `ee_vs_mumu_shape_control` should pass before ISR and machine-specific beam spectra are introduced.",
        "- LR-vs-RL polarization checks are diagnostic warnings by default because the exact sensitivity depends on the chosen observable and energy.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    paths = {
        "parse": (args.parse_summary or root / "validation" / "angular_summaries" / "lhe_parse_summary.csv").resolve(),
        "observables": (args.observable_summary or root / "validation" / "angular_summaries" / "spin_observable_summary.csv").resolve(),
        "comparisons": (args.comparison_summary or root / "validation" / "angular_summaries" / "spin_shape_comparisons.csv").resolve(),
    }
    output_csv = (args.output_csv or root / "validation" / "angular_summaries" / "spin_shape_validation.csv").resolve()
    output_md = (args.output_md or root / "validation" / "angular_summaries" / "spin_shape_validation.md").resolve()

    try:
        parse_rows = load_csv(paths["parse"])
        observable_rows = load_csv(paths["observables"])
        comparison_rows = load_csv(paths["comparisons"])
    except FileNotFoundError as exc:
        print(f"ERROR: required input does not exist: {exc}", file=sys.stderr)
        return 2

    checks = []
    checks.extend(validate_parse(parse_rows))
    checks.extend(validate_observables(observable_rows, args.max_cosine_excess))
    checks.extend(validate_comparisons(
        comparison_rows,
        args.max_control_js,
        args.min_control_ks_pvalue,
        args.min_signal_js,
        args.max_signal_ks_pvalue,
    ))

    write_csv(output_csv, checks)
    write_markdown(output_md, checks, paths)
    failures = sum(row["verdict"] == "FAIL" for row in checks)
    warnings = sum(row["verdict"] == "WARN" for row in checks)
    print(f"Wrote {output_csv}")
    print(f"Wrote {output_md}")
    print(f"Checks={len(checks)} PASS={len(checks)-failures-warnings} WARN={warnings} FAIL={failures}")
    if args.strict and failures:
        return 1
    if args.strict_warnings and (failures or warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
