"""Publication-facing tables, figures, and Markdown report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .contracts import COEFFICIENT_NAMES


def _save(base: Path) -> list[Path]:
    base.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    outputs = [base.with_suffix(".png"), base.with_suffix(".pdf")]
    plt.savefig(outputs[0], dpi=180, bbox_inches="tight")
    plt.savefig(outputs[1], bbox_inches="tight")
    plt.close()
    return outputs


def _read_optional(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def generate_report(analysis_root: str | Path) -> dict[str, Any]:
    root = Path(analysis_root)
    tables = root / "tables"
    plots = root / "plots"
    report_dir = root / "report"
    report_dir.mkdir(parents=True, exist_ok=True)

    moments = pd.read_csv(tables / "paper_spin_coefficients_moments.csv")
    derived = pd.read_csv(tables / "paper_spin_derived_quantities.csv")
    density = pd.read_csv(tables / "paper_spin_density_measures.csv")
    shape = _read_optional(tables / "paper_spin_moment_shape_comparison.csv")
    analytic = _read_optional(tables / "paper_spin_analytic_comparison.csv")
    comparison_summary = pd.read_csv(tables / "paper_spin_comparison_summary.csv")
    comparison_details = pd.read_csv(tables / "paper_spin_comparison_details.csv")

    figure_manifest: list[dict[str, str]] = []

    # Complete coefficient heatmap.
    pivot = moments.pivot_table(
        index=["dataset", "sample_id"],
        columns="coefficient_name",
        values="coefficient",
    ).reindex(columns=COEFFICIENT_NAMES)
    plt.figure(figsize=(13, max(8, 0.28 * len(pivot))))
    image = plt.imshow(pivot.values, aspect="auto")
    plt.colorbar(image, label="Coefficient")
    plt.xticks(np.arange(15), COEFFICIENT_NAMES, rotation=45, ha="right")
    plt.yticks(
        np.arange(len(pivot)),
        [f"{dataset} | {sample}" for dataset, sample in pivot.index],
        fontsize=6,
    )
    plt.title("Canonical lepton-collider Spin-15 coefficients")
    for output in _save(plots / "coefficients/spin15_all_samples_heatmap"):
        figure_manifest.append({"kind": "coefficient_heatmap", "path": str(output)})

    # LR/RL B-vector forests for all SC stage/initial/channel groups.
    b_names = [name for name in COEFFICIENT_NAMES if name.startswith("B")]
    sc = moments[moments["spin_mode"] == "sc"]
    for keys, group in sc.groupby(["stage", "initial_state", "decay_channel"]):
        stage, initial_state, decay_channel = keys
        table = group.pivot_table(
            index="coefficient_name",
            columns="polarization",
            values=["coefficient", "coefficient_se"],
        ).reindex(b_names)
        if not {"LR100", "RL100"}.issubset(table["coefficient"].columns):
            continue
        y = np.arange(len(b_names))
        plt.figure(figsize=(8, 5.5))
        for offset, polarization, marker in [(-0.1, "LR100", "o"), (0.1, "RL100", "s")]:
            plt.errorbar(
                table["coefficient"][polarization],
                y + offset,
                xerr=table["coefficient_se"][polarization],
                fmt=marker,
                capsize=3,
                label=polarization,
            )
        plt.axvline(0.0, linewidth=1)
        plt.yticks(y, b_names)
        plt.xlabel("Coefficient")
        plt.title(f"SC LR/RL polarization: {stage}, {initial_state}, {decay_channel}")
        plt.legend()
        base = plots / "polarization" / f"B_forest_{stage}_{initial_state}_{decay_channel}"
        for output in _save(base):
            figure_manifest.append({"kind": "polarization_forest", "path": str(output)})

    # ISO null coefficient summary.
    iso = moments[(moments["spin_mode"] == "iso") & moments["coefficient_name"].isin(b_names)]
    if not iso.empty:
        summary = iso.groupby("coefficient_name").agg(
            mean=("coefficient", "mean"),
            rms=("coefficient", "std"),
        ).reindex(b_names)
        y = np.arange(len(summary))
        plt.figure(figsize=(8, 5.2))
        plt.errorbar(summary["mean"], y, xerr=summary["rms"], fmt="o", capsize=3)
        plt.axvline(0.0, linewidth=1)
        plt.yticks(y, summary.index)
        plt.xlabel("Mean ISO coefficient across groups (error bar = group RMS)")
        plt.title("Isotropic-decay polarization null control")
        for output in _save(plots / "polarization/ISO_B_null_summary"):
            figure_manifest.append({"kind": "iso_null", "path": str(output)})

    # Comparison max-z overview.
    for comparison, group in comparison_summary.groupby("comparison"):
        labels = [
            f"{row.initial_state_first}|{row.decay_channel_first}|{row.polarization_first}|"
            f"{row.spin_mode_first}|{row.stage_first}->{row.stage_second}"
            for row in group.itertuples()
        ]
        plt.figure(figsize=(11, max(5, 0.35 * len(group))))
        plt.barh(np.arange(len(group)), group["max_abs_z"])
        plt.axvline(5.0, linestyle="--", linewidth=1)
        plt.yticks(np.arange(len(group)), labels, fontsize=7)
        plt.xlabel("Maximum component significance |z|")
        plt.title(comparison.replace("_", " "))
        base = plots / "comparisons" / comparison
        for output in _save(base):
            figure_manifest.append({"kind": f"comparison_{comparison}", "path": str(output)})

    # Connected C matrices.
    connected = derived[derived["family"] == "connected"].copy()
    if not connected.empty:
        connected[["i", "j"]] = connected["quantity"].str.extract(r"Cconn_([krn])([krn])")
        axis = ["k", "r", "n"]
        for keys, group in connected.groupby(["dataset", "sample_id"]):
            dataset, sample_id = keys
            matrix = np.full((3, 3), np.nan)
            for row in group.itertuples():
                matrix[axis.index(row.i), axis.index(row.j)] = row.value
            plt.figure(figsize=(5.5, 5))
            image = plt.imshow(matrix, aspect="equal")
            plt.colorbar(image, label=r"$C^{conn}_{ij}$")
            plt.xticks(np.arange(3), axis)
            plt.yticks(np.arange(3), axis)
            plt.xlabel("Antitop axis")
            plt.ylabel("Top axis")
            plt.title(f"Connected correlation: {dataset}\n{sample_id}")
            for i in range(3):
                for j in range(3):
                    plt.text(j, i, f"{matrix[i,j]:.3f}", ha="center", va="center")
            base = plots / "connected_matrices" / dataset / sample_id
            for output in _save(base):
                figure_manifest.append({"kind": "connected_matrix", "path": str(output)})

    # Density physicality and nonlinear measures.
    plt.figure(figsize=(10, max(6, 0.25 * len(density))))
    labels = [f"{r.dataset}|{r.sample_id}" for r in density.itertuples()]
    plt.barh(np.arange(len(density)), density["raw_min_eigenvalue"])
    plt.axvline(0.0, linewidth=1)
    plt.yticks(np.arange(len(density)), labels, fontsize=6)
    plt.xlabel("Minimum eigenvalue of raw moment density matrix")
    plt.title("Finite-sample density-matrix physicality")
    for output in _save(plots / "density/raw_min_eigenvalues"):
        figure_manifest.append({"kind": "density_physicality", "path": str(output)})

    # Moment vs simultaneous physical shape fit.
    if not shape.empty:
        plt.figure(figsize=(7, 6))
        plt.scatter(shape["moment_coefficient"], shape["shape_fit_coefficient"], s=16)
        low = min(shape["moment_coefficient"].min(), shape["shape_fit_coefficient"].min()) - 0.05
        high = max(shape["moment_coefficient"].max(), shape["shape_fit_coefficient"].max()) + 0.05
        grid = np.linspace(low, high, 300)
        plt.plot(grid, grid, linewidth=1)
        plt.xlim(low, high)
        plt.ylim(low, high)
        plt.xlabel("Moment estimator")
        plt.ylabel("Simultaneous physical-likelihood fit")
        plt.title("Moment-versus-shape extraction closure")
        for output in _save(plots / "closure/moment_vs_shape"):
            figure_manifest.append({"kind": "moment_shape", "path": str(output)})

    # Analytic benchmark.
    if not analytic.empty:
        measured = analytic["analytic_coefficient"] + analytic["measured_minus_analytic"]
        plt.figure(figsize=(7, 6))
        plt.scatter(analytic["analytic_coefficient"], measured, s=18)
        low = min(analytic["analytic_coefficient"].min(), measured.min()) - 0.05
        high = max(analytic["analytic_coefficient"].max(), measured.max()) + 0.05
        grid = np.linspace(low, high, 300)
        plt.plot(grid, grid, linewidth=1)
        plt.xlabel("Independent tree-level analytic prediction")
        plt.ylabel("WHIZARD moment extraction")
        plt.title("Analytic production-density benchmark")
        for output in _save(plots / "analytic/measured_vs_tree"):
            figure_manifest.append({"kind": "analytic_benchmark", "path": str(output)})

    pd.DataFrame(figure_manifest).to_csv(report_dir / "figure_manifest.csv", index=False)

    manifest = json.loads((root / "paper_spin_manifest.json").read_text())
    warnings: list[str] = []
    if density["raw_physical"].astype(bool).sum() != len(density):
        warnings.append(
            "At least one unconstrained moment density matrix is not positive semidefinite; "
            "use the raw result for unbiased linear coefficients and the projected/physical-fit "
            "result only for nonlinear quantum measures."
        )
    if analytic.empty:
        warnings.append(
            "No analytic benchmark rows were produced. Review the exact generator SM inputs "
            "and the cos(theta) convention before enabling a strict signed comparison."
        )

    report = [
        "# Paper-grade ttbar spin tomography report",
        "",
        "## Scope",
        "",
        f"- Validated input datasets: **{manifest['samples']}**",
        f"- Moment coefficient rows: **{manifest['coefficient_rows']}**",
        f"- Convention: **{manifest['convention']['name']}**",
        "- Baseline qualification tree modified: **No**",
        "",
        "## Extraction methods",
        "",
        "1. Exact event-level first and mixed angular moments with a full 15x15 covariance.",
        "2. Simultaneous unbinned physical density-matrix likelihood fit.",
        "3. Linear symmetric/antisymmetric off-diagonal combinations and trace markers.",
        "4. Nonlinear connected-correlation covariance by Jacobian propagation.",
        "5. Raw and physical density-matrix diagnostics, with bootstrap support for nonlinear measures.",
        "6. Independent gamma/Z tree-level benchmark when the generator parameter and kinematics mappings are reviewed.",
        "",
        "## Important interpretation rule",
        "",
        "The unconstrained moment estimator is the primary unbiased estimator for the 15 linear coefficients. "
        "Physical projection or the Cholesky likelihood fit must be used for nonlinear quantities such as "
        "negativity, concurrence, and CHSH reach, because finite-statistics moments can yield a non-positive matrix.",
        "",
        "## Warnings",
        "",
    ]
    report.extend([f"- {warning}" for warning in warnings] or ["- None."])
    report.extend(
        [
            "",
            "## Products",
            "",
            "- `tables/paper_spin_coefficients_moments.csv`",
            "- `tables/paper_spin_derived_quantities.csv`",
            "- `tables/paper_spin_density_measures.csv`",
            "- `tables/paper_spin_moment_shape_comparison.csv`",
            "- `tables/paper_spin_comparison_details.csv`",
            "- `tables/paper_spin_comparison_summary.csv`",
            "- `tables/paper_spin_analytic_comparison.csv`",
            "- `report/figure_manifest.csv`",
            "",
        ]
    )
    (report_dir / "paper_spin_report.md").write_text("\n".join(report))
    return {
        "figures": len(figure_manifest),
        "warnings": warnings,
        "report": str(report_dir / "paper_spin_report.md"),
    }
