#!/usr/bin/env python3
"""Validate WHIZARD integration results recorded in the sample manifest."""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Result:
    sample_id: str
    initial_state: str
    sqrt_s_GeV: str
    decay_channel: str
    polarization: str
    spin_mode: str
    cross: float
    error: float
    rel_error: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    p.add_argument("--repo-root", type=Path, default=default_root)
    p.add_argument("--manifest", type=Path, default=None)
    p.add_argument("--output-csv", type=Path, default=None)
    p.add_argument("--output-md", type=Path, default=None)
    p.add_argument("--max-relative-integration-error", type=float, default=0.02)
    p.add_argument("--max-pair-relative-difference", type=float, default=0.03)
    p.add_argument("--max-pair-pull", type=float, default=3.0)
    p.add_argument("--strict", action="store_true")
    return p.parse_args()


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load(path: Path) -> tuple[list[Result], list[dict[str, str]]]:
    results: list[Result] = []
    raw: list[dict[str, str]] = []
    if not path.exists():
        return results, raw
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            raw.append(row)
            cross = as_float(row.get("cross_section_fb", ""))
            error = as_float(row.get("cross_section_error_fb", ""))
            if cross is None or error is None or cross < 0 or error < 0:
                continue
            rel = error / cross if cross else math.inf
            results.append(Result(
                row.get("sample_id", ""), row.get("initial_state", ""),
                row.get("sqrt_s_GeV", ""), row.get("decay_channel", ""),
                row.get("polarization", ""), row.get("spin_mode", ""),
                cross, error, rel,
            ))
    return results, raw


def metrics(a: Result, b: Result) -> tuple[float, float]:
    scale = 0.5 * (abs(a.cross) + abs(b.cross))
    relative = abs(a.cross - b.cross) / scale if scale else 0.0
    sigma = math.hypot(a.error, b.error)
    pull = abs(a.cross - b.cross) / sigma if sigma else (0.0 if a.cross == b.cross else math.inf)
    return relative, pull


def pair_verdict(relative: float, pull: float, max_relative: float, max_pull: float) -> str:
    return "PASS" if (relative <= max_relative or pull <= max_pull) else "FAIL"


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    manifest = args.manifest or root / "metadata" / "sample_manifest.csv"
    out_csv = args.output_csv or root / "validation" / "summaries" / "cross_section_validation.csv"
    out_md = args.output_md or root / "validation" / "summaries" / "cross_section_validation.md"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    results, raw = load(manifest)
    checks: list[dict[str, str]] = []

    for result in sorted(results, key=lambda item: item.sample_id):
        checks.append({
            "check_type": "integration_precision",
            "sample_a": result.sample_id,
            "sample_b": "",
            "cross_section_a_fb": f"{result.cross:.12g}",
            "cross_section_b_fb": "",
            "relative_difference": "",
            "pull": "",
            "verdict": "PASS" if result.rel_error <= args.max_relative_integration_error else "FAIL",
            "detail": f"relative integration error={result.rel_error:.6g}; limit={args.max_relative_integration_error:.6g}",
        })

    by_key = {
        (r.initial_state, r.sqrt_s_GeV, r.decay_channel, r.polarization, r.spin_mode): r
        for r in results
    }

    energies = sorted({r.sqrt_s_GeV for r in results})
    decays = sorted({r.decay_channel for r in results})
    for energy in energies:
        for decay in decays:
            for polarization in ("unpol", "LR100", "RL100"):
                for spin in ("sc", "iso"):
                    a = by_key.get(("ee", energy, decay, polarization, spin))
                    b = by_key.get(("mumu", energy, decay, polarization, spin))
                    if a and b:
                        relative, pull = metrics(a, b)
                        checks.append({
                            "check_type": "ee_vs_mumu",
                            "sample_a": a.sample_id,
                            "sample_b": b.sample_id,
                            "cross_section_a_fb": f"{a.cross:.12g}",
                            "cross_section_b_fb": f"{b.cross:.12g}",
                            "relative_difference": f"{relative:.12g}",
                            "pull": f"{pull:.12g}",
                            "verdict": pair_verdict(relative, pull, args.max_pair_relative_difference, args.max_pair_pull),
                            "detail": "same energy, decay, polarization and spin mode; ISR/beam spectra disabled",
                        })

    for initial in ("ee", "mumu"):
        for energy in energies:
            for decay in decays:
                for polarization in ("unpol", "LR100", "RL100"):
                    a = by_key.get((initial, energy, decay, polarization, "sc"))
                    b = by_key.get((initial, energy, decay, polarization, "iso"))
                    if a and b:
                        relative, pull = metrics(a, b)
                        checks.append({
                            "check_type": "sc_vs_iso_normalization",
                            "sample_a": a.sample_id,
                            "sample_b": b.sample_id,
                            "cross_section_a_fb": f"{a.cross:.12g}",
                            "cross_section_b_fb": f"{b.cross:.12g}",
                            "relative_difference": f"{relative:.12g}",
                            "pull": f"{pull:.12g}",
                            "verdict": pair_verdict(relative, pull, args.max_pair_relative_difference, args.max_pair_pull),
                            "detail": "same hard process and beam state; only cascade spin treatment differs",
                        })

    fields = [
        "check_type", "sample_a", "sample_b", "cross_section_a_fb",
        "cross_section_b_fb", "relative_difference", "pull", "verdict", "detail"
    ]
    with out_csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(checks)

    failures = sum(check["verdict"] == "FAIL" for check in checks)
    lines = [
        "# WHIZARD cross-section validation", "",
        f"- Manifest: `{manifest}`",
        f"- Samples with parsed cross sections: **{len(results)}/{len(raw)}**",
        f"- Pending or unparsable samples: **{len(raw) - len(results)}**",
        f"- Completed checks: **{len(checks)}**",
        f"- Failed checks: **{failures}**", "",
    ]
    if checks:
        lines += [
            "| Check | Sample A | Sample B | Relative difference | Pull | Verdict |",
            "|---|---|---|---:|---:|---|",
        ]
        for check in checks:
            lines.append(
                f"| {check['check_type']} | `{check['sample_a']}` | `{check['sample_b']}` | "
                f"{check['relative_difference'] or '—'} | {check['pull'] or '—'} | **{check['verdict']}** |"
            )
        lines.append("")
    else:
        lines += [
            "No cross sections are available yet. Run the WHIZARD matrix, refresh",
            "the manifest, and rerun this validator.", "",
        ]
    lines += [
        "## Interpretation", "",
        "- `ee_vs_mumu` should agree before ISR and machine spectra are enabled.",
        "- `sc_vs_iso_normalization` should agree in normalization; the intended",
        "  difference is in decay-angle shapes.",
        "- A pair fails only when both the relative difference and pull exceed",
        "  their thresholds.",
        "- These checks do not replace LHE-level angular-distribution validation.", "",
    ]
    out_md.write_text("\n".join(lines))

    print(f"Read {len(raw)} manifest rows; parsed {len(results)} cross sections.")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    if failures:
        print(f"Validation failures: {failures}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
