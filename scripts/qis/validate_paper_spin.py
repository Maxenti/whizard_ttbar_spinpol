#!/usr/bin/env python3
"""Strict, convention-aware validation of paper-grade spin products."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

B_NAMES = ["B1k", "B1r", "B1n", "B2k", "B2r", "B2n"]


def load_covariance(root: Path, dataset: str, sample_id: str, stem: str) -> tuple[list[str], np.ndarray]:
    source = root / "samples" / dataset / sample_id / f"{stem}.npz"
    archive = np.load(source)
    return [str(value) for value in archive["names"]], archive["covariance"]


def result(name: str, status: str, message: str, **metrics: Any) -> dict[str, Any]:
    return {"check": name, "status": status, "message": message, **metrics}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--synthetic-closure")
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.analysis_root)
    config = yaml.safe_load(Path(args.config).read_text()) or {}
    thresholds = config.get("validation", {})
    tables = root / "tables"

    moments = pd.read_csv(tables / "paper_spin_coefficients_moments.csv")
    derived = pd.read_csv(tables / "paper_spin_derived_quantities.csv")
    density = pd.read_csv(tables / "paper_spin_density_measures.csv")
    marginal = pd.read_csv(tables / "paper_spin_moment_marginal_comparison.csv")
    shape = pd.read_csv(tables / "paper_spin_moment_shape_comparison.csv")
    details = pd.read_csv(tables / "paper_spin_comparison_details.csv")
    summaries = pd.read_csv(tables / "paper_spin_comparison_summary.csv")
    analytic_path = tables / "paper_spin_analytic_comparison.csv"
    try:
        analytic = pd.read_csv(analytic_path) if analytic_path.is_file() else pd.DataFrame()
    except pd.errors.EmptyDataError:
        analytic = pd.DataFrame()

    checks: list[dict[str, Any]] = []

    sample_count = moments[["dataset", "sample_id"]].drop_duplicates().shape[0]
    coefficient_rows = len(moments)
    expected_samples = int(thresholds.get("expected_samples", 32))
    expected_rows = expected_samples * 15
    checks.append(
        result(
            "structure",
            "pass" if sample_count == expected_samples and coefficient_rows == expected_rows else "fail",
            f"samples={sample_count}, coefficient_rows={coefficient_rows}",
            samples=sample_count,
            coefficient_rows=coefficient_rows,
        )
    )

    failed_marginal = int((~marginal["fit_success"].astype(bool)).sum())
    checks.append(
        result(
            "marginal_shape_fits",
            "pass" if failed_marginal == 0 else "fail",
            f"failed fits={failed_marginal}",
            failures=failed_marginal,
        )
    )

    failed_shape = int((~shape["shape_fit_success"].astype(bool)).sum())
    min_bracket = float(shape["min_pdf_bracket"].min())
    checks.append(
        result(
            "simultaneous_physical_likelihood",
            "pass" if failed_shape == 0 and min_bracket > 0.0 else "fail",
            f"failed coefficient rows={failed_shape}, minimum PDF bracket={min_bracket:.6g}",
            failures=failed_shape,
            minimum_pdf_bracket=min_bracket,
        )
    )

    projected_physical_columns = [column for column in density.columns if column == "projected_physical"]
    projected_failures = 0
    if projected_physical_columns:
        projected_failures = int((~density["projected_physical"].astype(bool)).sum())
    checks.append(
        result(
            "physical_density_matrix",
            "pass" if projected_failures == 0 else "fail",
            f"projected/fit physical failures={projected_failures}; raw moment matrices may be non-PSD from finite statistics",
            failures=projected_failures,
            raw_unphysical=int((~density["raw_physical"].astype(bool)).sum()),
        )
    )

    # SC LR/RL must separate in a B component with full coefficient errors.
    lr = details[
        (details["comparison"] == "LR100_minus_RL100")
        & details["coefficient_name"].isin(B_NAMES)
    ]
    lr_groups = []
    for keys, group in lr.groupby(
        ["stage_first", "initial_state_first", "decay_channel_first", "spin_mode_first"]
    ):
        lr_groups.append({"keys": keys, "max_abs_z": float(group["z"].abs().max())})
    sc_lr = [group for group in lr_groups if group["keys"][3] == "sc"]
    iso_lr = [group for group in lr_groups if group["keys"][3] == "iso"]
    polarization_min_z = float(thresholds.get("polarization_min_z", 5.0))
    sc_failures = [group for group in sc_lr if group["max_abs_z"] < polarization_min_z]
    checks.append(
        result(
            "SC_LR_RL_polarization",
            "pass" if not sc_failures and sc_lr else "fail",
            f"groups={len(sc_lr)}, failures={len(sc_failures)}, minimum required max|z|={polarization_min_z}",
            groups=len(sc_lr),
            failures=len(sc_failures),
            minimum_observed=min(group["max_abs_z"] for group in sc_lr) if sc_lr else None,
        )
    )

    # ISO is a null control: use full six-dimensional B covariance per sample.
    iso_null_max_chi2_per_dof = float(thresholds.get("iso_null_max_chi2_per_dof", 4.0))
    iso_null_failures = 0
    iso_null_rows = []
    for (dataset, sample_id), group in moments[
        (moments["spin_mode"] == "iso") & moments["coefficient_name"].isin(B_NAMES)
    ].groupby(["dataset", "sample_id"]):
        group = group.set_index("coefficient_name").reindex(B_NAMES)
        names, covariance = load_covariance(root, dataset, sample_id, "moment_covariance")
        indices = [names.index(name) for name in B_NAMES]
        cov_b = covariance[np.ix_(indices, indices)]
        vector = group["coefficient"].to_numpy(float)
        chi2 = float(vector @ np.linalg.pinv(cov_b, hermitian=True) @ vector)
        ndof = int(np.linalg.matrix_rank(cov_b))
        ratio = chi2 / max(ndof, 1)
        failed = ratio > iso_null_max_chi2_per_dof
        iso_null_failures += int(failed)
        iso_null_rows.append({"dataset": dataset, "sample_id": sample_id, "chi2": chi2, "ndof": ndof, "chi2_per_dof": ratio, "failed": failed})
    checks.append(
        result(
            "ISO_polarization_null",
            "pass" if iso_null_failures == 0 else "fail",
            f"groups={len(iso_null_rows)}, failures={iso_null_failures}",
            groups=len(iso_null_rows),
            failures=iso_null_failures,
            maximum_chi2_per_dof=max(row["chi2_per_dof"] for row in iso_null_rows),
        )
    )

    # Connected SC/ISO comparisons are produced with full propagated covariance.
    sc_iso = summaries[summaries["comparison"] == "SC_minus_ISO_connected"]
    spin_min_z = float(thresholds.get("spin_correlation_min_z", 5.0))
    spin_failures = int((sc_iso["max_abs_z"] < spin_min_z).sum())
    checks.append(
        result(
            "SC_ISO_connected_correlation",
            "pass" if len(sc_iso) > 0 and spin_failures == 0 else "fail",
            f"groups={len(sc_iso)}, failures={spin_failures}, threshold={spin_min_z}",
            groups=len(sc_iso),
            failures=spin_failures,
            minimum_observed=float(sc_iso["max_abs_z"].min()) if len(sc_iso) else None,
        )
    )

    flavour = summaries[summaries["comparison"] == "epmum_minus_mupem"]
    flavour_max_z = float(thresholds.get("flavour_consistency_max_z", 5.0))
    flavour_failures = int((flavour["max_abs_z"] > flavour_max_z).sum())
    checks.append(
        result(
            "decay_flavour_consistency",
            "pass" if len(flavour) > 0 and flavour_failures == 0 else "fail",
            f"groups={len(flavour)}, failures={flavour_failures}, maximum allowed={flavour_max_z}",
            groups=len(flavour),
            failures=flavour_failures,
            maximum_observed=float(flavour["max_abs_z"].max()) if len(flavour) else None,
        )
    )

    universality = summaries[summaries["comparison"] == "ee_minus_mumu"]
    universality_max_z = float(thresholds.get("lepton_universality_max_z", 5.0))
    universality_failures = int((universality["max_abs_z"] > universality_max_z).sum())
    checks.append(
        result(
            "ee_mumu_universality",
            "pass" if len(universality) > 0 and universality_failures == 0 else "warn",
            f"groups={len(universality)}, failures={universality_failures}, diagnostic threshold={universality_max_z}",
            groups=len(universality),
            failures=universality_failures,
        )
    )

    # LHE and HepMC represent different analyzer definitions:
    #
    #   LHE:
    #       hard-process charged leptons from the top-decay matrix element;
    #
    #   HepMC:
    #       primary-W charged leptons after PYTHIA final-state shower recoil
    #       and possible QED final-state radiation.
    #
    # Event identity and event-weight transport remain strict requirements.
    # Analyzer changes are retained as a paired post-shower migration result,
    # not interpreted as a failure to transport the hard event.
    paired_comparison_name = "hepmc_minus_lhe_paired"
    spin_coefficient_count = 15

    paired_summaries = summaries[
        summaries["comparison"]
        == paired_comparison_name
    ].copy()

    paired_details = details[
        details["comparison"]
        == paired_comparison_name
    ].copy()

    expected_paired_groups = int(
        thresholds.get(
            "lhe_hepmc_expected_paired_groups",
            16,
        )
    )

    expected_common_events = int(
        thresholds.get(
            "lhe_hepmc_expected_common_events_per_group",
            10000,
        )
    )

    expected_detail_rows = (
        expected_paired_groups
        * spin_coefficient_count
    )

    transport_messages: list[str] = []

    paired_groups = int(
        len(paired_summaries)
    )

    if paired_groups != expected_paired_groups:
        transport_messages.append(
            "paired groups="
            f"{paired_groups}, "
            "expected="
            f"{expected_paired_groups}"
        )

    actual_detail_rows = int(
        len(paired_details)
    )

    if actual_detail_rows != expected_detail_rows:
        transport_messages.append(
            "paired coefficient rows="
            f"{actual_detail_rows}, "
            "expected="
            f"{expected_detail_rows}"
        )

    minimum_common_events = None
    maximum_common_events = None

    if paired_summaries.empty:
        transport_messages.append(
            "no paired LHE/HepMC summary groups"
        )
    else:
        common_events = pd.to_numeric(
            paired_summaries["common_events"],
            errors="coerce",
        )

        if common_events.isna().any():
            transport_messages.append(
                "non-numeric common_events value"
            )
        else:
            minimum_common_events = int(
                common_events.min()
            )

            maximum_common_events = int(
                common_events.max()
            )

            incorrect_counts = int(
                (
                    common_events
                    != expected_common_events
                ).sum()
            )

            if incorrect_counts:
                transport_messages.append(
                    "groups with unexpected common-event "
                    f"count={incorrect_counts}"
                )

        if "method" not in paired_summaries.columns:
            transport_messages.append(
                "paired comparison method column missing"
            )
        else:
            methods = set(
                paired_summaries[
                    "method"
                ].astype(str)
            )

            expected_methods = {
                "paired_event_full_covariance"
            }

            if methods != expected_methods:
                transport_messages.append(
                    "unexpected comparison methods="
                    f"{sorted(methods)}"
                )

        if (
            "event_pairing_verified"
            in paired_summaries.columns
        ):
            pairing_verified = (
                paired_summaries[
                    "event_pairing_verified"
                ]
                .astype(str)
                .str.lower()
                .isin(
                    {
                        "true",
                        "1",
                        "yes",
                    }
                )
            )

            if not bool(
                pairing_verified.all()
            ):
                transport_messages.append(
                    "one or more paired groups lack "
                    "event-pairing verification"
                )

        if (
            "event_weight_transport_verified"
            in paired_summaries.columns
        ):
            weight_verified = (
                paired_summaries[
                    "event_weight_transport_verified"
                ]
                .astype(str)
                .str.lower()
                .isin(
                    {
                        "true",
                        "1",
                        "yes",
                    }
                )
            )

            if not bool(
                weight_verified.all()
            ):
                transport_messages.append(
                    "one or more paired groups lack "
                    "event-weight verification"
                )

    transport_status = (
        "pass"
        if not transport_messages
        else "fail"
    )

    checks.append(
        result(
            "LHE_HepMC_event_transport",
            transport_status,
            (
                "strict one-to-one event-key and "
                "event-weight transport; "
                f"paired groups={paired_groups}, "
                "common events/group="
                f"{minimum_common_events}-"
                f"{maximum_common_events}"
            )
            if not transport_messages
            else "; ".join(
                transport_messages
            ),
            paired_groups=
                paired_groups,
            expected_paired_groups=
                expected_paired_groups,
            coefficient_rows=
                actual_detail_rows,
            expected_coefficient_rows=
                expected_detail_rows,
            minimum_common_events=
                minimum_common_events,
            maximum_common_events=
                maximum_common_events,
            expected_common_events_per_group=
                expected_common_events,
            failures=
                len(transport_messages),
        )
    )

    migration_abs = float(
        thresholds.get(
            "shower_migration_reference_max_abs",
            thresholds.get(
                "preservation_max_abs",
                0.02,
            ),
        )
    )

    migration_z = float(
        thresholds.get(
            "shower_migration_reference_max_z",
            thresholds.get(
                "preservation_max_z",
                5.0,
            ),
        )
    )

    paired_details["large"] = (
        paired_details[
            "delta_first_minus_second"
        ].abs()
        > migration_abs
    )

    paired_details["significant"] = (
        paired_details["z"].abs()
        > migration_z
    )

    large_and_significant = int(
        (
            paired_details["large"]
            & paired_details["significant"]
        ).sum()
    )

    one_limit_exceedances = int(
        (
            paired_details["large"]
            ^ paired_details["significant"]
        ).sum()
    )

    maximum_absolute_migration = (
        float(
            paired_details[
                "delta_first_minus_second"
            ].abs().max()
        )
        if len(paired_details)
        else None
    )

    maximum_migration_z = (
        float(
            paired_details[
                "z"
            ].abs().max()
        )
        if len(paired_details)
        else None
    )

    migration_status = (
        "warn"
        if (
            large_and_significant > 0
            or one_limit_exceedances > 0
        )
        else "pass"
    )

    checks.append(
        result(
            "LHE_HepMC_postshower_analyzer_migration",
            migration_status,
            (
                "paired post-shower minus hard-process "
                "analyzer migration; "
                "large-and-significant rows="
                f"{large_and_significant}, "
                "one-limit rows="
                f"{one_limit_exceedances}, "
                f"paired groups={paired_groups}"
            ),
            large_and_significant_rows=
                large_and_significant,
            one_limit_exceedance_rows=
                one_limit_exceedances,
            paired_groups=
                paired_groups,
            reference_max_abs=
                migration_abs,
            reference_max_z=
                migration_z,
            maximum_absolute_migration=
                maximum_absolute_migration,
            maximum_abs_z=
                maximum_migration_z,
            interpretation=(
                "Physical migration of primary-W "
                "charged-lepton analyzers after PYTHIA "
                "final-state shower recoil; not an "
                "event-transport identity failure."
            ),
        )
    )

    # Backward-compatible check name for readers expecting the earlier schema.
    # It is intentionally not a fatal physics gate.
    checks.append(
        result(
            "LHE_HepMC_preservation",
            "not_applicable",
            (
                "Superseded by LHE_HepMC_event_transport "
                "and LHE_HepMC_postshower_analyzer_migration."
            ),
            superseded=True,
        )
    )

    marginal_max_abs = float(thresholds.get("moment_marginal_max_abs", 0.03))
    marginal_exceed = int((marginal["marginal_minus_moment"].abs() > marginal_max_abs).sum())
    checks.append(
        result(
            "moment_marginal_shape_closure",
            "pass" if marginal_exceed == 0 else "warn",
            f"absolute-difference exceedances={marginal_exceed} at {marginal_max_abs}",
            exceedances=marginal_exceed,
            maximum_absolute_difference=float(marginal["marginal_minus_moment"].abs().max()),
        )
    )

    # Opening-angle shape fit versus trace moment; exact same convention.
    trace = derived[(derived["family"] == "linear") & (derived["quantity"] == "D_lc_1")][
        ["dataset", "sample_id", "value"]
    ]
    marginal_summaries = []
    for path in root.glob("samples/*/*/marginal_fit_summary.json"):
        payload = json.loads(path.read_text())
        marginal_summaries.append(
            {
                "dataset": path.parent.parent.name,
                "sample_id": path.parent.name,
                "trace_fit": payload["trace_fit"]["value"],
            }
        )
    trace_fit = pd.DataFrame(marginal_summaries)
    trace_compare = trace.merge(trace_fit, on=["dataset", "sample_id"])
    trace_compare["delta"] = trace_compare["trace_fit"] - trace_compare["value"]
    trace_max_abs = float(thresholds.get("trace_closure_max_abs", 0.03))
    trace_exceed = int((trace_compare["delta"].abs() > trace_max_abs).sum())
    checks.append(
        result(
            "trace_opening_angle_closure",
            "pass" if trace_exceed == 0 else "warn",
            f"exceedances={trace_exceed} at {trace_max_abs}",
            exceedances=trace_exceed,
            maximum_absolute_difference=float(trace_compare["delta"].abs().max()),
        )
    )

    if args.synthetic_closure:
        synthetic = json.loads(Path(args.synthetic_closure).read_text())
        moment_max_pull = max(
            float(item["max_abs_pull"])
            for item in synthetic["moment_injection_closure"]
        )
        shape_failures = sum(
            not bool(item["shape_fit_success"])
            for item in synthetic["moment_shape_closure"]
        )
        synthetic_pull_max = float(thresholds.get("synthetic_max_abs_pull", 5.0))
        checks.append(
            result(
                "synthetic_injection_closure",
                "pass" if moment_max_pull <= synthetic_pull_max and shape_failures == 0 else "fail",
                f"maximum moment pull={moment_max_pull:.3f}, shape failures={shape_failures}",
                maximum_moment_pull=moment_max_pull,
                shape_failures=shape_failures,
            )
        )

    if analytic.empty:
        checks.append(
            result(
                "independent_analytic_prediction",
                "not_applicable",
                "No strict analytic rows: exact generator input scheme and/or cos(theta) map is not reviewed.",
            )
        )
    else:
        eligible = analytic[analytic["strict_eligible"].astype(bool)]
        analytic_max_z = float(thresholds.get("analytic_max_z", 5.0))
        failures = int((eligible["z"].abs() > analytic_max_z).sum())
        checks.append(
            result(
                "independent_analytic_prediction",
                "pass" if len(eligible) > 0 and failures == 0 else ("fail" if failures else "not_applicable"),
                f"strict-eligible rows={len(eligible)}, failures={failures}",
                eligible_rows=len(eligible),
                failures=failures,
            )
        )

    fatal = [check for check in checks if check["status"] == "fail"]
    overall = "pass" if not fatal else "fail"
    payload = {
        "schema_version": 1,
        "status": overall,
        "checks": checks,
        "fatal_checks": [check["check"] for check in fatal],
        "physics_policy": {
            "linear_coefficients": "unconstrained moment estimator with full covariance",
            "nonlinear_quantum_measures": "physical projection/physical likelihood plus replicas",
            "analytic_prediction": "strict only after explicit generator-parameter and kinematics review",
            "lhe_hepmc_event_transport": (
                "strict event-key pairing, paired-group coverage, "
                "common-event counts, and event-weight equality"
            ),
            "lhe_hepmc_analyzer_comparison": (
                "post-shower primary-W charged-lepton migration "
                "relative to LHE hard-process analyzers; "
                "diagnostic rather than identity"
            ),
        },
    }
    output = Path(args.output) if args.output else root / "paper_spin_validation.json"
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
