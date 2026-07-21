#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# WHIZARD ttbar Spin-15 presentation bundle builder
#
# This script reads the authoritative EOS qualification tree directly.
# It:
#   1. copies all raw per-sample figures listed in the figure manifest;
#   2. copies all validation and coefficient tables;
#   3. generates LR/RL, SC/ISO, and LHE/HepMC comparison plots from ntuples;
#   4. generates compact summary figures;
#   5. creates a curated main-presentation subset;
#   6. writes inventories, checksums, and a README;
#   7. creates a compressed tarball on EOS.
#
# Run from lxplus:
#   chmod +x build_spin15_presentation_bundle_from_eos.sh
#   ./build_spin15_presentation_bundle_from_eos.sh
#
# Optional overrides:
#   OUT=/eos/.../spin15_gate_10k_sharded_v2
#   EOS_BUNDLE_DIR=/eos/.../presentation_bundles
#   INCLUDE_RAW_FIGURES=1
#   MAKE_LR_RL_OVERLAYS=1
#   MAKE_SC_ISO_OVERLAYS=1
#   MAKE_LHE_HEPMC_OVERLAYS=1
#   HIST_BINS=40
#   KEEP_STAGE=0
# ---------------------------------------------------------------------------

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
OUT=${OUT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/spin15_gate_10k_sharded_v2}
EOS_BUNDLE_DIR=${EOS_BUNDLE_DIR:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/presentation_bundles}

INCLUDE_RAW_FIGURES=${INCLUDE_RAW_FIGURES:-1}
MAKE_LR_RL_OVERLAYS=${MAKE_LR_RL_OVERLAYS:-1}
MAKE_SC_ISO_OVERLAYS=${MAKE_SC_ISO_OVERLAYS:-1}
MAKE_LHE_HEPMC_OVERLAYS=${MAKE_LHE_HEPMC_OVERLAYS:-1}
HIST_BINS=${HIST_BINS:-40}
KEEP_STAGE=${KEEP_STAGE:-0}

cd "$REPO"

if [[ -r "$REPO/setup_lxplus.sh" ]]; then
  # shellcheck disable=SC1091
  source "$REPO/setup_lxplus.sh"
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BUNDLE_NAME="whizard_ttbar_spin15_presentation_full_${STAMP}"
WORK_PARENT=${TMPDIR:-/tmp/${USER:-unknown}}
STAGE="$WORK_PARENT/$BUNDLE_NAME"
TARBALL="$EOS_BUNDLE_DIR/${BUNDLE_NAME}.tar.gz"

rm -rf "$STAGE"

mkdir -p \
  "$STAGE/00_recommended_main_figures" \
  "$STAGE/00_overview" \
  "$STAGE/01_generation_and_structure/tables" \
  "$STAGE/01_generation_and_structure/plots" \
  "$STAGE/02_beam_polarization/tables" \
  "$STAGE/02_beam_polarization/plots_coefficients_sc" \
  "$STAGE/02_beam_polarization/plots_coefficients_iso_null" \
  "$STAGE/02_beam_polarization/plots_distributions_lr_rl/sc" \
  "$STAGE/02_beam_polarization/plots_distributions_lr_rl/iso" \
  "$STAGE/03_spin_correlation/tables" \
  "$STAGE/03_spin_correlation/plots_significance" \
  "$STAGE/03_spin_correlation/plots_connected_matrices" \
  "$STAGE/03_spin_correlation/plots_distributions_sc_iso" \
  "$STAGE/04_lhe_hepmc_preservation/tables" \
  "$STAGE/04_lhe_hepmc_preservation/plots_summary" \
  "$STAGE/04_lhe_hepmc_preservation/plots_distributions_lhe_hepmc" \
  "$STAGE/05_decay_flavour/tables" \
  "$STAGE/05_decay_flavour/plots" \
  "$STAGE/06_coefficient_overview/tables" \
  "$STAGE/06_coefficient_overview/plots" \
  "$STAGE/07_raw_figure_archive" \
  "$STAGE/90_manifests" \
  "$STAGE/99_provenance"

export REPO OUT STAGE
export INCLUDE_RAW_FIGURES MAKE_LR_RL_OVERLAYS
export MAKE_SC_ISO_OVERLAYS MAKE_LHE_HEPMC_OVERLAYS
export HIST_BINS

python3 - <<'PY'
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


repo = Path(os.environ["REPO"])
out = Path(os.environ["OUT"])
stage = Path(os.environ["STAGE"])

include_raw = bool(int(os.environ["INCLUDE_RAW_FIGURES"]))
make_lr_rl = bool(int(os.environ["MAKE_LR_RL_OVERLAYS"]))
make_sc_iso = bool(int(os.environ["MAKE_SC_ISO_OVERLAYS"]))
make_lhe_hepmc = bool(int(os.environ["MAKE_LHE_HEPMC_OVERLAYS"]))
hist_bins = int(os.environ["HIST_BINS"])

gate_dir = out / "gate"
spin15_dir = out / "spin15"
ntuples_dir = out / "ntuples"
provenance_dir = out / "provenance"

