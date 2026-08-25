#!/usr/bin/env python3
"""
Plot:

  1. unrestricted full-ME region components
  2. region-sum vs monolithic closure pulls

Compatible with older Matplotlib versions commonly provided by
system Python installations on CERN lxplus.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--campaign-dir",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    campaign = args.campaign_dir.resolve()

    outdir = campaign / "analysis" / "plots"
    outdir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Region components
    # ------------------------------------------------------------------

    region_sums = campaign / "analysis" / "region_sums.tsv"

    if region_sums.is_file():
        with region_sums.open(newline="") as handle:
            rows = list(
                csv.DictReader(
                    handle,
                    delimiter="\t",
                )
            )

        keys = sorted(
            set(
                (
                    row["window_id"],
                    row["recipe_id"],
                )
                for row in rows
            )
        )

        for window_id, recipe_id in keys:
            selected = sorted(
                [
                    row
                    for row in rows
                    if row["window_id"] == window_id
                    and row["recipe_id"] == recipe_id
                ],
                key=lambda row: row["seed_id"],
            )

            seeds = [
                row["seed_id"]
                for row in selected
            ]

            fig, ax = plt.subplots(
                figsize=(9, 5)
            )

            bottom = [0.0] * len(selected)

            components = [
                ("DR_fb", "DR"),
                ("SR_PLUS_fb", "SR+"),
                ("SR_MINUS_fb", "SR-"),
                ("NR_fb", "NR"),
            ]

            for column, label in components:
                values = [
                    float(row[column])
                    for row in selected
                ]

                ax.bar(
                    seeds,
                    values,
                    bottom=bottom,
                    label=label,
                )

                bottom = [
                    old + new
                    for old, new in zip(
                        bottom,
                        values,
                    )
                ]

            ax.set_ylabel("cross section [fb]")

            ax.set_title(
                f"{window_id} {recipe_id}: "
                "unrestricted full-ME kinematic partition"
            )

            ax.legend()

            fig.tight_layout()

            fig.savefig(
                outdir
                / f"region_components_{window_id}_{recipe_id}.png",
                dpi=180,
                bbox_inches="tight",
            )

            plt.close(fig)

    # ------------------------------------------------------------------
    # Region vs monolithic closure
    # ------------------------------------------------------------------

    closure = (
        campaign
        / "analysis"
        / "region_vs_monolithic.tsv"
    )

    if closure.is_file():
        with closure.open(newline="") as handle:
            rows = list(
                csv.DictReader(
                    handle,
                    delimiter="\t",
                )
            )

        if rows:
            labels = [
                f"{row['recipe_id']}:{row['seed_id']}"
                for row in rows
            ]

            values = [
                float(row["pull"])
                for row in rows
            ]

            fig, ax = plt.subplots(
                figsize=(
                    max(
                        10,
                        len(rows) * 0.35,
                    ),
                    5,
                )
            )

            x_positions = list(
                range(len(values))
            )

            ax.axhline(
                0,
                linewidth=1,
            )

            ax.plot(
                x_positions,
                values,
                marker="o",
                linestyle="none",
            )

            # Old-Matplotlib-compatible API.
            ax.set_xticks(x_positions)
            ax.set_xticklabels(
                labels,
                rotation=90,
            )

            ax.set_ylabel(
                "(region sum - monolithic) / combined error"
            )

            ax.set_title(
                "Nine-cell closure pulls"
            )

            fig.tight_layout()

            fig.savefig(
                outdir
                / "region_monolithic_closure_pulls.png",
                dpi=180,
                bbox_inches="tight",
            )

            plt.close(fig)

    print(f"PLOT_DIR={outdir}")
    print("PLOT_REGIONS=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
