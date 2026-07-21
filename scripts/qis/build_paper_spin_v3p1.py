#!/usr/bin/env python3
"""Build a presentation-only paper-spin v3p1 release from validated v3."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import stat
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

TOOL_VERSION = "1.0.0"
CONNECTED_AXES = ("k", "r", "n")
DEFAULT_DIFFERENTIAL_COEFFICIENTS = ("B1k", "B2k", "Ckk", "Crr")
PHYSICS_PRESERVATION_PATHS = (
    "tables",
    "samples",
    "paper_spin_validation.json",
    "synthetic_closure.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a presentation-only v3p1 tree from a validated paper-spin v3 output."
    )
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--archive", type=Path, default=None)
    parser.add_argument("--connected-vlim", type=float, default=0.45)
    parser.add_argument(
        "--differential-coefficients",
        nargs="+",
        default=list(DEFAULT_DIFFERENTIAL_COEFFICIENTS),
    )
    parser.add_argument("--allow-nonpassing-source", action="store_true")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(candidate for candidate in path.rglob("*") if candidate.is_file())


def physics_snapshot(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for relative in PHYSICS_PRESERVATION_PATHS:
        target = root / relative
        if not target.exists():
            raise FileNotFoundError(f"Required physics product is missing: {target}")
        for file_path in iter_files(target):
            snapshot[file_path.relative_to(root).as_posix()] = sha256_file(file_path)
    return snapshot


def require_source(root: Path, allow_nonpassing: bool) -> dict[str, Any]:
    required = [
        root / "paper_spin_validation.json",
        root / "paper_spin_manifest.json",
        root / "tables" / "paper_spin_derived_quantities.csv",
        root / "tables" / "paper_spin_differential_coefficients.csv",
        root / "tables" / "paper_spin_comparison_summary.csv",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required source files:\n  " + "\n  ".join(missing))
    validation = json.loads((root / "paper_spin_validation.json").read_text())
    if not allow_nonpassing and validation.get("status") != "pass":
        raise RuntimeError("Source validation status is not pass")
    return validation


def display_initial_state(value: str) -> str:
    return {"ee": "e⁺e⁻", "mumu": "μ⁺μ⁻"}.get(str(value), str(value))


def display_decay(value: str) -> str:
    return {"epmum": "e⁺μ⁻", "mupem": "μ⁺e⁻"}.get(str(value), str(value))


def sample_title(row: pd.Series) -> str:
    return (
        f"{display_initial_state(row['initial_state'])} → tt̄ → {display_decay(row['decay_channel'])}; "
        f"{row['polarization']}, {str(row['spin_mode']).upper()}, {str(row['stage']).upper()}"
    )


def save_figure(fig: plt.Figure, base: Path) -> list[Path]:
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs = [base.with_suffix(".png"), base.with_suffix(".pdf")]
    fig.savefig(outputs[0], dpi=220, bbox_inches="tight")
    fig.savefig(outputs[1], bbox_inches="tight")
    plt.close(fig)
    return outputs


def comparison_label(row: pd.Series, comparison: str) -> str:
    initial = display_initial_state(row.get("initial_state_first", ""))
    decay = display_decay(row.get("decay_channel_first", ""))
    polarization = str(row.get("polarization_first", ""))
    spin_mode = str(row.get("spin_mode_first", "")).upper()
    stage = str(row.get("stage_first", "")).upper()
    if comparison == "hepmc_minus_lhe_paired":
        return f"{initial} · {decay} · {polarization} · {spin_mode}"
    return f"{initial} · {decay} · {polarization} · {spin_mode} · {stage}"


def plot_comparison_summaries(root: Path) -> list[dict[str, str]]:
    table = pd.read_csv(root / "tables" / "paper_spin_comparison_summary.csv")
    titles = {
        "LR100_minus_RL100": "LR100 − RL100 spin response",
        "SC_minus_ISO_connected": "Spin-correlated − isotropic connected correlations",
        "ee_minus_mumu": "Initial-state universality: e⁺e⁻ − μ⁺μ⁻",
        "epmum_minus_mupem": "Decay-flavour consistency: e⁺μ⁻ − μ⁺e⁻",
        "hepmc_minus_lhe_paired": "Post-shower charged-lepton analyzer migration",
    }
    subtitles = {
        "LR100_minus_RL100": "Maximum |z| among 15 spin coefficients; SC should separate strongly while ISO remains null.",
        "SC_minus_ISO_connected": "Maximum |z| among connected-correlation components; dashed line is 5σ.",
        "ee_minus_mumu": "Maximum |z| across matched coefficient sets; universality diagnostic.",
        "epmum_minus_mupem": "Maximum |z| across matched coefficient sets; flavour-consistency diagnostic.",
        "hepmc_minus_lhe_paired": (
            "HepMC post-recoil analyzers minus LHE hard-process analyzers: physical migration, not an identity gate."
        ),
    }
    records: list[dict[str, str]] = []
    out_dir = root / "plots" / "comparisons"
    for comparison, title in titles.items():
        frame = table[table["comparison"] == comparison].copy()
        if frame.empty:
            continue
        frame["label"] = [comparison_label(row, comparison) for _, row in frame.iterrows()]
        frame = frame.sort_values(["spin_mode_first", "stage_first", "max_abs_z", "label"])
        fig, ax = plt.subplots(figsize=(11.5, max(5.5, 0.33 * len(frame) + 2.2)))
        y = np.arange(len(frame))
        colors = ["tab:blue" if str(mode).lower() == "sc" else "tab:gray" for mode in frame["spin_mode_first"]]
        ax.barh(y, frame["max_abs_z"], color=colors, alpha=0.85)
        ax.set_yticks(y, frame["label"], fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel("Maximum |z| across compared coefficient components")
        ax.set_title(title, fontsize=15, pad=16)
        ax.text(0.0, 1.01, subtitles[comparison], transform=ax.transAxes, fontsize=9, va="bottom")
        if comparison != "hepmc_minus_lhe_paired":
            ax.axvline(5.0, color="black", linestyle="--", linewidth=1.0, label="5σ reference")
            ax.legend(loc="lower right")
        ax.grid(axis="x", alpha=0.25)
        for output in save_figure(fig, out_dir / comparison):
            records.append({"path": output.relative_to(root).as_posix(), "caption": subtitles[comparison]})
    return records


def connected_matrix_values(group: pd.DataFrame) -> np.ndarray:
    values = dict(zip(group["quantity"], group["value"], strict=True))
    matrix = np.zeros((3, 3), dtype=float)
    for i, first in enumerate(CONNECTED_AXES):
        for j, second in enumerate(CONNECTED_AXES):
            matrix[i, j] = float(values[f"Cconn_{first}{second}"])
    return matrix


def plot_connected_matrices(root: Path, requested_vlim: float) -> tuple[list[dict[str, str]], float]:
    table = pd.read_csv(root / "tables" / "paper_spin_derived_quantities.csv")
    table = table[table["family"] == "connected"].copy()
    observed_max = float(table["value"].abs().max())
    vlim = max(float(requested_vlim), math.ceil(observed_max * 20.0) / 20.0)
    norm = TwoSlopeNorm(vmin=-vlim, vcenter=0.0, vmax=vlim)
    records: list[dict[str, str]] = []
    columns = ["dataset", "sample_id", "initial_state", "decay_channel", "polarization", "spin_mode", "stage"]
    for keys, group in table.groupby(columns, sort=True):
        row = dict(zip(columns, keys, strict=True))
        matrix = connected_matrix_values(group)
        fig, ax = plt.subplots(figsize=(6.6, 5.7))
        image = ax.imshow(matrix, cmap="RdBu_r", norm=norm)
        ax.set_xticks(range(3), CONNECTED_AXES)
        ax.set_yticks(range(3), CONNECTED_AXES)
        ax.set_xlabel("Antitop analyzer axis j")
        ax.set_ylabel("Top analyzer axis i")
        ax.set_title("Connected spin-correlation matrix\n" + sample_title(pd.Series(row)), fontsize=12)
        for i in range(3):
            for j in range(3):
                color = "white" if abs(matrix[i, j]) > 0.55 * vlim else "black"
                ax.text(j, i, f"{matrix[i, j]:+.3f}", ha="center", va="center", color=color, fontsize=11)
        colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        colorbar.set_label(f"Connected coefficient (shared scale ±{vlim:.2f})")
        outputs = save_figure(fig, root / "plots" / "connected_matrices" / row["dataset"] / row["sample_id"])
        for output in outputs:
            records.append({
                "path": output.relative_to(root).as_posix(),
                "caption": f"Connected matrix on shared zero-centered ±{vlim:.2f} scale.",
            })
    payload = {
        "schema_version": 1,
        "shared_absolute_limit": vlim,
        "observed_maximum_absolute_connected_coefficient": observed_max,
        "colormap": "RdBu_r",
        "center": 0.0,
    }
    (root / "plots" / "connected_matrices" / "shared_scale.json").write_text(json.dumps(payload, indent=2) + "\n")
    return records, vlim


def make_shape_figure(shape: pd.DataFrame, limit: float, max_delta: float) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.4, 7.0))
    for stage, group in shape.groupby("stage"):
        ax.scatter(group["moment_coefficient"], group["shape_fit_coefficient"], s=18, alpha=0.62, label=str(stage).upper())
    ax.plot([-limit, limit], [-limit, limit], color="black", linestyle="--", linewidth=1.0)
    ax.set(xlim=(-limit, limit), ylim=(-limit, limit))
    ax.set_xlabel("Unconstrained moment coefficient")
    ax.set_ylabel("Constrained physical-likelihood coefficient")
    ax.set_title("Unconstrained moments versus constrained physical likelihood")
    ax.text(0.02, 0.98, f"Maximum |fit − moment| = {max_delta:.4f}\nThe fit enforces density-matrix physicality.", transform=ax.transAxes, va="top", fontsize=9)
    ax.grid(alpha=0.25)
    ax.legend()
    return fig


def plot_closure_products(root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    out_dir = root / "plots" / "closure"
    shape = pd.read_csv(root / "tables" / "paper_spin_moment_shape_comparison.csv")
    limit = max(1.0, float(np.nanmax(np.abs(shape[["moment_coefficient", "shape_fit_coefficient"]].to_numpy()))) * 1.05)
    max_delta = float(shape["shape_minus_moment"].abs().max())
    for base in ("moment_vs_shape", "unconstrained_moments_vs_physical_likelihood"):
        for output in save_figure(make_shape_figure(shape, limit, max_delta), out_dir / base):
            records.append({"path": output.relative_to(root).as_posix(), "caption": "Unconstrained moments versus the constrained physical-likelihood fit."})

    marginal = pd.read_csv(root / "tables" / "paper_spin_moment_marginal_comparison.csv")
    fig, ax = plt.subplots(figsize=(7.4, 7.0))
    for stage, group in marginal.groupby("stage"):
        ax.errorbar(
            group["moment_coefficient"], group["marginal_fit_coefficient"], yerr=group["marginal_fit_se"],
            fmt="o", markersize=3.0, alpha=0.45, linewidth=0.6, label=str(stage).upper(),
        )
    limit = max(1.0, float(np.nanmax(np.abs(marginal[["moment_coefficient", "marginal_fit_coefficient"]].to_numpy()))) * 1.05)
    ax.plot([-limit, limit], [-limit, limit], color="black", linestyle="--", linewidth=1.0)
    ax.set(xlim=(-limit, limit), ylim=(-limit, limit))
    ax.set_xlabel("Moment coefficient")
    ax.set_ylabel("Independent marginal-fit coefficient")
    ax.set_title("Validated moment-versus-marginal extraction closure")
    max_delta = float(marginal["marginal_minus_moment"].abs().max())
    ax.text(0.02, 0.98, f"Maximum |marginal − moment| = {max_delta:.4f}; configured limit = 0.0300", transform=ax.transAxes, va="top", fontsize=9)
    ax.grid(alpha=0.25)
    ax.legend()
    for output in save_figure(fig, out_dir / "moment_vs_marginal"):
        records.append({"path": output.relative_to(root).as_posix(), "caption": "Independent marginal fits versus event moments."})
    return records


def plot_density_summary(root: Path) -> list[dict[str, str]]:
    table = pd.read_csv(root / "tables" / "paper_spin_density_measures.csv")
    table = table.sort_values(["stage", "spin_mode", "raw_min_eigenvalue"]).reset_index(drop=True)
    labels = [
        f"{display_initial_state(row.initial_state)} · {display_decay(row.decay_channel)} · {row.polarization} · {str(row.spin_mode).upper()} · {str(row.stage).upper()}"
        for row in table.itertuples()
    ]
    fig, ax = plt.subplots(figsize=(12.0, 8.2))
    x = np.arange(len(table))
    colors = ["tab:blue" if bool(value) else "tab:red" for value in table["raw_physical"]]
    ax.scatter(x, table["raw_min_eigenvalue"], c=colors, s=40)
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xticks(x, labels, rotation=70, ha="right", fontsize=7)
    ax.set_ylabel("Minimum eigenvalue of raw moment density matrix")
    ax.set_title("Raw moment density-matrix physicality diagnostic")
    ax.text(0.0, 1.01, "Red: finite-statistics non-PSD raw matrix. Nonlinear measures use projected or likelihood-fitted matrices.", transform=ax.transAxes, fontsize=9, va="bottom")
    ax.grid(axis="y", alpha=0.25)
    return [
        {"path": output.relative_to(root).as_posix(), "caption": "Raw moment minimum eigenvalues."}
        for output in save_figure(fig, root / "plots" / "density" / "raw_min_eigenvalues")
    ]


def differential_axis_label(variable: str) -> str:
    return {
        "costheta_top_beam_plus": "cos θₜ relative to the positive incoming beam",
        "mtt_GeV": "m(tt̄) [GeV]",
    }.get(variable, variable)


def plot_differential_atlas(root: Path, coefficients: list[str]) -> list[dict[str, str]]:
    table = pd.read_csv(root / "tables" / "paper_spin_differential_coefficients.csv")
    missing = sorted(set(coefficients) - set(table["coefficient_name"].unique()))
    if missing:
        raise ValueError(f"Unavailable differential coefficients: {missing}")
    selected = table[table["coefficient_name"].isin(coefficients)].copy()
    records: list[dict[str, str]] = []
    index_rows: list[dict[str, Any]] = []
    columns = ["dataset", "sample_id", "initial_state", "decay_channel", "polarization", "spin_mode", "stage", "variable"]
    for keys, group in selected.groupby(columns, sort=True):
        row = dict(zip(columns, keys, strict=True))
        ncols = 2
        nrows = math.ceil(len(coefficients) / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(10.8, 4.2 * nrows), squeeze=False)
        axes_flat = axes.ravel()
        for axis, coefficient in zip(axes_flat, coefficients, strict=False):
            subset = group[group["coefficient_name"] == coefficient].sort_values("bin_index")
            centers = 0.5 * (subset["bin_low"].to_numpy() + subset["bin_high"].to_numpy())
            xerr = 0.5 * (subset["bin_high"].to_numpy() - subset["bin_low"].to_numpy())
            axis.errorbar(centers, subset["coefficient"], xerr=xerr, yerr=subset["coefficient_se"], fmt="o-", capsize=2.5, linewidth=1.1, markersize=4.0)
            axis.axhline(0.0, color="black", linewidth=0.8)
            axis.set_ylim(-1.05, 1.05)
            axis.set_title(coefficient)
            axis.set_xlabel(differential_axis_label(row["variable"]))
            axis.set_ylabel("Coefficient")
            axis.grid(alpha=0.25)
        for axis in axes_flat[len(coefficients):]:
            axis.axis("off")
        fig.suptitle(
            f"Differential spin coefficients versus {differential_axis_label(row['variable'])}\n{sample_title(pd.Series(row))}",
            fontsize=14, y=1.01,
        )
        count_min = int(group["events_in_bin"].min())
        count_max = int(group["events_in_bin"].max())
        fig.text(0.5, 0.005, f"Per-bin events: {count_min}–{count_max}; vertical bars are coefficient standard errors.", ha="center", fontsize=9)
        fig.tight_layout(rect=(0.0, 0.035, 1.0, 0.96))
        base = root / "plots" / "differential" / row["variable"] / row["dataset"] / row["sample_id"]
        base.parent.mkdir(parents=True, exist_ok=True)
        output = base.with_suffix(".png")
        fig.savefig(output, dpi=200, bbox_inches="tight")
        plt.close(fig)
        records.append({"path": output.relative_to(root).as_posix(), "caption": f"Differential {', '.join(coefficients)} for {row['sample_id']}."})
        index_rows.append({
            **row,
            "coefficients": ",".join(coefficients),
            "png": output.relative_to(root).as_posix(),
            "minimum_events_in_bin": count_min,
            "maximum_events_in_bin": count_max,
        })
    pd.DataFrame(index_rows).to_csv(root / "report" / "differential_figure_index.csv", index=False)
    return records


def figure_kind(path: Path) -> str:
    parts = path.parts
    for key in ("differential", "connected_matrices", "comparisons", "polarization", "closure", "analytic", "density", "coefficients"):
        if key in parts:
            return key
    return "plot"


def write_figure_manifest(root: Path, generated_records: list[dict[str, str]]) -> None:
    captions = {record["path"]: record["caption"] for record in generated_records}
    rows = []
    for path in sorted((root / "plots").rglob("*")):
        if path.is_file() and path.suffix.lower() in {".png", ".pdf"}:
            relative = path.relative_to(root).as_posix()
            rows.append({
                "kind": figure_kind(path.relative_to(root)),
                "path": relative,
                "format": path.suffix.lower().lstrip("."),
                "caption": captions.get(relative, "Retained validated v3 figure."),
            })
    with (root / "report" / "figure_manifest.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["kind", "path", "format", "caption"])
        writer.writeheader()
        writer.writerows(rows)


def validation_map(validation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("check")): item for item in validation.get("checks", [])}


def write_report(root: Path, validation: dict[str, Any], connected_vlim: float, differential_count: int) -> None:
    manifest = json.loads((root / "paper_spin_manifest.json").read_text())
    checks = validation_map(validation)
    migration = checks.get("LHE_HepMC_postshower_analyzer_migration", {})
    transport = checks.get("LHE_HepMC_event_transport", {})
    density = checks.get("physical_density_matrix", {})
    marginal = checks.get("moment_marginal_shape_closure", {})
    analytic = checks.get("independent_analytic_prediction", {})
    text = f"""# Paper-grade ttbar spin tomography report — v3p1 presentation release

