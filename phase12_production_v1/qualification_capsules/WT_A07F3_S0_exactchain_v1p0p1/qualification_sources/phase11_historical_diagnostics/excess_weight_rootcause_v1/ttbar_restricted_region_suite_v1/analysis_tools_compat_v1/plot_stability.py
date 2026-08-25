#!/usr/bin/env python3
"""
Create diagnostic stability plots from:

    analysis/node_numerical_metrics.tsv

This implementation intentionally supports older Matplotlib versions
available in system Python environments on CERN lxplus.

It does not modify any campaign data.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

# Always use a non-interactive backend on lxplus / batch nodes.
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def as_float(value: str, default: float = math.nan) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--campaign-dir",
        type=Path,
        required=True,
        help="Prepared campaign directory containing analysis/",
    )
    args = parser.parse_args()

    campaign = args.campaign_dir.resolve()

    metrics_path = campaign / "analysis" / "node_numerical_metrics.tsv"

    if not metrics_path.is_file():
        raise SystemExit(
            f"ERROR: missing numerical metrics:\n  {metrics_path}\n"
            "Run analyze_stability.py first."
        )

    with metrics_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    outdir = campaign / "analysis" / "plots"
    outdir.mkdir(parents=True, exist_ok=True)

    adaptive = [
        row
        for row in rows
        if row.get("stage") == "adaptive"
        and row.get("adaptive_id", "").startswith("A")
    ]

    adaptive_ids = sorted(
        set(row["adaptive_id"] for row in adaptive)
    )
    seed_ids = sorted(
        set(row["seed_id"] for row in adaptive)
    )

    if not adaptive_ids or not seed_ids:
        print("WARNING: no adaptive rows found; no adaptive plots produced")
        print(f"PLOT_DIR={outdir}")
        print("PLOT_STABILITY=PASS")
        return 0

    index = {
        (row["adaptive_id"], row["seed_id"]): row
        for row in adaptive
    }

    # ------------------------------------------------------------------
    # Plot 1:
    # maximum reported WHIZARD error after the first adaptive iteration
    # ------------------------------------------------------------------

    matrix = []

    for adaptive_id in adaptive_ids:
        row_values = []

        for seed_id in seed_ids:
            record = index.get((adaptive_id, seed_id))

            if record is None:
                row_values.append(math.nan)
            else:
                row_values.append(
                    as_float(
                        record.get(
                            "max_postfirst_reported_error_pct",
                            "nan",
                        )
                    )
                )

        matrix.append(row_values)

    fig, ax = plt.subplots(figsize=(9, 8))

    image = ax.imshow(
        matrix,
        aspect="auto",
        interpolation="nearest",
    )

    x_positions = list(range(len(seed_ids)))
    y_positions = list(range(len(adaptive_ids)))

    # Old-Matplotlib-compatible tick API.
    ax.set_xticks(x_positions)
    ax.set_xticklabels(seed_ids)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(adaptive_ids)

    ax.set_xlabel("integration seed")
    ax.set_ylabel("adaptive prescription")

    ax.set_title(
        "Maximum post-first WHIZARD reported error [%]"
    )

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("%")

    fig.tight_layout()

    fig.savefig(
        outdir / "adaptive_max_error_heatmap.png",
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    # ------------------------------------------------------------------
    # Plot 2:
    # final relative integration uncertainty per seed and prescription
    # ------------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 6))

    for seed_id in seed_ids:
        xs = []
        ys = []

        for i, adaptive_id in enumerate(adaptive_ids):
            record = index.get((adaptive_id, seed_id))

            if record is None:
                continue

            value = as_float(
                record.get("final_relative_error_pct", "nan")
            )

            if not math.isfinite(value):
                continue

            xs.append(i)
            ys.append(value)

        if xs:
            ax.plot(
                xs,
                ys,
                marker="o",
                label=seed_id,
            )

    x_positions = list(range(len(adaptive_ids)))

    ax.set_xticks(x_positions)
    ax.set_xticklabels(
        adaptive_ids,
        rotation=45,
        ha="right",
    )

    ax.set_ylabel("final relative error [%]")
    ax.set_xlabel("adaptive prescription")

    ax.set_title(
        "Adaptive-family final integration precision"
    )

    if seed_ids:
        ax.legend(ncol=4)

    fig.tight_layout()

    fig.savefig(
        outdir / "adaptive_final_relative_error.png",
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"PLOT_DIR={outdir}")
    print("PLOT_STABILITY=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
