#!/usr/bin/env python3
"""Compare WHIZARD ttbar spin/polarization samples and make validation plots.

The script consumes *_spin_observables.csv tables, constructs all central
comparison pairs, calculates normalized-shape metrics, and writes one- and
two-dimensional plots into the validation hierarchy.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class ObservableSpec:
    name: str
    category: str
    label: str
    bins: int
    low: float
    high: float


OBSERVABLES = (
    ObservableSpec("cos_theta_t", "production", r"$\cos\theta_t$", 30, -1.0, 1.0),
    ObservableSpec("top_pt_GeV", "production", r"$p_{T,t}$ [GeV]", 30, 0.0, 250.0),
    ObservableSpec("top_rapidity", "production", r"$y_t$", 30, -2.5, 2.5),
    ObservableSpec("m_tt_GeV", "production", r"$m_{t\bar t}$ [GeV]", 40, 495.0, 505.0),
    ObservableSpec("delta_phi_ll", "dilepton", r"$|\Delta\phi_{\ell\ell}|$", 30, 0.0, math.pi),
    ObservableSpec("delta_R_ll", "dilepton", r"$\Delta R_{\ell\ell}$", 35, 0.0, 7.0),
    ObservableSpec("cos_opening_ll", "dilepton", r"$\cos\varphi_{\ell\ell}$", 30, -1.0, 1.0),
    ObservableSpec("m_ll_GeV", "dilepton", r"$m_{\ell\ell}$ [GeV]", 35, 0.0, 350.0),
    ObservableSpec("cos_theta_star_plus", "helicity_angles", r"$\cos\theta^*_+$", 30, -1.0, 1.0),
    ObservableSpec("cos_theta_star_minus", "helicity_angles", r"$\cos\theta^*_-$", 30, -1.0, 1.0),
    ObservableSpec("cos_theta_star_product", "helicity_angles", r"$\cos\theta^*_+\cos\theta^*_-$", 30, -1.0, 1.0),
    ObservableSpec("lplus_energy_lab_GeV", "helicity_angles", r"$E_{\ell^+}$ [GeV]", 35, 0.0, 250.0),
    ObservableSpec("lminus_energy_lab_GeV", "helicity_angles", r"$E_{\ell^-}$ [GeV]", 35, 0.0, 250.0),
)

METRIC_FIELDS = [
    "comparison_type",
    "pair_id",
    "sample_a",
    "sample_b",
    "initial_state_a",
    "initial_state_b",
    "polarization_a",
    "polarization_b",
    "spin_mode_a",
    "spin_mode_b",
    "observable",
    "category",
    "dimension",
    "n_a",
    "n_b",
    "mean_a",
    "mean_b",
    "std_a",
    "std_b",
    "mean_difference",
    "cohen_d",
    "ks_statistic",
    "ks_pvalue",
    "js_divergence",
    "l1_distance",
    "chi2",
    "ndf",
    "chi2_ndf",
    "max_abs_bin_difference",
    "plot_path",
]


@dataclass
class SampleData:
    sample_id: str
    initial_state: str
    polarization: str
    spin_mode: str
    values: dict[str, np.ndarray]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--plots-dir", type=Path, default=None)
    parser.add_argument("--summary-csv", type=Path, default=None)
    parser.add_argument("--summary-md", type=Path, default=None)
    parser.add_argument(
        "--comparison-groups",
        default="sc_vs_iso,ee_vs_mumu,polarization",
        help="Comma-separated subset of sc_vs_iso,ee_vs_mumu,polarization",
    )
    parser.add_argument("--sample", action="append", default=[], help="Sample ID/glob; repeatable")
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dpi", type=int, default=160)
    return parser.parse_args()


def sample_selected(sample_id: str, patterns: list[str]) -> bool:
    if not patterns:
        return True
    from fnmatch import fnmatch
    return any(fnmatch(sample_id, pattern) for pattern in patterns)


def load_sample(path: Path) -> SampleData:
    columns = {spec.name: [] for spec in OBSERVABLES}
    metadata: dict[str, str] = {}
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            if row.get("event_finite") != "1":
                continue
            if not metadata:
                metadata = {
                    "sample_id": row.get("sample_id", path.name.removesuffix("_spin_observables.csv")),
                    "initial_state": row.get("initial_state", ""),
                    "polarization": row.get("polarization", ""),
                    "spin_mode": row.get("spin_mode", ""),
                }
            for spec in OBSERVABLES:
                value = row.get(spec.name, "")
                if value:
                    parsed = float(value)
                    if math.isfinite(parsed):
                        columns[spec.name].append(parsed)
    if not metadata:
        raise ValueError(f"No finite event rows in {path}")
    return SampleData(
        sample_id=metadata["sample_id"],
        initial_state=metadata["initial_state"],
        polarization=metadata["polarization"],
        spin_mode=metadata["spin_mode"],
        values={name: np.asarray(values, dtype=float) for name, values in columns.items()},
    )


def ks_two_sample(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    if len(a) == 0 or len(b) == 0:
        return math.nan, math.nan
    a_sorted = np.sort(a)
    b_sorted = np.sort(b)
    combined = np.concatenate((a_sorted, b_sorted))
    cdf_a = np.searchsorted(a_sorted, combined, side="right") / len(a_sorted)
    cdf_b = np.searchsorted(b_sorted, combined, side="right") / len(b_sorted)
    statistic = float(np.max(np.abs(cdf_a - cdf_b)))
    effective = math.sqrt(len(a) * len(b) / (len(a) + len(b)))
    if statistic <= 0.0:
        return 0.0, 1.0
    lam = (effective + 0.12 + 0.11 / max(effective, 1.0e-12)) * statistic
    total = 0.0
    for k in range(1, 101):
        term = 2.0 * ((-1.0) ** (k - 1)) * math.exp(-2.0 * k * k * lam * lam)
        total += term
        if abs(term) < 1.0e-14:
            break
    return statistic, min(1.0, max(0.0, total))


def histogram_prob(values: np.ndarray, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    counts, _ = np.histogram(values, bins=edges)
    total = counts.sum()
    probabilities = counts.astype(float) / total if total else np.zeros_like(counts, dtype=float)
    return counts.astype(float), probabilities


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    eps = 1.0e-15
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = (p + eps) / np.sum(p + eps)
    q = (q + eps) / np.sum(q + eps)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return math.nan
    va = float(np.var(a, ddof=1))
    vb = float(np.var(b, ddof=1))
    pooled = ((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)
    if pooled <= 0.0:
        return 0.0 if np.mean(a) == np.mean(b) else math.inf
    return float((np.mean(a) - np.mean(b)) / math.sqrt(pooled))


def shape_metrics(a: np.ndarray, b: np.ndarray, edges: np.ndarray) -> dict[str, float]:
    counts_a, prob_a = histogram_prob(a, edges)
    counts_b, prob_b = histogram_prob(b, edges)
    ks, ks_p = ks_two_sample(a, b)
    l1 = float(np.sum(np.abs(prob_a - prob_b)))
    js = js_divergence(prob_a, prob_b)
    maxdiff = float(np.max(np.abs(prob_a - prob_b))) if len(prob_a) else math.nan

    # Symmetric two-sample binned chi-square, valid for shape comparisons.
    n_a = max(float(counts_a.sum()), 1.0)
    n_b = max(float(counts_b.sum()), 1.0)
    scale = n_a / n_b
    variance = counts_a + scale * scale * counts_b
    mask = variance > 0.0
    chi2 = float(np.sum(((counts_a[mask] - scale * counts_b[mask]) ** 2) / variance[mask]))
    ndf = max(int(np.count_nonzero(mask)) - 1, 0)

    return {
        "mean_a": float(np.mean(a)) if len(a) else math.nan,
        "mean_b": float(np.mean(b)) if len(b) else math.nan,
        "std_a": float(np.std(a, ddof=1)) if len(a) > 1 else math.nan,
        "std_b": float(np.std(b, ddof=1)) if len(b) > 1 else math.nan,
        "mean_difference": float(np.mean(a) - np.mean(b)) if len(a) and len(b) else math.nan,
        "cohen_d": cohen_d(a, b),
        "ks_statistic": ks,
        "ks_pvalue": ks_p,
        "js_divergence": js,
        "l1_distance": l1,
        "chi2": chi2,
        "ndf": float(ndf),
        "chi2_ndf": chi2 / ndf if ndf else math.nan,
        "max_abs_bin_difference": maxdiff,
    }


def fmt(value: float | int | None) -> str:
    if value is None:
        return ""
    try:
        if not math.isfinite(float(value)):
            return ""
    except (TypeError, ValueError):
        return ""
    return f"{float(value):.12g}"


def pair_definitions(samples: dict[str, SampleData], groups: set[str]) -> list[tuple[str, SampleData, SampleData]]:
    by_key = {
        (sample.initial_state, sample.polarization, sample.spin_mode): sample
        for sample in samples.values()
    }
    pairs: list[tuple[str, SampleData, SampleData]] = []

    if "sc_vs_iso" in groups:
        for initial in ("ee", "mumu"):
            for polarization in ("unpol", "LR100", "RL100"):
                a = by_key.get((initial, polarization, "sc"))
                b = by_key.get((initial, polarization, "iso"))
                if a and b:
                    pairs.append(("sc_vs_iso", a, b))

    if "ee_vs_mumu" in groups:
        for polarization in ("unpol", "LR100", "RL100"):
            for spin in ("sc", "iso"):
                a = by_key.get(("ee", polarization, spin))
                b = by_key.get(("mumu", polarization, spin))
                if a and b:
                    pairs.append(("ee_vs_mumu", a, b))

    if "polarization" in groups:
        for initial in ("ee", "mumu"):
            for spin in ("sc", "iso"):
                for pol_a, pol_b in (("LR100", "RL100"), ("LR100", "unpol"), ("RL100", "unpol")):
                    a = by_key.get((initial, pol_a, spin))
                    b = by_key.get((initial, pol_b, spin))
                    if a and b:
                        pairs.append(("polarization", a, b))
    return pairs


def normalized_hist(values: np.ndarray, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    counts, _ = np.histogram(values, bins=edges)
    total = counts.sum()
    prob = counts / total if total else np.zeros_like(counts, dtype=float)
    err = np.sqrt(counts) / total if total else np.zeros_like(counts, dtype=float)
    return prob.astype(float), err.astype(float)


def plot_1d(
    a: SampleData,
    b: SampleData,
    comparison_type: str,
    spec: ObservableSpec,
    output: Path,
    dpi: int,
) -> None:
    edges = np.linspace(spec.low, spec.high, spec.bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    pa, ea = normalized_hist(a.values[spec.name], edges)
    pb, eb = normalized_hist(b.values[spec.name], edges)
    ratio = np.divide(pa, pb, out=np.full_like(pa, np.nan), where=pb > 0.0)
    ratio_err = np.full_like(pa, np.nan)
    valid = (pa > 0.0) & (pb > 0.0)
    ratio_err[valid] = ratio[valid] * np.sqrt((ea[valid] / pa[valid]) ** 2 + (eb[valid] / pb[valid]) ** 2)

    fig = plt.figure(figsize=(8.0, 7.2))
    grid = fig.add_gridspec(2, 1, height_ratios=(3.2, 1.0), hspace=0.05)
    ax = fig.add_subplot(grid[0])
    ratio_ax = fig.add_subplot(grid[1], sharex=ax)

    ax.stairs(pa, edges, label=a.sample_id, linewidth=1.7)
    ax.stairs(pb, edges, label=b.sample_id, linewidth=1.7)
    ax.errorbar(centers, pa, yerr=ea, fmt="none", capsize=0, linewidth=0.8)
    ax.errorbar(centers, pb, yerr=eb, fmt="none", capsize=0, linewidth=0.8)
    ax.set_ylabel("Normalized events / bin")
    ax.set_title(f"{comparison_type}: {spec.name}")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    ax.tick_params(labelbottom=False)

    ratio_ax.axhline(1.0, linewidth=1.0)
    ratio_ax.errorbar(centers, ratio, yerr=ratio_err, fmt="o", markersize=2.5, linewidth=0.8)
    ratio_ax.set_ylim(0.5, 1.5)
    ratio_ax.set_ylabel("A / B")
    ratio_ax.set_xlabel(spec.label)
    ratio_ax.grid(alpha=0.25)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def normalized_hist2d(x: np.ndarray, y: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _, _ = np.histogram2d(x, y, bins=(edges, edges))
    total = counts.sum()
    return counts / total if total else counts


def plot_2d_sample(sample: SampleData, output: Path, dpi: int) -> None:
    edges = np.linspace(-1.0, 1.0, 25)
    hist = normalized_hist2d(
        sample.values["cos_theta_star_plus"],
        sample.values["cos_theta_star_minus"],
        edges,
    )
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    image = ax.pcolormesh(edges, edges, hist.T, shading="auto")
    fig.colorbar(image, ax=ax, label="Normalized events / bin")
    ax.set_xlabel(r"$\cos\theta^*_+$")
    ax.set_ylabel(r"$\cos\theta^*_-$")
    ax.set_title(sample.sample_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_2d_pair(a: SampleData, b: SampleData, comparison_type: str, output: Path, dpi: int) -> dict[str, float]:
    edges = np.linspace(-1.0, 1.0, 25)
    ha = normalized_hist2d(a.values["cos_theta_star_plus"], a.values["cos_theta_star_minus"], edges)
    hb = normalized_hist2d(b.values["cos_theta_star_plus"], b.values["cos_theta_star_minus"], edges)
    difference = ha - hb
    maximum = float(np.max(np.abs(difference))) if difference.size else 0.0

    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    image = ax.pcolormesh(edges, edges, difference.T, shading="auto", vmin=-maximum or None, vmax=maximum or None)
    fig.colorbar(image, ax=ax, label="Normalized A − B")
    ax.set_xlabel(r"$\cos\theta^*_+$")
    ax.set_ylabel(r"$\cos\theta^*_-$")
    ax.set_title(f"{comparison_type}\n{a.sample_id} − {b.sample_id}")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    flat_a = ha.ravel()
    flat_b = hb.ravel()
    variance = flat_a / max(len(a.values["cos_theta_star_plus"]), 1) + flat_b / max(len(b.values["cos_theta_star_plus"]), 1)
    mask = variance > 0.0
    chi2 = float(np.sum(((flat_a[mask] - flat_b[mask]) ** 2) / variance[mask]))
    ndf = max(int(np.count_nonzero(mask)) - 1, 0)
    return {
        "js_divergence": js_divergence(flat_a, flat_b),
        "l1_distance": float(np.sum(np.abs(flat_a - flat_b))),
        "chi2": chi2,
        "ndf": float(ndf),
        "chi2_ndf": chi2 / ndf if ndf else math.nan,
        "max_abs_bin_difference": maximum,
    }


def metric_row(
    comparison_type: str,
    a: SampleData,
    b: SampleData,
    observable: str,
    category: str,
    dimension: str,
    metrics: dict[str, float],
    plot_path: Path,
) -> dict[str, str]:
    pair_id = f"{comparison_type}__{a.sample_id}__vs__{b.sample_id}"
    row = {field: "" for field in METRIC_FIELDS}
    row.update({
        "comparison_type": comparison_type,
        "pair_id": pair_id,
        "sample_a": a.sample_id,
        "sample_b": b.sample_id,
        "initial_state_a": a.initial_state,
        "initial_state_b": b.initial_state,
        "polarization_a": a.polarization,
        "polarization_b": b.polarization,
        "spin_mode_a": a.spin_mode,
        "spin_mode_b": b.spin_mode,
        "observable": observable,
        "category": category,
        "dimension": dimension,
        "n_a": str(len(a.values["cos_theta_t"])),
        "n_b": str(len(b.values["cos_theta_t"])),
        "plot_path": str(plot_path),
    })
    for key, value in metrics.items():
        if key in row:
            row[key] = fmt(value)
    return row


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=METRIC_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], samples: dict[str, SampleData], pairs: list[tuple[str, SampleData, SampleData]]) -> None:
    lines = [
        "# WHIZARD spin-shape comparison summary",
        "",
        f"- Samples loaded: **{len(samples)}**",
        f"- Comparison pairs: **{len(pairs)}**",
        f"- Metric rows: **{len(rows)}**",
        "",
        "## Comparison pairs",
        "",
        "| Type | Sample A | Sample B |",
        "|---|---|---|",
    ]
    for comparison_type, a, b in pairs:
        lines.append(f"| {comparison_type} | `{a.sample_id}` | `{b.sample_id}` |")
    lines += [
        "",
        "## Key one-dimensional metrics",
        "",
        "| Type | Observable | Sample A | Sample B | KS p-value | JS divergence | χ²/ndf |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    key_names = {"cos_theta_t", "delta_phi_ll", "cos_opening_ll", "cos_theta_star_product"}
    for row in rows:
        if row["dimension"] != "1D" or row["observable"] not in key_names:
            continue
        lines.append(
            f"| {row['comparison_type']} | {row['observable']} | `{row['sample_a']}` | `{row['sample_b']}` | "
            f"{row['ks_pvalue'] or '—'} | {row['js_divergence'] or '—'} | {row['chi2_ndf'] or '—'} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- `sc_vs_iso`: production-level controls should agree, while charged-lepton and helicity-angle shapes should change.",
        "- `ee_vs_mumu`: all shapes should agree before ISR and machine-specific beam spectra are enabled.",
        "- `polarization`: LR100, RL100, and unpolarized samples may differ in both production and decay-lepton shapes.",
        "- All histograms are normalized to unit area; absolute-rate validation remains in the cross-section package.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    input_dir = (args.input_dir or root / "validation" / "angular_tables" / "observables").resolve()
    plots_dir = (args.plots_dir or root / "validation" / "plots").resolve()
    summary_csv = (args.summary_csv or root / "validation" / "angular_summaries" / "spin_shape_comparisons.csv").resolve()
    summary_md = (args.summary_md or root / "validation" / "angular_summaries" / "spin_shape_comparisons.md").resolve()

    valid_groups = {"sc_vs_iso", "ee_vs_mumu", "polarization"}
    groups = {item.strip() for item in args.comparison_groups.split(",") if item.strip()}
    unknown = groups - valid_groups
    if unknown:
        print(f"ERROR: unknown comparison group(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2

    files = sorted(input_dir.glob("*_spin_observables.csv"))
    files = [path for path in files if sample_selected(path.name.removesuffix("_spin_observables.csv"), args.sample)]
    if not files:
        print(f"ERROR: no observable tables found in {input_dir}", file=sys.stderr)
        return 2

    samples: dict[str, SampleData] = {}
    for path in files:
        sample = load_sample(path)
        samples[sample.sample_id] = sample
        print(f"Loaded {sample.sample_id}: {len(sample.values['cos_theta_t'])} finite events")

    pairs = pair_definitions(samples, groups)
    if not pairs:
        print("ERROR: no comparison pairs could be formed", file=sys.stderr)
        return 2

    if not args.no_plots:
        for sample in samples.values():
            output = plots_dir / "two_dimensional" / "samples" / f"{sample.sample_id}__cosstar2d.png"
            if args.overwrite or not output.exists():
                plot_2d_sample(sample, output, args.dpi)

    rows: list[dict[str, str]] = []
    for comparison_type, a, b in pairs:
        pair_slug = f"{comparison_type}__{a.sample_id}__vs__{b.sample_id}"
        print(f"Comparing {a.sample_id} vs {b.sample_id} ({comparison_type}) ...", flush=True)
        for spec in OBSERVABLES:
            edges = np.linspace(spec.low, spec.high, spec.bins + 1)
            metrics = shape_metrics(a.values[spec.name], b.values[spec.name], edges)
            plot_path = plots_dir / spec.category / comparison_type / f"{pair_slug}__{spec.name}.png"
            if not args.no_plots and (args.overwrite or not plot_path.exists()):
                plot_1d(a, b, comparison_type, spec, plot_path, args.dpi)
            rows.append(metric_row(comparison_type, a, b, spec.name, spec.category, "1D", metrics, plot_path))

        plot_2d = plots_dir / "two_dimensional" / comparison_type / f"{pair_slug}__cosstar2d_difference.png"
        if args.no_plots:
            edges = np.linspace(-1.0, 1.0, 25)
            ha = normalized_hist2d(a.values["cos_theta_star_plus"], a.values["cos_theta_star_minus"], edges)
            hb = normalized_hist2d(b.values["cos_theta_star_plus"], b.values["cos_theta_star_minus"], edges)
            two_metrics = {
                "js_divergence": js_divergence(ha.ravel(), hb.ravel()),
                "l1_distance": float(np.sum(np.abs(ha - hb))),
                "max_abs_bin_difference": float(np.max(np.abs(ha - hb))),
            }
        else:
            two_metrics = plot_2d_pair(a, b, comparison_type, plot_2d, args.dpi)
        rows.append(metric_row(
            comparison_type,
            a,
            b,
            "cos_theta_star_plus__vs__cos_theta_star_minus",
            "two_dimensional",
            "2D",
            two_metrics,
            plot_2d,
        ))

    write_csv(summary_csv, rows)
    write_markdown(summary_md, rows, samples, pairs)
    print(f"Wrote {summary_csv}")
    print(f"Wrote {summary_md}")
    print(f"Generated metrics for {len(pairs)} pair(s) and {len(rows)} comparison rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