## Release status

- Numerical physics baseline: **v3, unchanged**
- Presentation release: **v3p1**
- Validation status: **{validation.get('status')}**
- Fatal checks: **{len(validation.get('fatal_checks', []))}**
- Validated input datasets: **{manifest.get('samples')}**
- Moment coefficient rows: **{manifest.get('coefficient_rows')}**
- Differential coefficient rows: **{manifest.get('differential_rows')}**
- Convention: **{manifest.get('convention', {}).get('name')}**

## LHE/HepMC transport and post-shower migration

- **Event transport:** {transport.get('status', 'unknown')}. {transport.get('message', '')}
- **Analyzer migration:** {migration.get('status', 'unknown')}. {migration.get('message', '')}
- Maximum absolute migrated coefficient: **{migration.get('maximum_absolute_migration', float('nan')):.6f}**
- Maximum migration significance: **{migration.get('maximum_abs_z', float('nan')):.3f}σ**

The LHE analyzers use hard-process top-decay charged leptons. HepMC analyzers use the primary-W charged leptons after PYTHIA final-state shower recoil and possible QED final-state radiation. Their coefficient differences are physical post-shower migration, not an event-transport identity failure. The superseded `LHE_HepMC_preservation` check remains only as a compatibility marker.

## Extraction and physicality policy

