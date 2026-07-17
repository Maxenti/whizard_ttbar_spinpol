#!/usr/bin/env python3
"""Plot and summarize the complete 15 ttbar spin-density observables.

The input tables are produced by scripts/qis/make_qis_ntuples.py after the
analysis-facing aliases b1k...cnr have been added by
qis_ttbar.physics.observables.event_observables.

Lower-case columns are bounded event-level angular analyzers.  The corresponding
spin-density coefficients are extracted from weighted means using the repository
convention antitop_analyzer_sign=-1:

  B1_i = 3 <b1i> / alpha_plus
  B2_i = 3 <b2i> / alpha_minus
  C_ij = 9 <cij> / (alpha_plus alpha_minus)

Examples
--------
python3 scripts/qis/plot_spin15_distributions.py \
  --dataset lhe_sc=/path/to/ntuples/lhe_sc \
  --dataset hepmc_sc=/path/to/ntuples/hepmc_sc \
  --output-dir /path/to/spin15
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qis_ttbar.physics.observables import (  # noqa: E402
    SPIN15_COEFFICIENT_NAMES,
    SPIN15_EVENT_COLUMNS,
)

POLARIZATION_COLUMNS = ("b1k", "b1r", "b1n", "b2k", "b2r", "b2n")
CORRELATION_COLUMNS = ("ckk", "crr", "cnn", "ckr", "crk", "ckn", "cnk", "crn", "cnr")

COEFFICIENT_BY_COLUMN = dict(zip(SPIN15_EVENT_COLUMNS, SPIN15_COEFFICIENT_NAMES, strict=True))
SAMPLE_RE = re.compile(
    r"^(?P<initial_state>ee|mumu)_ttbar_"
    r"(?P<decay_channel>epmum|mupem)_"
    r"(?P<polarization>LR100|RL100|unpol)_"
    r"(?P<spin_mode>sc|iso)_ISR_"
    r"(?P<sqrt_s>[0-9]+)GeV$"
)


@dataclass(frozen=True)
class DatasetSpec:
    label: str
    directory: Path


@dataclass(frozen=True)
class SampleTable:
    dataset: str
    sample_id: str
    path: Path
    frame: pd.DataFrame
    initial_state: str
    decay_channel: str
    polarization: str
    spin_mode: str
    sqrt_s_GeV: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        action="append",
        required=True,
        metavar="LABEL=DIR",
        help="Input ntuple directory. Repeat for LHE/HepMC and SC/ISO datasets.",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--bins", type=int, default=40)
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--formats", nargs="+", default=("png", "pdf"))
    parser.add_argument("--dpi", type=int, default=170)
    parser.add_argument("--no-individual", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def parse_dataset(value: str) -> DatasetSpec:
    if "=" not in value:
        raise ValueError(f"dataset must be LABEL=DIR, got {value!r}")
    label, directory = value.split("=", 1)
    label = label.strip()
    path = Path(directory).expanduser()
    if not label:
        raise ValueError("dataset label cannot be empty")
    if not path.is_dir():
        raise FileNotFoundError(path)
    return DatasetSpec(label=label, directory=path)


def discover_tables(spec: DatasetSpec) -> list[Path]:
    # Prefer parquet over CSV when both were written for the same sample.
    selected: dict[str, Path] = {}
    for extension in (".csv", ".parquet"):
        for path in sorted(spec.directory.glob(f"*{extension}")):
            if path.name.endswith(".summary.csv"):
                continue
            sample_id = path.stem
            if extension == ".parquet" or sample_id not in selected:
                selected[sample_id] = path
    if not selected:
        raise FileNotFoundError(f"no CSV or parquet ntuples under {spec.directory}")
    return [selected[key] for key in sorted(selected)]


def read_table(path: Path, max_events: int | None) -> pd.DataFrame:
    frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    if max_events is not None:
        frame = frame.head(max_events).copy()
    return frame


def parse_sample(path: Path, frame: pd.DataFrame, dataset: str) -> SampleTable:
    if "sample_id" in frame.columns and len(frame):
        ids = frame["sample_id"].dropna().astype(str).unique()
        if len(ids) != 1:
            raise ValueError(f"{path}: expected one sample_id, found {ids.tolist()}")
        sample_id = str(ids[0])
    else:
        sample_id = path.stem
    match = SAMPLE_RE.match(sample_id)
    if not match:
        raise ValueError(f"unsupported sample ID convention: {sample_id}")
    missing = [column for column in SPIN15_EVENT_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{path}: missing spin15 columns {missing}")
    return SampleTable(
        dataset=dataset,
        sample_id=sample_id,
        path=path,
        frame=frame,
        initial_state=match.group("initial_state"),
        decay_channel=match.group("decay_channel"),
        polarization=match.group("polarization"),
        spin_mode=match.group("spin_mode"),
        sqrt_s_GeV=int(match.group("sqrt_s")),
    )


def finite_values(frame: pd.DataFrame, column: str) -> tuple[np.ndarray, np.ndarray]:
    values = pd.to_numeric(frame[column], errors="coerce").to_numpy(float)
    if "event_weight" in frame.columns:
        weights = pd.to_numeric(frame["event_weight"], errors="coerce").to_numpy(float)
    else:
        weights = np.ones(len(frame), dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights)
    values = values[mask]
    weights = weights[mask]
    if len(values) == 0:
        raise ValueError(f"column {column} has no finite values")
    if float(np.sum(weights)) == 0.0:
        raise ValueError(f"column {column} has zero total weight")
    return values, weights


def weighted_stats(values: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    sum_w = float(np.sum(weights))
    sum_w2 = float(np.sum(np.square(weights)))
    mean = float(np.sum(weights * values) / sum_w)
    variance = float(np.sum(weights * np.square(values - mean)) / sum_w)
    neff = sum_w * sum_w / sum_w2 if sum_w2 > 0.0 else 0.0
    std = math.sqrt(max(variance, 0.0))
    mean_se = std / math.sqrt(neff) if neff > 0.0 else math.nan
    return {
        "events": float(len(values)),
        "weight_sum": sum_w,
        "effective_events": neff,
        "mean": mean,
        "std": std,
        "mean_se": mean_se,
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def coefficient_scale(column: str, frame: pd.DataFrame) -> float:
    alpha_plus = float(frame["alpha_plus"].iloc[0]) if "alpha_plus" in frame.columns and len(frame) else 1.0
    alpha_minus = float(frame["alpha_minus"].iloc[0]) if "alpha_minus" in frame.columns and len(frame) else 1.0
    if column.startswith("b1"):
        if alpha_plus == 0.0:
            raise ValueError("alpha_plus is zero")
        return 3.0 / alpha_plus
    if column.startswith("b2"):
        if alpha_minus == 0.0:
            raise ValueError("alpha_minus is zero")
        return 3.0 / alpha_minus
    if alpha_plus == 0.0 or alpha_minus == 0.0:
        raise ValueError("spin analyzing powers must be nonzero")
    return 9.0 / (alpha_plus * alpha_minus)


def normalized_histogram(values: np.ndarray, weights: np.ndarray, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    counts, _ = np.histogram(values, bins=edges, weights=weights)
    variance, _ = np.histogram(values, bins=edges, weights=np.square(weights))
    total = float(np.sum(counts))
    if total == 0.0:
        return np.zeros_like(counts), np.zeros_like(counts)
    return counts / total, np.sqrt(variance) / abs(total)


def save_figure(fig, base: Path, formats: Iterable[str], dpi: int) -> list[str]:
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in formats:
        path = base.with_suffix(f".{extension}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def draw_histogram(ax, values: np.ndarray, weights: np.ndarray, bins: int, label: str | None = None) -> None:
    edges = np.linspace(-1.0, 1.0, bins + 1)
    probabilities, errors = normalized_histogram(values, weights, edges)
    centers = 0.5 * (edges[:-1] + edges[1:])
    ax.stairs(probabilities, edges, linewidth=1.5, label=label)
    ax.errorbar(centers, probabilities, yerr=errors, fmt="none", linewidth=0.7)
    ax.set_xlim(-1.0, 1.0)
    ax.grid(alpha=0.25)


def make_panel(sample: SampleTable, columns: tuple[str, ...], *, title: str, output_base: Path, bins: int, formats: Iterable[str], dpi: int) -> list[str]:
    rows = 2 if len(columns) == 6 else 3
    cols = 3
    fig, axes = plt.subplots(rows, cols, figsize=(12.0, 7.3 if rows == 2 else 10.0), squeeze=False)
    for ax, column in zip(axes.flat, columns, strict=True):
        values, weights = finite_values(sample.frame, column)
        draw_histogram(ax, values, weights, bins)
        coefficient = COEFFICIENT_BY_COLUMN[column]
        scale = coefficient_scale(column, sample.frame)
        stats = weighted_stats(values, weights)
        ax.set_title(f"{column}  ({coefficient}={scale * stats['mean']:+.3f})")
        ax.set_xlabel(column)
        ax.set_ylabel("Normalized events / bin")
    fig.suptitle(f"{title}\n{sample.dataset}: {sample.sample_id}", y=1.01)
    fig.tight_layout()
    return save_figure(fig, output_base, formats, dpi)


def make_individual(sample: SampleTable, column: str, *, output_base: Path, bins: int, formats: Iterable[str], dpi: int) -> list[str]:
    values, weights = finite_values(sample.frame, column)
    stats = weighted_stats(values, weights)
    scale = coefficient_scale(column, sample.frame)
    coefficient = COEFFICIENT_BY_COLUMN[column]
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    draw_histogram(ax, values, weights, bins)
    ax.set_xlabel(column)
    ax.set_ylabel("Normalized events / bin")
    ax.set_title(
        f"{sample.dataset}: {sample.sample_id}\n"
        f"{coefficient} = {scale * stats['mean']:+.4f} ± {scale * stats['mean_se']:.4f}"
    )
    fig.tight_layout()
    return save_figure(fig, output_base, formats, dpi)


def main() -> int:
    args = parse_args()
    if args.bins < 5:
        raise ValueError("--bins must be at least 5")
    specs = [parse_dataset(value) for value in args.dataset]
    labels = [spec.label for spec in specs]
    if len(labels) != len(set(labels)):
        raise ValueError("dataset labels must be unique")

    samples: list[SampleTable] = []
    for spec in specs:
        for path in discover_tables(spec):
            samples.append(parse_sample(path, read_table(path, args.max_events), spec.label))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, object]] = []
    figure_manifest: list[dict[str, str]] = []
    failures: list[str] = []

    for sample in samples:
        sample_root = args.output_dir / "per_sample" / sample.dataset / sample.sample_id
        try:
            outputs = make_panel(
                sample,
                POLARIZATION_COLUMNS,
                title="Top and antitop polarization analyzers",
                output_base=sample_root / "spin15_polarization_panel",
                bins=args.bins,
                formats=args.formats,
                dpi=args.dpi,
            )
            figure_manifest.extend(
                {"dataset": sample.dataset, "sample_id": sample.sample_id, "kind": "polarization_panel", "path": path}
                for path in outputs
            )
            outputs = make_panel(
                sample,
                CORRELATION_COLUMNS,
                title="Top-antitop spin-correlation analyzers",
                output_base=sample_root / "spin15_correlation_panel",
                bins=args.bins,
                formats=args.formats,
                dpi=args.dpi,
            )
            figure_manifest.extend(
                {"dataset": sample.dataset, "sample_id": sample.sample_id, "kind": "correlation_panel", "path": path}
                for path in outputs
            )

            for column in SPIN15_EVENT_COLUMNS:
                values, weights = finite_values(sample.frame, column)
                stats = weighted_stats(values, weights)
                scale = coefficient_scale(column, sample.frame)
                row = {
                    "dataset": sample.dataset,
                    "sample_id": sample.sample_id,
                    "initial_state": sample.initial_state,
                    "decay_channel": sample.decay_channel,
                    "polarization": sample.polarization,
                    "spin_mode": sample.spin_mode,
                    "sqrt_s_GeV": sample.sqrt_s_GeV,
                    "observable": column,
                    "coefficient_name": COEFFICIENT_BY_COLUMN[column],
                    **stats,
                    "coefficient": scale * stats["mean"],
                    "coefficient_se": abs(scale) * stats["mean_se"],
                    "in_unit_interval": stats["min"] >= -1.0 - 1.0e-10 and stats["max"] <= 1.0 + 1.0e-10,
                    "source_table": str(sample.path),
                }
                summary_rows.append(row)
                if not row["in_unit_interval"]:
                    failures.append(
                        f"{sample.dataset}/{sample.sample_id}/{column}: range "
                        f"[{stats['min']}, {stats['max']}]"
                    )
                if not args.no_individual:
                    outputs = make_individual(
                        sample,
                        column,
                        output_base=sample_root / "individual" / column,
                        bins=args.bins,
                        formats=args.formats,
                        dpi=args.dpi,
                    )
                    figure_manifest.extend(
                        {"dataset": sample.dataset, "sample_id": sample.sample_id, "kind": column, "path": path}
                        for path in outputs
                    )
        except Exception as exc:
            failures.append(f"{sample.dataset}/{sample.sample_id}: {exc}")
            if args.strict:
                raise

    summary_path = args.output_dir / "spin15_coefficients.csv"
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
    manifest_path = args.output_dir / "spin15_figure_manifest.csv"
    with manifest_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["dataset", "sample_id", "kind", "path"])
        writer.writeheader()
        writer.writerows(figure_manifest)

    metadata = {
        "schema_version": 1,
        "datasets": [{"label": spec.label, "directory": str(spec.directory)} for spec in specs],
        "samples": len(samples),
        "observables": list(SPIN15_EVENT_COLUMNS),
        "coefficients": list(SPIN15_COEFFICIENT_NAMES),
        "coefficient_convention": {
            "B1_i": "3 * weighted_mean(b1i) / alpha_plus",
            "B2_i": "3 * weighted_mean(b2i) / alpha_minus",
            "C_ij": "9 * weighted_mean(cij) / (alpha_plus * alpha_minus)",
            "antitop_analyzer_sign": -1.0,
        },
        "summary_csv": str(summary_path),
        "figure_manifest_csv": str(manifest_path),
        "failures": failures,
    }
    (args.output_dir / "spin15_manifest.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )

    print(f"Samples: {len(samples)}")
    print(f"Coefficient rows: {len(summary_rows)}")
    print(f"Figures: {len(figure_manifest)}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {manifest_path}")
    if failures:
        print("FAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        return 1 if args.strict else 0
    print("SPIN15 DISTRIBUTION PACKAGE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