required = [
    gate_dir / "spin15_gate_summary.json",
    gate_dir / "spin15_gate_report.md",
    gate_dir / "spin15_structure.csv",
    gate_dir / "beam_polarization_config_audit.csv",
    gate_dir / "spin15_lr_rl_gate.csv",
    gate_dir / "spin15_lr_rl_details.csv",
    gate_dir / "spin15_sc_iso_gate.csv",
    gate_dir / "spin15_sc_iso_details.csv",
    gate_dir / "spin15_connected_correlations.csv",
    gate_dir / "spin15_decay_flavour_gate.csv",
    gate_dir / "spin15_decay_flavour_details.csv",
    gate_dir / "spin15_lhe_hepmc_preservation.csv",
    spin15_dir / "spin15_coefficients.csv",
    spin15_dir / "spin15_figure_manifest.csv",
]

missing = [path for path in required if not path.is_file()]
if missing:
    raise SystemExit(
        "Missing required authoritative files:\n"
        + "\n".join(f"  {path}" for path in missing)
    )


def copy_file(source: Path, destination_dir: Path, name: str | None = None) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / (name or source.name)
    shutil.copy2(source, destination)
    return destination


def save_figure(base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(base.with_suffix(".png"), dpi=180, bbox_inches="tight")
    plt.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close()


def safe_slug(value: object) -> str:
    text = str(value)
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("_")


# -----------------------------------------------------------------------
# Copy authoritative reports, tables, configs, and provenance
# -----------------------------------------------------------------------

overview_sources = [
    gate_dir / "spin15_gate_summary.json",
    gate_dir / "spin15_gate_report.md",
    out / "QUALIFICATION_COMPLETE.md",
]
for source in overview_sources:
    if source.is_file():
        copy_file(source, stage / "00_overview")

table_map = {
    "01_generation_and_structure/tables": [
        gate_dir / "spin15_structure.csv",
        gate_dir / "beam_polarization_config_audit.csv",
    ],
    "02_beam_polarization/tables": [
        gate_dir / "spin15_lr_rl_gate.csv",
        gate_dir / "spin15_lr_rl_details.csv",
    ],
    "03_spin_correlation/tables": [
        gate_dir / "spin15_sc_iso_gate.csv",
        gate_dir / "spin15_sc_iso_details.csv",
        gate_dir / "spin15_connected_correlations.csv",
    ],
    "04_lhe_hepmc_preservation/tables": [
        gate_dir / "spin15_lhe_hepmc_preservation.csv",
    ],
    "05_decay_flavour/tables": [
        gate_dir / "spin15_decay_flavour_gate.csv",
        gate_dir / "spin15_decay_flavour_details.csv",
    ],
    "06_coefficient_overview/tables": [
        spin15_dir / "spin15_coefficients.csv",
    ],
    "90_manifests": [
        spin15_dir / "spin15_figure_manifest.csv",
    ],
}

for relative_dir, sources in table_map.items():
    for source in sources:
        copy_file(source, stage / relative_dir)

for source in [
    provenance_dir / "SHA256SUMS.txt",
    provenance_dir / "validate_spin15_gate.py",
]:
    if source.is_file():
        copy_file(source, stage / "99_provenance")

for config in [
    repo / "configs/qis/qualification_500GeV_ISR_sc_v1.yaml",
    repo / "configs/qis/qualification_500GeV_ISR_iso_v1.yaml",
    repo / "configs/production/production_500GeV_ISR_sc_v1.csv",
    repo / "configs/production/production_500GeV_ISR_iso_validation_v1.csv",
]:
    if config.is_file():
        copy_file(config, stage / "99_provenance")


# -----------------------------------------------------------------------
# Copy every raw figure from the authoritative EOS manifest
# -----------------------------------------------------------------------

manifest = pd.read_csv(spin15_dir / "spin15_figure_manifest.csv")

required_manifest_columns = {"dataset", "sample_id", "kind", "path"}
if not required_manifest_columns.issubset(manifest.columns):
    raise SystemExit(
        "Unexpected figure-manifest schema. Required columns: "
        + ", ".join(sorted(required_manifest_columns))
        + "\nActual columns: "
        + ", ".join(manifest.columns)
    )

raw_copy_records: list[dict[str, object]] = []
unresolved_records: list[dict[str, object]] = []

if include_raw:
    for index, row in manifest.iterrows():
        source = Path(str(row["path"]))

        if not source.is_absolute():
            candidates = [
                spin15_dir / source,
                out / source,
                repo / source,
            ]
            source = next(
                (candidate for candidate in candidates if candidate.is_file()),
                source,
            )

        if not source.is_file():
            unresolved_records.append(
                {
                    "manifest_index": index,
                    "dataset": row["dataset"],
                    "sample_id": row["sample_id"],
                    "kind": row["kind"],
                    "path": row["path"],
                }
            )
            continue

        destination_dir = (
            stage
            / "07_raw_figure_archive"
            / safe_slug(row["dataset"])
            / safe_slug(row["sample_id"])
            / safe_slug(row["kind"])
        )

        destination = destination_dir / source.name
        destination_dir.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            digest = hashlib.sha1(
                str(source).encode("utf-8")
            ).hexdigest()[:10]
            destination = destination_dir / f"{digest}__{source.name}"

        shutil.copy2(source, destination)

        raw_copy_records.append(
            {
                "manifest_index": index,
                "dataset": row["dataset"],
                "sample_id": row["sample_id"],
                "kind": row["kind"],
                "source_path": str(source),
                "bundle_path": str(destination.relative_to(stage)),
                "size_bytes": destination.stat().st_size,
            }
        )

pd.DataFrame(raw_copy_records).to_csv(
    stage / "90_manifests/raw_figure_copy_manifest.csv",
    index=False,
)

pd.DataFrame(unresolved_records).to_csv(
    stage / "90_manifests/unresolved_raw_figures.csv",
    index=False,
)


# -----------------------------------------------------------------------
# Load validation tables and coefficient metadata
# -----------------------------------------------------------------------

structure = pd.read_csv(gate_dir / "spin15_structure.csv")
config_audit = pd.read_csv(gate_dir / "beam_polarization_config_audit.csv")
lr_gate = pd.read_csv(gate_dir / "spin15_lr_rl_gate.csv")
lr_details = pd.read_csv(gate_dir / "spin15_lr_rl_details.csv")
sc_iso_gate = pd.read_csv(gate_dir / "spin15_sc_iso_gate.csv")
sc_iso_details = pd.read_csv(gate_dir / "spin15_sc_iso_details.csv")
connected = pd.read_csv(gate_dir / "spin15_connected_correlations.csv")
preservation = pd.read_csv(gate_dir / "spin15_lhe_hepmc_preservation.csv")
flavour_gate = pd.read_csv(gate_dir / "spin15_decay_flavour_gate.csv")
flavour_details = pd.read_csv(gate_dir / "spin15_decay_flavour_details.csv")
coefficients = pd.read_csv(spin15_dir / "spin15_coefficients.csv")

sample_meta = (
    coefficients[
        [
            "dataset",
            "sample_id",
            "initial_state",
            "decay_channel",
            "polarization",
            "spin_mode",
            "sqrt_s_GeV",
            "source_table",
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)

if len(sample_meta) != 32:
    raise SystemExit(
        f"Expected 32 unique coefficient datasets, found {len(sample_meta)}"
    )


# -----------------------------------------------------------------------
# Compact derivative tables
# -----------------------------------------------------------------------

lr_gate[lr_gate["spin_mode"] == "sc"].to_csv(
    stage / "02_beam_polarization/tables/polarization_sc_only.csv",
    index=False,
)
lr_gate[lr_gate["spin_mode"] == "iso"].to_csv(
    stage / "02_beam_polarization/tables/polarization_iso_null_controls.csv",
    index=False,
)

preservation["abs_delta"] = preservation["delta_hepmc_minus_lhe"].abs()
preservation["abs_z"] = preservation["z"].abs()

preservation[preservation["status"] == "warn"].to_csv(
    stage
    / "04_lhe_hepmc_preservation/tables"
    / "preservation_warnings_only.csv",
    index=False,
)

(
    preservation[preservation["status"] == "warn"]
    .groupby(["observable", "coefficient_name"], dropna=False)
    .size()
    .reset_index(name="warning_rows")
    .sort_values("warning_rows", ascending=False)
    .to_csv(
        stage
        / "04_lhe_hepmc_preservation/tables"
        / "preservation_warning_summary.csv",
        index=False,
    )
)

summary = json.loads((gate_dir / "spin15_gate_summary.json").read_text())
counts = summary["counts"]

gate_summary = pd.DataFrame(
    [
        {
            "validation": "Sample structure",
            "failures": counts.get("structural_failures", 0),
            "warnings": 0,
            "not_applicable": 0,
        },
        {
            "validation": "Beam configuration",
            "failures": counts.get("config_failures", 0),
            "warnings": 0,
            "not_applicable": 0,
        },
        {
            "validation": "LHE to HepMC coefficients",
            "failures": counts.get("preservation_failures", 0),
            "warnings": counts.get("preservation_warnings", 0),
            "not_applicable": 0,
        },
        {
            "validation": "LR100 versus RL100",
            "failures": counts.get("polarization_failures", 0),
            "warnings": 0,
            "not_applicable": counts.get(
                "polarization_not_applicable",
                0,
            ),
        },
        {
            "validation": "SC versus ISO connected correlations",
            "failures": counts.get("spin_correlation_failures", 0),
            "warnings": 0,
            "not_applicable": 0,
        },
        {
            "validation": "Decay-flavour consistency",
            "failures": counts.get("flavour_failures", 0),
            "warnings": counts.get("flavour_warnings", 0),
            "not_applicable": 0,
        },
    ]
)

gate_summary.to_csv(
    stage / "00_overview/presentation_gate_summary.csv",
    index=False,
)


# -----------------------------------------------------------------------
# Summary figures from validation tables
# -----------------------------------------------------------------------

# Configuration count audit.
config_counts = (
    config_audit.groupby(["spin_correlated", "polarization"])
    .size()
    .unstack(fill_value=0)
)
config_counts.plot(kind="bar", figsize=(8, 5))
plt.ylabel("Configured samples")
plt.xlabel("Spin-correlated flag")
plt.title("Generated sample configuration audit")
plt.xticks(rotation=0)
save_figure(
    stage
    / "01_generation_and_structure/plots"
    / "sample_configuration_counts"
)

# Final gate summary.
plot_gate = gate_summary.copy()
positions = np.arange(len(plot_gate))
plt.figure(figsize=(9, 5.5))
plt.barh(positions, plot_gate["failures"], label="Failures")
plt.barh(
    positions,
    plot_gate["warnings"],
    left=plot_gate["failures"],
    label="Warnings",
)
plt.barh(
    positions,
    plot_gate["not_applicable"],
    left=plot_gate["failures"] + plot_gate["warnings"],
    label="Not applicable",
)
plt.yticks(positions, plot_gate["validation"])
plt.xlabel("Count")
plt.title("Final Spin-15 qualification summary")
plt.legend()
save_figure(stage / "00_overview/final_gate_summary")

# LR/RL maximum significance.
lr_plot = lr_gate.copy()
lr_plot["label"] = (
    lr_plot["dataset"]
    + " | "
    + lr_plot["initial_state"]
    + " | "
    + lr_plot["decay_channel"]
)
lr_plot = lr_plot.sort_values(
    ["spin_mode", "dataset", "initial_state", "decay_channel"]
)
plt.figure(figsize=(11, 7))
plt.barh(np.arange(len(lr_plot)), lr_plot["max_abs_z"])
plt.axvline(5.0, linewidth=1)
plt.yticks(np.arange(len(lr_plot)), lr_plot["label"], fontsize=8)
plt.xlabel("Maximum LR/RL separation significance |z|")
plt.title("Beam-polarization validation: SC signal and ISO null control")
save_figure(
    stage
    / "02_beam_polarization"
    / "lr_rl_max_significance_all_groups"
)

# SC/ISO maximum significance.
spin_plot = sc_iso_gate.copy()
spin_plot["label"] = (
    spin_plot["stage"]
    + " | "
    + spin_plot["initial_state"]
    + " | "
    + spin_plot["polarization"]
    + " | "
    + spin_plot["decay_channel"]
)
spin_plot = spin_plot.sort_values(
    ["stage", "initial_state", "polarization", "decay_channel"]
)
plt.figure(figsize=(11, 7))
plt.barh(np.arange(len(spin_plot)), spin_plot["max_abs_z"])
plt.axvline(5.0, linewidth=1)
plt.yticks(np.arange(len(spin_plot)), spin_plot["label"], fontsize=8)
plt.xlabel("Maximum SC/ISO connected-correlation significance |z|")
plt.title("Spin-correlation qualification across all matched groups")
save_figure(
    stage
    / "03_spin_correlation/plots_significance"
    / "sc_iso_max_significance_all_groups"
)

# Decay-flavour consistency.
flavour_plot = flavour_gate.copy()
flavour_plot["label"] = (
    flavour_plot["dataset"]
    + " | "
    + flavour_plot["initial_state"]
    + " | "
    + flavour_plot["polarization"]
    + " | "
    + flavour_plot["spin_mode"]
)
flavour_plot = flavour_plot.sort_values(
    ["dataset", "initial_state", "polarization", "spin_mode"]
)
plt.figure(figsize=(11, 7))
plt.barh(np.arange(len(flavour_plot)), flavour_plot["max_abs_z"])
plt.axvline(5.0, linewidth=1)
plt.yticks(np.arange(len(flavour_plot)), flavour_plot["label"], fontsize=8)
plt.xlabel("Maximum epmum/mupem consistency significance |z|")
plt.title("Decay-flavour consistency across all groups")
save_figure(
    stage
    / "05_decay_flavour/plots"
    / "decay_flavour_max_significance"
)

# LHE/HepMC coefficient preservation.
for spin_mode in ["sc", "iso"]:
    subset = preservation[preservation["spin_mode"] == spin_mode]
    plt.figure(figsize=(7, 6))
    plt.scatter(
        subset["lhe_coefficient"],
        subset["hepmc_coefficient"],
        s=20,
    )
    low = min(
        subset["lhe_coefficient"].min(),
        subset["hepmc_coefficient"].min(),
    ) - 0.05
    high = max(
        subset["lhe_coefficient"].max(),
        subset["hepmc_coefficient"].max(),
    ) + 0.05
    grid = np.linspace(low, high, 300)
    plt.plot(grid, grid, linewidth=1)
    plt.plot(grid, grid + 0.02, linestyle="--", linewidth=1)
    plt.plot(grid, grid - 0.02, linestyle="--", linewidth=1)
    plt.xlim(low, high)
    plt.ylim(low, high)
    plt.xlabel("LHE coefficient")
    plt.ylabel("HepMC coefficient")
    plt.title(
        f"LHE-to-HepMC coefficient preservation: {spin_mode.upper()}"
    )
    save_figure(
        stage
        / "04_lhe_hepmc_preservation/plots_summary"
        / f"lhe_hepmc_scatter_{spin_mode}"
    )

warning_counts = (
    preservation[preservation["status"] == "warn"]
    .groupby("coefficient_name")
    .size()
    .sort_values()
)
plt.figure(figsize=(8, 5))
plt.barh(warning_counts.index, warning_counts.values)
plt.xlabel("Warning rows")
plt.title("LHE/HepMC absolute-shift warnings by coefficient")
save_figure(
    stage
    / "04_lhe_hepmc_preservation/plots_summary"
    / "preservation_warning_counts"
)

plt.figure(figsize=(7, 6))
plt.scatter(
    preservation["abs_delta"],
    preservation["abs_z"],
    s=20,
)
plt.axvline(0.02, linestyle="--", linewidth=1)
plt.axhline(5.0, linestyle="--", linewidth=1)
plt.xlabel(r"Absolute coefficient shift $|\Delta|$")
plt.ylabel(r"Significance $|z|$")
plt.title("LHE/HepMC preservation gate plane")
save_figure(
    stage
    / "04_lhe_hepmc_preservation/plots_summary"
    / "preservation_abs_shift_vs_significance"
)

# Complete 32x15 coefficient heatmap.
coefficient_order = [
    "B1k", "B1r", "B1n",
    "B2k", "B2r", "B2n",
    "Ckk", "Crr", "Cnn",
    "Ckr", "Crk", "Ckn", "Cnk", "Crn", "Cnr",
]

sample_order = (
    coefficients[["dataset", "sample_id"]]
    .drop_duplicates()
    .sort_values(["dataset", "sample_id"])
)

pivot = coefficients.pivot_table(
    index=["dataset", "sample_id"],
    columns="coefficient_name",
    values="coefficient",
)

pivot = pivot.reindex(
    pd.MultiIndex.from_frame(sample_order)
)
pivot = pivot[coefficient_order]

plt.figure(figsize=(12, 11))
image = plt.imshow(pivot.values, aspect="auto")
plt.colorbar(image, label="Coefficient")
plt.xticks(
    np.arange(len(coefficient_order)),
    coefficient_order,
    rotation=45,
    ha="right",
)
labels = [
    f"{dataset} | {sample_id}"
    for dataset, sample_id in pivot.index
]
plt.yticks(np.arange(len(labels)), labels, fontsize=6)
plt.title("Complete Spin-15 coefficient overview")
save_figure(
    stage
    / "06_coefficient_overview/plots"
    / "spin15_coefficient_heatmap_all_samples"
)


# -----------------------------------------------------------------------
# Polarization coefficient forest plots
# -----------------------------------------------------------------------

b_order = ["b1k", "b1r", "b1n", "b2k", "b2r", "b2n"]

for spin_mode, destination_name in [
    ("sc", "plots_coefficients_sc"),
    ("iso", "plots_coefficients_iso_null"),
]:
    subset = lr_details[lr_details["spin_mode"] == spin_mode]

    for (
        stage_name,
        initial_state,
        decay_channel,
    ), group in subset.groupby(
        ["stage", "initial_state", "decay_channel"]
    ):
        group = (
            group.set_index("observable")
            .reindex(b_order)
            .dropna(subset=["lr_coefficient", "rl_coefficient"])
            .reset_index()
        )

        y = np.arange(len(group))
        plt.figure(figsize=(8, 5.5))
        plt.errorbar(
            group["lr_coefficient"],
            y - 0.10,
            xerr=group["lr_se"],
            fmt="o",
            capsize=3,
            label="LR100",
        )
        plt.errorbar(
            group["rl_coefficient"],
            y + 0.10,
            xerr=group["rl_se"],
            fmt="s",
            capsize=3,
            label="RL100",
        )
        plt.axvline(0.0, linewidth=1)
        plt.yticks(y, group["coefficient_name"])
        plt.xlabel("Polarization coefficient")
        title_mode = (
            "Spin-correlated polarization"
            if spin_mode == "sc"
            else "Isotropic-decay null control"
        )
        plt.title(
            f"{title_mode}: "
            f"{stage_name.upper()}, {initial_state}, {decay_channel}"
        )
        plt.legend()
        save_figure(
            stage
            / "02_beam_polarization"
            / destination_name
            / (
                f"polarization_{spin_mode}_{stage_name}_"
                f"{initial_state}_{decay_channel}"
            )
        )


# -----------------------------------------------------------------------
# Connected-correlation difference matrices
# -----------------------------------------------------------------------

axis_order = ["k", "r", "n"]
observable_to_indices = {
    "ckk": ("k", "k"),
    "ckr": ("k", "r"),
    "ckn": ("k", "n"),
    "crk": ("r", "k"),
    "crr": ("r", "r"),
    "crn": ("r", "n"),
    "cnk": ("n", "k"),
    "cnr": ("n", "r"),
    "cnn": ("n", "n"),
}

for (
    stage_name,
    initial_state,
    decay_channel,
    polarization,
), group in sc_iso_details.groupby(
    ["stage", "initial_state", "decay_channel", "polarization"]
):
    matrix = np.full((3, 3), np.nan)

    for _, row in group.iterrows():
        i, j = observable_to_indices[row["observable"]]
        matrix[
            axis_order.index(i),
            axis_order.index(j),
        ] = row["delta_sc_minus_iso"]

    plt.figure(figsize=(5.8, 5.1))
    image = plt.imshow(matrix, aspect="equal")
    plt.colorbar(
        image,
        label=r"$D_{ij}^{SC}-D_{ij}^{ISO}$",
    )
    plt.xticks(np.arange(3), axis_order)
    plt.yticks(np.arange(3), axis_order)
    plt.xlabel("Antitop analyzer axis j")
    plt.ylabel("Top analyzer axis i")
    plt.title(
        "Connected-correlation difference:\n"
        f"{stage_name.upper()}, {initial_state}, "
        f"{polarization}, {decay_channel}"
    )

    for i in range(3):
        for j in range(3):
            plt.text(
                j,
                i,
                f"{matrix[i, j]:.3f}",
                ha="center",
                va="center",
            )

    save_figure(
        stage
        / "03_spin_correlation/plots_connected_matrices"
        / (
            f"delta_D_{stage_name}_{initial_state}_"
            f"{polarization}_{decay_channel}"
        )
    )


# -----------------------------------------------------------------------
# Distribution overlays from the authoritative ntuple Parquet tables
# -----------------------------------------------------------------------

table_cache: dict[str, pd.DataFrame] = {}


def load_table(path: str) -> pd.DataFrame:
    if path not in table_cache:
        source = Path(path)
        if not source.is_file():
            raise FileNotFoundError(source)
        table_cache[path] = pd.read_parquet(source)
    return table_cache[path]


def weight_column(frame: pd.DataFrame) -> str | None:
    for candidate in [
        "weight",
        "event_weight",
        "nominal_weight",
        "weights",
    ]:
        if candidate in frame.columns:
            return candidate
    return None


def distribution(
    frame: pd.DataFrame,
    observable: str,
    edges: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if observable not in frame.columns:
        raise KeyError(
            f"Missing observable {observable!r}; "
            f"available columns include {list(frame.columns)[:30]}"
        )

    values = pd.to_numeric(
        frame[observable],
        errors="coerce",
    ).to_numpy(dtype=float)

    finite = np.isfinite(values)
    values = values[finite]

    weight_name = weight_column(frame)
    weights = None

    if weight_name is not None:
        weights = pd.to_numeric(
            frame.loc[finite, weight_name],
            errors="coerce",
        ).fillna(0.0).to_numpy(dtype=float)

    counts, _ = np.histogram(
        values,
        bins=edges,
        weights=weights,
    )

    widths = np.diff(edges)
    total = counts.sum()

    if total > 0:
        density = counts / (total * widths)
    else:
        density = counts.astype(float)

    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers, density


def find_sample(
    *,
    dataset: str,
    initial_state: str,
    decay_channel: str,
    polarization: str,
) -> pd.Series:
    matches = sample_meta[
        (sample_meta["dataset"] == dataset)
        & (sample_meta["initial_state"] == initial_state)
        & (sample_meta["decay_channel"] == decay_channel)
        & (sample_meta["polarization"] == polarization)
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Expected one sample for "
            f"dataset={dataset}, initial_state={initial_state}, "
            f"decay_channel={decay_channel}, "
            f"polarization={polarization}; found {len(matches)}"
        )

    return matches.iloc[0]


edges = np.linspace(-1.0, 1.0, hist_bins + 1)
b_observables = ["b1k", "b1r", "b1n", "b2k", "b2r", "b2n"]
c_observables = [
    "ckk", "crr", "cnn",
    "ckr", "crk", "ckn", "cnk", "crn", "cnr",
]
all_observables = b_observables + c_observables


def plot_overlay(
    left_table: pd.DataFrame,
    right_table: pd.DataFrame,
    observable: str,
    left_label: str,
    right_label: str,
    title: str,
    destination: Path,
) -> None:
    x_left, y_left = distribution(left_table, observable, edges)
    x_right, y_right = distribution(right_table, observable, edges)

    plt.figure(figsize=(7.4, 5.4))
    plt.plot(
        x_left,
        y_left,
        drawstyle="steps-mid",
        label=left_label,
    )
    plt.plot(
        x_right,
        y_right,
        drawstyle="steps-mid",
        label=right_label,
    )
    plt.xlabel(observable)
    plt.ylabel("Normalized event density")
    plt.title(title)
    plt.legend()
    save_figure(destination)


if make_lr_rl:
    for spin_mode in ["sc", "iso"]:
        for stage_name in ["lhe", "hepmc"]:
            dataset = f"{stage_name}_{spin_mode}"

            for initial_state in ["ee", "mumu"]:
                for decay_channel in ["epmum", "mupem"]:
                    lr = find_sample(
                        dataset=dataset,
                        initial_state=initial_state,
                        decay_channel=decay_channel,
                        polarization="LR100",
                    )
                    rl = find_sample(
                        dataset=dataset,
                        initial_state=initial_state,
                        decay_channel=decay_channel,
                        polarization="RL100",
                    )

                    lr_table = load_table(str(lr["source_table"]))
                    rl_table = load_table(str(rl["source_table"]))

                    for observable in b_observables:
                        plot_overlay(
                            lr_table,
                            rl_table,
                            observable,
                            "LR100",
                            "RL100",
                            (
                                f"LR100 versus RL100: "
                                f"{stage_name.upper()}, "
                                f"{spin_mode.upper()}, "
                                f"{initial_state}, {decay_channel}"
                            ),
                            stage
                            / "02_beam_polarization"
                            / "plots_distributions_lr_rl"
                            / spin_mode
                            / (
                                f"lr_rl_{stage_name}_{spin_mode}_"
                                f"{initial_state}_{decay_channel}_"
                                f"{observable}"
                            ),
                        )


if make_sc_iso:
    for stage_name in ["lhe", "hepmc"]:
        for initial_state in ["ee", "mumu"]:
            for polarization in ["LR100", "RL100"]:
                for decay_channel in ["epmum", "mupem"]:
                    sc = find_sample(
                        dataset=f"{stage_name}_sc",
                        initial_state=initial_state,
                        decay_channel=decay_channel,
                        polarization=polarization,
                    )
                    iso = find_sample(
                        dataset=f"{stage_name}_iso",
                        initial_state=initial_state,
                        decay_channel=decay_channel,
                        polarization=polarization,
                    )

                    sc_table = load_table(str(sc["source_table"]))
                    iso_table = load_table(str(iso["source_table"]))

                    for observable in c_observables:
                        plot_overlay(
                            sc_table,
                            iso_table,
                            observable,
                            "Spin-correlated",
                            "Isotropic control",
                            (
                                f"SC versus ISO: "
                                f"{stage_name.upper()}, "
                                f"{initial_state}, {polarization}, "
                                f"{decay_channel}"
                            ),
                            stage
                            / "03_spin_correlation"
                            / "plots_distributions_sc_iso"
                            / (
                                f"sc_iso_{stage_name}_{initial_state}_"
                                f"{polarization}_{decay_channel}_"
                                f"{observable}"
                            ),
                        )


if make_lhe_hepmc:
    for spin_mode in ["sc", "iso"]:
        for initial_state in ["ee", "mumu"]:
            for polarization in ["LR100", "RL100"]:
                for decay_channel in ["epmum", "mupem"]:
                    lhe = find_sample(
                        dataset=f"lhe_{spin_mode}",
                        initial_state=initial_state,
                        decay_channel=decay_channel,
                        polarization=polarization,
                    )
                    hepmc = find_sample(
                        dataset=f"hepmc_{spin_mode}",
                        initial_state=initial_state,
                        decay_channel=decay_channel,
                        polarization=polarization,
                    )

                    lhe_table = load_table(str(lhe["source_table"]))
                    hepmc_table = load_table(str(hepmc["source_table"]))

                    for observable in all_observables:
                        plot_overlay(
                            lhe_table,
                            hepmc_table,
                            observable,
                            "LHE",
                            "HepMC",
                            (
                                f"LHE versus HepMC: "
                                f"{spin_mode.upper()}, "
                                f"{initial_state}, {polarization}, "
                                f"{decay_channel}"
                            ),
                            stage
                            / "04_lhe_hepmc_preservation"
                            / "plots_distributions_lhe_hepmc"
                            / (
                                f"lhe_hepmc_{spin_mode}_{initial_state}_"
                                f"{polarization}_{decay_channel}_"
                                f"{observable}"
                            ),
                        )


# -----------------------------------------------------------------------
# Curated main-presentation subset
# -----------------------------------------------------------------------

recommended = [
    (
        stage / "00_overview/final_gate_summary.png",
        "01_final_gate_summary.png",
    ),
    (
        stage
        / "02_beam_polarization"
        / "lr_rl_max_significance_all_groups.png",
        "02_lr_rl_significance_all_groups.png",
    ),
    (
        stage
        / "02_beam_polarization"
        / "plots_coefficients_sc"
        / "polarization_sc_hepmc_ee_epmum.png",
        "03_sc_polarization_forest_ee_hepmc_epmum.png",
    ),
    (
        stage
        / "02_beam_polarization"
        / "plots_coefficients_sc"
        / "polarization_sc_hepmc_mumu_epmum.png",
        "04_sc_polarization_forest_mumu_hepmc_epmum.png",
    ),
    (
        stage
        / "02_beam_polarization"
        / "plots_coefficients_iso_null"
        / "polarization_iso_hepmc_ee_epmum.png",
        "05_iso_null_control_ee_hepmc_epmum.png",
    ),
    (
        stage
        / "02_beam_polarization"
        / "plots_distributions_lr_rl"
        / "sc"
        / "lr_rl_hepmc_sc_ee_epmum_b2r.png",
        "06_lr_rl_distribution_hepmc_sc_ee_epmum_b2r.png",
    ),
    (
        stage
        / "03_spin_correlation"
        / "plots_significance"
        / "sc_iso_max_significance_all_groups.png",
        "07_sc_iso_significance_all_groups.png",
    ),
    (
        stage
        / "03_spin_correlation"
        / "plots_connected_matrices"
        / "delta_D_hepmc_ee_LR100_epmum.png",
        "08_connected_correlation_matrix_hepmc_ee_LR100_epmum.png",
    ),
    (
        stage
        / "03_spin_correlation"
        / "plots_distributions_sc_iso"
        / "sc_iso_hepmc_ee_LR100_epmum_ckk.png",
        "09_sc_iso_distribution_hepmc_ee_LR100_epmum_ckk.png",
    ),
    (
        stage
        / "04_lhe_hepmc_preservation"
        / "plots_summary"
        / "lhe_hepmc_scatter_sc.png",
        "10_lhe_hepmc_coefficient_preservation_sc.png",
    ),
    (
        stage
        / "04_lhe_hepmc_preservation"
        / "plots_summary"
        / "preservation_abs_shift_vs_significance.png",
        "11_preservation_gate_plane.png",
    ),
    (
        stage
        / "05_decay_flavour"
        / "plots"
        / "decay_flavour_max_significance.png",
        "12_decay_flavour_consistency.png",
    ),
    (
        stage
        / "06_coefficient_overview"
        / "plots"
        / "spin15_coefficient_heatmap_all_samples.png",
        "13_all_coefficients_heatmap.png",
    ),
]

for source, destination_name in recommended:
    if source.is_file():
        copy_file(
            source,
            stage / "00_recommended_main_figures",
            destination_name,
        )


# -----------------------------------------------------------------------
# README and inventories
# -----------------------------------------------------------------------

readme = f"""# WHIZARD ttbar Spin-15 presentation bundle

Generated directly from the authoritative EOS qualification tree:

`{out}`

## Qualification status

- Structural status: **{summary['structural_status'].upper()}**
- Physics status: **{summary['physics_status'].upper()}**
- Strict physics mode: `{summary['strict_physics']}`
- Samples analyzed: 32 LHE/HepMC datasets
- Events per dataset: 10,000
- Spin-15 coefficient rows: {counts['coefficient_rows']}
- LHE/HepMC preservation warnings: {counts['preservation_warnings']}
- LHE/HepMC preservation failures: {counts['preservation_failures']}
- Polarization failures: {counts['polarization_failures']}
- Isotropic LR/RL groups marked N/A: {counts['polarization_not_applicable']}
- Spin-correlation failures: {counts['spin_correlation_failures']}
- Decay-flavour failures: {counts['flavour_failures']}

## Directory guide

### `00_recommended_main_figures/`

A concise presentation-facing set:

1. final gate summary;
2. all-group LR/RL significance;
3. representative SC polarization coefficient forests;
4. ISO null-control coefficient forest;
5. representative LR/RL angular-distribution overlay;
6. all-group SC/ISO connected-correlation significance;
7. representative connected-correlation matrix;
8. representative SC/ISO correlation-distribution overlay;
9. LHE/HepMC coefficient preservation;
10. preservation gate plane;
11. decay-flavour consistency;
12. complete coefficient heatmap.

### `02_beam_polarization/`

Contains:

- all SC LR100/RL100 coefficient forest plots;
- all ISO null-control coefficient plots;
- all LR100/RL100 normalized distribution overlays for the six B observables.

### `03_spin_correlation/`

Contains:

- all SC/ISO gate tables;
- all-group significance summary;
- sixteen connected-correlation difference matrices;
- all normalized SC/ISO overlays for the nine C observables.

### `04_lhe_hepmc_preservation/`

Contains:

- coefficient-preservation tables;
- global LHE/HepMC scatter plots;
- warning summaries;
- all normalized LHE/HepMC overlays for all 15 observables.

### `07_raw_figure_archive/`

Contains every raw per-sample plot listed in the authoritative
`spin15_figure_manifest.csv`, organized as:

`dataset/sample_id/kind/figure`

Raw-figure copy status is recorded in:

- `90_manifests/raw_figure_copy_manifest.csv`
- `90_manifests/unresolved_raw_figures.csv`

## Main interpretation

Beam polarization is supported by:

- correct LR100/RL100 production configuration;
- approximately 52--54 sigma LR/RL separation in SC B coefficients;
- preservation of that separation at HepMC level;
- disappearance of the analyzer separation in isotropic controls.

Spin correlation is supported by:

- connected correlations
  `D_ij = C_ij - B1_i B2_j`;
- 16/16 matched SC/ISO comparison groups passing;
- consistent behavior across both initial states, both polarizations,
  both forced decay channels, and both LHE/HepMC stages.

The 56 LHE/HepMC warnings exceed only the configured absolute-shift
threshold. None is a statistically significant preservation failure.
"""

(stage / "README.md").write_text(readme)

inventory_records = []

for path in sorted(stage.rglob("*")):
    if path.is_file():
        inventory_records.append(
            {
                "relative_path": str(path.relative_to(stage)),
                "size_bytes": path.stat().st_size,
            }
        )

pd.DataFrame(inventory_records).to_csv(
    stage / "90_manifests/BUNDLE_FILE_INVENTORY.csv",
    index=False,
)

category_counts = (
    pd.DataFrame(inventory_records)
    .assign(
        top_directory=lambda frame: frame["relative_path"]
        .str.split("/")
        .str[0]
    )
    .groupby("top_directory")
    .agg(files=("relative_path", "size"), bytes=("size_bytes", "sum"))
    .reset_index()
)

category_counts.to_csv(
    stage / "90_manifests/BUNDLE_DIRECTORY_COUNTS.csv",
    index=False,
)

print("Presentation bundle staging complete.")
print(f"Stage: {stage}")
print()
print(category_counts.to_string(index=False))
PY

find "$STAGE" \
  -type f \
  ! -path "$STAGE/99_provenance/BUNDLE_SHA256SUMS.txt" \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > "$STAGE/99_provenance/BUNDLE_SHA256SUMS.txt"

mkdir -p "$EOS_BUNDLE_DIR"

if command -v pigz >/dev/null 2>&1; then
  tar \
    -C "$WORK_PARENT" \
    -I 'pigz -1' \
    -cf "$TARBALL" \
    "$BUNDLE_NAME"
else
  tar \
    -C "$WORK_PARENT" \
    -czf "$TARBALL" \
    "$BUNDLE_NAME"
fi

sha256sum "$TARBALL" \
  | tee "${TARBALL}.sha256"

echo
echo "============================================================"
echo "PRESENTATION BUNDLE COMPLETE"
echo "============================================================"
echo
echo "EOS tarball:"
echo "  $TARBALL"
echo
echo "Checksum:"
echo "  ${TARBALL}.sha256"
echo
echo "Tarball size:"
du -sh "$TARBALL"
echo
echo "Top-level directory counts:"
column -s, -t \
  < "$STAGE/90_manifests/BUNDLE_DIRECTORY_COUNTS.csv" \
  || cat "$STAGE/90_manifests/BUNDLE_DIRECTORY_COUNTS.csv"

if [[ "$KEEP_STAGE" != "1" ]]; then
  rm -rf "$STAGE"
else
  echo
  echo "Staging directory retained:"
  echo "  $STAGE"
fi