1. Event moments with the full 15×15 covariance are the primary unbiased linear estimator.
2. Independent marginal fits validate moment extraction; maximum absolute difference: **{marginal.get('maximum_absolute_difference', float('nan')):.6f}**.
3. The simultaneous physical-likelihood fit enforces a positive-semidefinite density matrix and is not an identity test against unconstrained moments.
4. Projected or likelihood-fitted matrices are used for nonlinear quantum measures.
5. Raw non-PSD matrices: **{density.get('raw_unphysical', 'unknown')}**; projected and fit physical failures remain zero.
6. Independent tree-level benchmark: **{analytic.get('eligible_rows', 0)}** strict rows, **{analytic.get('failures', 0)}** failures.

## v3p1 presentation upgrades

- Connected matrices share one zero-centered scale: **±{connected_vlim:.2f}**.
- Comparison plots use concise labels and explicit semantics.
- Constrained physical-likelihood comparison is separated from marginal closure.
- Differential atlas added for both variables using B1k, B2k, Ckk, and Crr: **{differential_count}** PNG figures.
- Figure/checksum manifests use relative paths.
- `verify_bundle.sh` validates the release in place.

## Integrity guarantee

`provenance/v3p1_upgrade_manifest.json` records SHA-256 snapshots of every file under `tables/`, `samples/`, plus `paper_spin_validation.json` and `synthetic_closure.json`. The build aborts unless source v3 and output v3p1 are byte-identical for every one of these physics products.

## Principal products

- `paper_spin_validation.json`
- `tables/`
- `plots/comparisons/`
- `plots/connected_matrices/`
- `plots/closure/moment_vs_marginal.*`
- `plots/closure/unconstrained_moments_vs_physical_likelihood.*`
- `plots/differential/`
- `report/figure_manifest.csv`
- `report/differential_figure_index.csv`
- `provenance/SHA256SUMS.txt`
- `verify_bundle.sh`
"""
    (root / "report" / "paper_spin_report.md").write_text(text)


def write_release_notes(root: Path) -> None:
    (root / "PRESENTATION_UPGRADE.md").write_text(
        """# v3p1 presentation upgrade

Presentation-only derivative of the validated v3 physics baseline.

Changed: shared connected-matrix scales, clearer comparison semantics, separate marginal and physical-fit closure figures, complete differential atlas, corrected report wording, and portable relative manifests.

Unchanged: all samples, tables, covariance products, density matrices, validation JSON, and synthetic closure.

Run `./verify_bundle.sh` from this directory.
"""
    )


def write_verify_script(root: Path) -> None:
    script = '''#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT"
sha256sum --check provenance/SHA256SUMS.txt
python3 - <<'PYVERIFY'
import json
from pathlib import Path
root = Path.cwd()
validation = json.loads((root / "paper_spin_validation.json").read_text())
upgrade = json.loads((root / "provenance" / "v3p1_upgrade_manifest.json").read_text())
if validation.get("status") != "pass":
    raise SystemExit("validation status is not pass")
if validation.get("fatal_checks"):
    raise SystemExit(f"fatal checks: {validation['fatal_checks']}")
if not upgrade.get("physics_products_byte_identical"):
    raise SystemExit("physics byte-identity certification is false")
print("Validation status: pass")
print("Fatal checks: none")
print("Physics products byte-identical to v3: yes")
print("Portable v3p1 bundle verification: PASS")
PYVERIFY
'''
    path = root / "verify_bundle.sh"
    path.write_text(script)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_relative_checksums(root: Path) -> int:
    checksum_path = root / "provenance" / "SHA256SUMS.txt"
    checksum_path.unlink(missing_ok=True)
    files = [path for path in sorted(root.rglob("*")) if path.is_file() and path != checksum_path]
    with checksum_path.open("w") as stream:
        for path in files:
            stream.write(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}\n")
    return len(files)


def update_manifest(root: Path, source_root: Path, connected_vlim: float, figure_count: int) -> None:
    path = root / "paper_spin_manifest.json"
    payload = json.loads(path.read_text())
    payload["output_root"] = str(root)
    payload["presentation_release"] = {
        "name": "v3p1",
        "tool_version": TOOL_VERSION,
        "created_utc": utc_now(),
        "source_v3_root": str(source_root),
        "numerical_physics_unchanged": True,
        "shared_connected_matrix_absolute_limit": connected_vlim,
        "figure_files": figure_count,
        "portable_relative_manifests": True,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")


def create_archive(root: Path, archive: Path) -> None:
    archive = archive.expanduser().resolve()
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        raise FileExistsError(f"Archive already exists: {archive}")
    mode = "w:gz" if archive.name.endswith((".tar.gz", ".tgz")) else "w"
    with tarfile.open(archive, mode) as tar:
        tar.add(root, arcname=root.name)


def main() -> int:
    args = parse_args()
    source = args.input_root.expanduser().resolve()
    output = args.output_root.expanduser().resolve()
    if source == output:
        raise ValueError("Input and output roots must differ")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output}")
    validation = require_source(source, args.allow_nonpassing_source)
    source_snapshot = physics_snapshot(source)

    print(f"Copying validated v3 tree:\n  {source}\n→ {output}")
    shutil.copytree(source, output, symlinks=True)
    provenance = output / "provenance"
    old_checksum = provenance / "SHA256SUMS.txt"
    if old_checksum.exists():
        old_checksum.rename(provenance / "SHA256SUMS_v3_absolute.txt")
    old_figure_manifest = output / "report" / "figure_manifest.csv"
    if old_figure_manifest.exists():
        old_figure_manifest.rename(output / "report" / "figure_manifest_v3_absolute.csv")

    generated: list[dict[str, str]] = []
    generated.extend(plot_comparison_summaries(output))
    connected_records, connected_vlim = plot_connected_matrices(output, args.connected_vlim)
    generated.extend(connected_records)
    generated.extend(plot_closure_products(output))
    generated.extend(plot_density_summary(output))
    differential_records = plot_differential_atlas(output, args.differential_coefficients)
    generated.extend(differential_records)

    write_report(output, validation, connected_vlim, len(differential_records))
    write_release_notes(output)
    write_figure_manifest(output, generated)
    figure_count = sum(1 for path in (output / "plots").rglob("*") if path.is_file() and path.suffix.lower() in {".png", ".pdf"})
    update_manifest(output, source, connected_vlim, figure_count)
    write_verify_script(output)

    output_snapshot = physics_snapshot(output)
    if source_snapshot != output_snapshot:
        changed = sorted(key for key in set(source_snapshot) | set(output_snapshot) if source_snapshot.get(key) != output_snapshot.get(key))
        raise RuntimeError("Physics products changed:\n  " + "\n  ".join(changed[:50]))

    upgrade_manifest = {
        "schema_version": 1,
        "release": "v3p1",
        "tool_version": TOOL_VERSION,
        "created_utc": utc_now(),
        "source_v3_root": str(source),
        "output_v3p1_root": str(output),
        "source_validation_status": validation.get("status"),
        "source_fatal_checks": validation.get("fatal_checks", []),
        "physics_products_byte_identical": True,
        "physics_product_file_count": len(source_snapshot),
        "source_physics_sha256": source_snapshot,
        "output_physics_sha256": output_snapshot,
        "connected_matrix_shared_absolute_limit": connected_vlim,
        "generated_or_rewritten_figure_records": len(generated),
        "total_figure_files": figure_count,
        "differential_coefficients": args.differential_coefficients,
    }
    (provenance / "v3p1_upgrade_manifest.json").write_text(json.dumps(upgrade_manifest, indent=2) + "\n")
    checksum_count = write_relative_checksums(output)

    print("Physics products byte-identical: True")
    print(f"Physics product files checked: {len(source_snapshot)}")
    print(f"Figure files in v3p1: {figure_count}")
    print(f"Relative checksum entries: {checksum_count}")
    if args.archive is not None:
        create_archive(output, args.archive)
        print(f"Wrote archive: {args.archive.expanduser().resolve()}")
    print("Run from the v3p1 root: ./verify_bundle.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
