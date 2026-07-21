"""Additive paper-grade tomography pipeline over validated Spin-15 ntuples."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .analytic_tree import TreeLevelSM, load_sm_parameters
from .basis import reconstruct_from_frame
from .benchmark import compare_to_analytic, comparison_rows
from .bootstrap import bootstrap_tomography, percentile_summary
from .contracts import AXES, COEFFICIENT_NAMES, coefficient_vector_to_parts
from .differential import estimate_differential
from .distribution_fit import fit_marginal_coefficients
from .density import (
    all_density_measures,
    density_matrix_from_coefficients,
    project_density_matrix,
    validate_density_matrix,
)
from .histograms import angular_observables, default_edges, normalized_histogram
from .io import (
    AnalyzerSample,
    SampleDescriptor,
    discover_ntuples,
    frame_to_analyzers,
    load_config,
)
from .moments import (
    DerivedResult,
    MomentResult,
    compare_independent,
    derive_connected_correlation,
    derive_linear_quantities,
    estimate_moments,
    estimate_paired_difference,
    event_estimands,
)
from .shape_fit import fit_physical_density_matrix


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {
                "real": value.real.tolist(),
                "imag": value.imag.tolist(),
            }
        return value.tolist()
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    raise TypeError(f"Cannot JSON-serialize {type(value)!r}")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n"
    )


def coefficient_rows(
    descriptor: SampleDescriptor,
    result: MomentResult,
    method: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, name in enumerate(COEFFICIENT_NAMES):
        rows.append(
            {
                **asdict(descriptor),
                "source_path": str(descriptor.source_path),
                "method": method,
                "coefficient_name": name,
                "coefficient": float(result.coefficient_vector[index]),
                "coefficient_se": float(result.standard_errors[index]),
                "events": result.events,
                "effective_events": result.effective_events,
                "weight_sum": result.weight_sum,
                "convention": result.convention_name,
            }
        )
    return rows


def derived_rows(
    descriptor: SampleDescriptor,
    result: DerivedResult,
    family: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, name in enumerate(result.names):
        rows.append(
            {
                **asdict(descriptor),
                "source_path": str(descriptor.source_path),
                "family": family,
                "quantity": name,
                "value": float(result.values[index]),
                "standard_error": float(result.standard_errors[index]),
            }
        )
    return rows


def save_covariance(
    output_base: Path,
    names: tuple[str, ...],
    covariance: np.ndarray,
) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_base.with_suffix(".npz"),
        names=np.asarray(names),
        covariance=np.asarray(covariance, dtype=float),
    )
    pd.DataFrame(covariance, index=names, columns=names).to_csv(
        output_base.with_suffix(".csv")
    )


def load_frame_and_sample(
    descriptor: SampleDescriptor,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, AnalyzerSample]:
    frame = pd.read_parquet(descriptor.source_path)
    sample = frame_to_analyzers(frame, descriptor.source_path, config)
    return frame, sample


def _descriptor_key(descriptor: SampleDescriptor) -> tuple[str, ...]:
    return (
        descriptor.stage,
        descriptor.initial_state,
        descriptor.decay_channel,
        descriptor.polarization,
        descriptor.spin_mode,
    )


def _comparison_metadata(
    first: SampleDescriptor,
    second: SampleDescriptor,
    comparison: str,
) -> dict[str, Any]:
    return {
        "comparison": comparison,
        "first_dataset": first.dataset,
        "first_sample_id": first.sample_id,
        "second_dataset": second.dataset,
        "second_sample_id": second.sample_id,
        "stage_first": first.stage,
        "stage_second": second.stage,
        "initial_state_first": first.initial_state,
        "initial_state_second": second.initial_state,
        "decay_channel_first": first.decay_channel,
        "decay_channel_second": second.decay_channel,
        "polarization_first": first.polarization,
        "polarization_second": second.polarization,
        "spin_mode_first": first.spin_mode,
        "spin_mode_second": second.spin_mode,
    }


def _independent_comparison_rows(
    first_descriptor: SampleDescriptor,
    second_descriptor: SampleDescriptor,
    first: MomentResult,
    second: MomentResult,
    comparison: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    result = compare_independent(first, second)
    metadata = _comparison_metadata(first_descriptor, second_descriptor, comparison)
    rows: list[dict[str, Any]] = []
    for index, name in enumerate(COEFFICIENT_NAMES):
        rows.append(
            {
                **metadata,
                "coefficient_name": name,
                "delta_first_minus_second": float(result["delta"][index]),
                "standard_error": float(result["standard_errors"][index]),
                "z": float(result["z"][index]),
            }
        )
    summary = {
        **metadata,
        "max_abs_z": result["max_abs_z"],
        "chi2": result["chi2"],
        "ndof": result["ndof"],
        "method": "independent_full_covariance",
    }
    return rows, summary


def _derived_comparison_rows(
    first_descriptor: SampleDescriptor,
    second_descriptor: SampleDescriptor,
    first: DerivedResult,
    second: DerivedResult,
    comparison: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if first.names != second.names:
        raise ValueError("Derived quantity names differ")
    delta = first.values - second.values
    covariance = first.covariance + second.covariance
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    z = np.divide(
        delta, standard_errors, out=np.full_like(delta, np.nan),
        where=standard_errors > 0.0,
    )
    inverse = np.linalg.pinv(covariance, hermitian=True)
    chi2 = float(delta @ inverse @ delta)
    ndof = int(np.linalg.matrix_rank(covariance))
    metadata = _comparison_metadata(first_descriptor, second_descriptor, comparison)
    rows = [
        {
            **metadata,
            "coefficient_name": name,
            "delta_first_minus_second": float(delta[index]),
            "standard_error": float(standard_errors[index]),
            "z": float(z[index]),
        }
        for index, name in enumerate(first.names)
    ]
    summary = {
        **metadata,
        "max_abs_z": float(np.nanmax(np.abs(z))),
        "chi2": chi2,
        "ndof": ndof,
        "method": "independent_full_covariance_derived",
    }
    return rows, summary


def _paired_lhe_hepmc_rows(
    lhe_descriptor: SampleDescriptor,
    hepmc_descriptor: SampleDescriptor,
    lhe_sample: AnalyzerSample,
    hepmc_sample: AnalyzerSample,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if lhe_sample.event_keys is None or hepmc_sample.event_keys is None:
        raise RuntimeError(
            "Paired LHE/HepMC comparison requires event keys in both ntuples"
        )
    if len(np.unique(lhe_sample.event_keys)) != len(lhe_sample.event_keys):
        raise RuntimeError("Duplicate LHE event keys prevent one-to-one pairing")
    if len(np.unique(hepmc_sample.event_keys)) != len(hepmc_sample.event_keys):
        raise RuntimeError("Duplicate HepMC event keys prevent one-to-one pairing")
    lhe_index = {key: index for index, key in enumerate(lhe_sample.event_keys)}
    hepmc_index = {key: index for index, key in enumerate(hepmc_sample.event_keys)}
    common = sorted(set(lhe_index) & set(hepmc_index), key=str)
    if not common:
        raise RuntimeError("No common event keys for paired LHE/HepMC comparison")

    lhe_indices = np.asarray([lhe_index[key] for key in common], dtype=int)
    hepmc_indices = np.asarray([hepmc_index[key] for key in common], dtype=int)
    lhe_estimands = event_estimands(
        lhe_sample.plus[lhe_indices],
        lhe_sample.minus[lhe_indices],
    )
    hepmc_estimands = event_estimands(
        hepmc_sample.plus[hepmc_indices],
        hepmc_sample.minus[hepmc_indices],
    )
    if not np.allclose(
        lhe_sample.weights[lhe_indices],
        hepmc_sample.weights[hepmc_indices],
        atol=0.0,
        rtol=1.0e-12,
    ):
        raise RuntimeError("Paired LHE/HepMC event weights differ")
    delta, covariance = estimate_paired_difference(
        hepmc_estimands,
        lhe_estimands,
        lhe_sample.weights[lhe_indices],
    )
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    z = np.divide(
        delta,
        standard_errors,
        out=np.full_like(delta, np.nan),
        where=standard_errors > 0.0,
    )
    inverse = np.linalg.pinv(covariance, hermitian=True)
    chi2 = float(delta @ inverse @ delta)
    ndof = int(np.linalg.matrix_rank(covariance))
    metadata = _comparison_metadata(
        hepmc_descriptor,
        lhe_descriptor,
        "hepmc_minus_lhe_paired",
    )
    rows = [
        {
            **metadata,
            "coefficient_name": name,
            "delta_first_minus_second": float(delta[index]),
            "standard_error": float(standard_errors[index]),
            "z": float(z[index]),
            "common_events": len(common),
        }
        for index, name in enumerate(COEFFICIENT_NAMES)
    ]
    summary = {
        **metadata,
        "max_abs_z": float(np.nanmax(np.abs(z))),
        "chi2": chi2,
        "ndof": ndof,
        "method": "paired_event_full_covariance",
        "common_events": len(common),
    }
    return rows, summary


def run_pipeline(
    qualification_root: str | Path,
    output_root: str | Path,
    config_path: str | Path | None,
    sample_filter: str | None = None,
) -> dict[str, Any]:
    qualification_root = Path(qualification_root).resolve()
    output_root = Path(output_root).resolve()
    if qualification_root == output_root or qualification_root in output_root.parents:
        # The additive output may sit next to the baseline but never inside it.
        if qualification_root == output_root or output_root.is_relative_to(qualification_root):
            raise ValueError(
                "Paper-grade outputs must not be written inside the validated baseline tree"
            )
    output_root.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)
    descriptors = discover_ntuples(qualification_root)
    if sample_filter:
        regex = pd.Series([d.sample_id for d in descriptors]).str.contains(
            sample_filter, regex=True
        )
        descriptors = [d for d, keep in zip(descriptors, regex, strict=True) if keep]
    if not descriptors:
        raise ValueError("No descriptors remain after sample filtering")

    moment_results: dict[str, MomentResult] = {}
    samples: dict[str, AnalyzerSample] = {}
    frames: dict[str, pd.DataFrame] = {}
    descriptor_by_id = {descriptor.sample_id + "::" + descriptor.dataset: descriptor for descriptor in descriptors}

    coefficient_records: list[dict[str, Any]] = []
    derived_records: list[dict[str, Any]] = []
    density_records: list[dict[str, Any]] = []
    differential_records: list[dict[str, Any]] = []
    marginal_records: list[dict[str, Any]] = []
    shape_records: list[dict[str, Any]] = []
    analytic_records: list[dict[str, Any]] = []

    shape_config = config.get("shape_fit", {})
    bootstrap_config = config.get("bootstrap", {})
    analytic_config = config.get("analytic_benchmark", {})
    tree = None
    if bool(analytic_config.get("enabled", False)):
        sm_path = analytic_config.get("sm_parameters")
        if sm_path is None:
            raise ValueError("analytic_benchmark.sm_parameters is required")
        sm_path = Path(sm_path)
        if not sm_path.is_absolute() and config_path is not None:
            sm_path = Path(config_path).resolve().parent / sm_path
        tree = TreeLevelSM(load_sm_parameters(sm_path))

    for descriptor in descriptors:
        key = descriptor.sample_id + "::" + descriptor.dataset
        frame, sample = load_frame_and_sample(descriptor, config)
        frames[key] = frame
        samples[key] = sample
        sample_dir = output_root / "samples" / descriptor.dataset / descriptor.sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)
        basis_config = config.get("basis_reconstruction_audit", {})
        if bool(basis_config.get("enabled", False)):
            if not bool(basis_config.get("mapping_reviewed", False)):
                write_json(
                    sample_dir / "basis_audit_skipped.json",
                    {"reason": "basis_reconstruction_audit.mapping_reviewed is false"},
                )
            else:
                try:
                    basis_audit = reconstruct_from_frame(
                        frame,
                        basis_config["four_vectors"],
                        float(basis_config.get("singular_tolerance", 1.0e-10)),
                    )
                except (KeyError, ValueError) as error:
                    write_json(
                        sample_dir / "basis_audit_skipped.json",
                        {"reason": str(error)},
                    )
                else:
                    finite = ~basis_audit.singular
                    plus_delta = basis_audit.plus[finite] - sample.plus[finite]
                    minus_delta = basis_audit.minus[finite] - sample.minus[finite]
                    write_json(
                        sample_dir / "basis_audit.json",
                        {
                            "events": len(frame),
                            "singular_events": int(np.count_nonzero(basis_audit.singular)),
                            "max_plus_component_residual": float(np.max(np.abs(plus_delta), initial=0.0)),
                            "max_minus_component_residual": float(np.max(np.abs(minus_delta), initial=0.0)),
                            "max_orthonormal_residual": float(np.max(basis_audit.orthonormal_residual)),
                            "handedness_min": float(np.min(basis_audit.handedness)),
                            "handedness_max": float(np.max(basis_audit.handedness)),
                            "metadata": basis_audit.metadata,
                        },
                    )

        moments = estimate_moments(sample)
        moment_results[key] = moments
        coefficient_records.extend(coefficient_rows(descriptor, moments, "moments"))

        save_covariance(
            sample_dir / "moment_covariance",
            COEFFICIENT_NAMES,
            moments.covariance,
        )

        linear = derive_linear_quantities(moments)
        connected = derive_connected_correlation(moments)
        derived_records.extend(derived_rows(descriptor, linear, "linear"))
        derived_records.extend(derived_rows(descriptor, connected, "connected"))
        save_covariance(
            sample_dir / "linear_derived_covariance",
            linear.names,
            linear.covariance,
        )
        save_covariance(
            sample_dir / "connected_covariance",
            connected.names,
            connected.covariance,
        )

        rho_raw = density_matrix_from_coefficients(
            moments.coefficient_vector,
            moments.convention_name,
        )
        validation = validate_density_matrix(rho_raw)
        projection = project_density_matrix(rho_raw)
        raw_measures = all_density_measures(rho_raw, moments.convention_name)
        projected_measures = all_density_measures(
            projection.rho,
            moments.convention_name,
        )
        np.save(sample_dir / "rho_raw.npy", rho_raw)
        np.save(sample_dir / "rho_projected.npy", projection.rho)
        density_record = {
            **asdict(descriptor),
            "source_path": str(descriptor.source_path),
            "raw_physical": validation.valid,
            "raw_min_eigenvalue": validation.min_eigenvalue,
            "raw_purity": validation.purity,
            "projection_frobenius_distance": projection.frobenius_distance,
            **{f"raw_{name}": value for name, value in raw_measures.items() if np.isscalar(value)},
            **{
                f"projected_{name}": value
                for name, value in projected_measures.items()
                if np.isscalar(value)
            },
        }
        density_records.append(density_record)
        write_json(
            sample_dir / "density_summary.json",
            {
                "descriptor": asdict(descriptor),
                "validation": asdict(validation),
                "projection": asdict(projection),
                "raw_measures": raw_measures,
                "projected_measures": projected_measures,
            },
        )

        differential_config = config.get("differential", {})
        if bool(differential_config.get("enabled", False)):
            for variable_config in differential_config.get("variables", []):
                try:
                    bins = estimate_differential(frame, sample, variable_config)
                except (KeyError, RuntimeError, ValueError) as error:
                    write_json(
                        sample_dir / f"differential_{variable_config.get('name', 'unknown')}_skipped.json",
                        {"reason": str(error), "variable": variable_config},
                    )
                    continue
                for bin_result in bins:
                    save_covariance(
                        sample_dir / f"differential_{bin_result.variable}_bin{bin_result.bin_index:03d}_covariance",
                        COEFFICIENT_NAMES,
                        bin_result.moment.covariance,
                    )
                    for coefficient_index, coefficient_name in enumerate(COEFFICIENT_NAMES):
                        differential_records.append(
                            {
                                **asdict(descriptor),
                                "source_path": str(descriptor.source_path),
                                "variable": bin_result.variable,
                                "bin_index": bin_result.bin_index,
                                "bin_low": bin_result.bin_low,
                                "bin_high": bin_result.bin_high,
                                "events_in_bin": bin_result.events,
                                "coefficient_name": coefficient_name,
                                "coefficient": float(bin_result.moment.coefficient_vector[coefficient_index]),
                                "coefficient_se": float(bin_result.moment.standard_errors[coefficient_index]),
                            }
                        )

        histogram_config = config.get("histograms", {})
        if bool(histogram_config.get("enabled", True)):
            histogram_rows: list[dict[str, Any]] = []
            for observable, values in angular_observables(sample).items():
                histogram = normalized_histogram(
                    observable,
                    values,
                    sample.weights,
                    default_edges(observable, int(histogram_config.get("bins", 20))),
                )
                covariance_path = sample_dir / f"histogram_{observable}_covariance.npz"
                np.savez_compressed(
                    covariance_path,
                    edges=histogram.edges,
                    centers=histogram.centers,
                    probability_covariance=histogram.probability_covariance,
                    density_covariance=histogram.density_covariance,
                )
                for bin_index, (low, high, center, probability, density_value) in enumerate(
                    zip(
                        histogram.edges[:-1], histogram.edges[1:], histogram.centers,
                        histogram.probabilities, histogram.densities, strict=True,
                    )
                ):
                    histogram_rows.append(
                        {
                            "observable": observable,
                            "bin_index": bin_index,
                            "bin_low": float(low),
                            "bin_high": float(high),
                            "bin_center": float(center),
                            "probability": float(probability),
                            "probability_se": float(np.sqrt(max(histogram.probability_covariance[bin_index, bin_index], 0.0))),
                            "density": float(density_value),
                            "density_se": float(np.sqrt(max(histogram.density_covariance[bin_index, bin_index], 0.0))),
                            "underflow": histogram.underflow,
                            "overflow": histogram.overflow,
                        }
                    )
            pd.DataFrame(histogram_rows).to_csv(sample_dir / "angular_histograms.csv", index=False)

        marginal = fit_marginal_coefficients(sample)
        for index, name in enumerate(COEFFICIENT_NAMES):
            marginal_records.append(
                {
                    **asdict(descriptor),
                    "source_path": str(descriptor.source_path),
                    "coefficient_name": name,
                    "moment_coefficient": float(moments.coefficient_vector[index]),
                    "marginal_fit_coefficient": float(marginal.coefficient_vector[index]),
                    "marginal_fit_se": float(marginal.standard_errors[index]),
                    "marginal_minus_moment": float(
                        marginal.coefficient_vector[index] - moments.coefficient_vector[index]
                    ),
                    "fit_success": marginal.scalar_fits[name].success,
                }
            )
        write_json(sample_dir / "marginal_fit_summary.json", asdict(marginal))

        if bool(shape_config.get("enabled", True)):
            fit = fit_physical_density_matrix(
                sample,
                initial_coefficient_vector=moments.coefficient_vector,
                convention=moments.convention_name,
                max_iterations=int(shape_config.get("max_iterations", 2000)),
                gradient_tolerance=float(shape_config.get("gradient_tolerance", 1.0e-8)),
                calculate_covariance=bool(shape_config.get("calculate_covariance", True)),
            )
            np.save(sample_dir / "rho_shape_fit.npy", fit.rho)
            if fit.coefficient_covariance is not None:
                save_covariance(
                    sample_dir / "shape_fit_covariance",
                    COEFFICIENT_NAMES,
                    fit.coefficient_covariance,
                )
            for index, name in enumerate(COEFFICIENT_NAMES):
                shape_records.append(
                    {
                        **asdict(descriptor),
                        "source_path": str(descriptor.source_path),
                        "coefficient_name": name,
                        "moment_coefficient": float(moments.coefficient_vector[index]),
                        "shape_fit_coefficient": float(fit.coefficient_vector[index]),
                        "shape_minus_moment": float(
                            fit.coefficient_vector[index] - moments.coefficient_vector[index]
                        ),
                        "shape_fit_success": fit.success,
                        "shape_objective": fit.objective,
                        "min_pdf_bracket": fit.min_pdf_bracket,
                    }
                )
            write_json(sample_dir / "shape_fit_summary.json", asdict(fit))

        if int(bootstrap_config.get("replicas", 0)) > 0:
            replica_result = bootstrap_tomography(
                sample,
                replicas=int(bootstrap_config["replicas"]),
                seed=int(bootstrap_config.get("seed", 20260721)),
            )
            np.savez_compressed(
                sample_dir / "bootstrap_replicas.npz",
                coefficient_replicas=replica_result.coefficient_replicas,
                raw_measure_replicas=replica_result.raw_measure_replicas,
                projected_measure_replicas=replica_result.projected_measure_replicas,
                measure_names=np.asarray(replica_result.measure_names),
            )
            write_json(
                sample_dir / "bootstrap_summary.json",
                {
                    "metadata": replica_result.metadata,
                    "raw": percentile_summary(
                        replica_result.raw_measure_replicas,
                        replica_result.measure_names,
                    ),
                    "projected": percentile_summary(
                        replica_result.projected_measure_replicas,
                        replica_result.measure_names,
                    ),
                },
            )

        if tree is not None and descriptor.spin_mode == "sc":
            try:
                analytic = compare_to_analytic(
                    moments,
                    descriptor,
                    frame,
                    tree,
                    config,
                )
            except (KeyError, RuntimeError, ValueError) as error:
                write_json(
                    sample_dir / "analytic_benchmark_skipped.json",
                    {"reason": str(error), "descriptor": asdict(descriptor)},
                )
            else:
                analytic_records.extend(comparison_rows(analytic, descriptor))
                write_json(
                    sample_dir / "analytic_benchmark.json",
                    asdict(analytic),
                )

    tables_dir = output_root / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(coefficient_records).to_csv(
        tables_dir / "paper_spin_coefficients_moments.csv", index=False
    )
    pd.DataFrame(derived_records).to_csv(
        tables_dir / "paper_spin_derived_quantities.csv", index=False
    )
    pd.DataFrame(density_records).to_csv(
        tables_dir / "paper_spin_density_measures.csv", index=False
    )
    pd.DataFrame(differential_records).to_csv(
        tables_dir / "paper_spin_differential_coefficients.csv", index=False
    )
    pd.DataFrame(marginal_records).to_csv(
        tables_dir / "paper_spin_moment_marginal_comparison.csv", index=False
    )
    pd.DataFrame(shape_records).to_csv(
        tables_dir / "paper_spin_moment_shape_comparison.csv", index=False
    )
    pd.DataFrame(analytic_records).to_csv(
        tables_dir / "paper_spin_analytic_comparison.csv", index=False
    )

    comparison_rows_all: list[dict[str, Any]] = []
    comparison_summaries: list[dict[str, Any]] = []

    # LR/RL comparisons at fixed stage, initial state, decay channel and spin mode.
    for stage in sorted({d.stage for d in descriptors}):
        for initial_state in sorted({d.initial_state for d in descriptors}):
            for decay_channel in sorted({d.decay_channel for d in descriptors}):
                for spin_mode in sorted({d.spin_mode for d in descriptors}):
                    matches = [
                        d for d in descriptors
                        if d.stage == stage
                        and d.initial_state == initial_state
                        and d.decay_channel == decay_channel
                        and d.spin_mode == spin_mode
                    ]
                    by_pol = {d.polarization: d for d in matches}
                    if {"LR100", "RL100"}.issubset(by_pol):
                        first, second = by_pol["LR100"], by_pol["RL100"]
                        rows, summary = _independent_comparison_rows(
                            first,
                            second,
                            moment_results[first.sample_id + "::" + first.dataset],
                            moment_results[second.sample_id + "::" + second.dataset],
                            "LR100_minus_RL100",
                        )
                        comparison_rows_all.extend(rows)
                        comparison_summaries.append(summary)

    # SC/ISO at fixed stage, initial state, channel, polarization.
    for stage in sorted({d.stage for d in descriptors}):
        for initial_state in sorted({d.initial_state for d in descriptors}):
            for decay_channel in sorted({d.decay_channel for d in descriptors}):
                for polarization in sorted({d.polarization for d in descriptors}):
                    matches = [
                        d for d in descriptors
                        if d.stage == stage
                        and d.initial_state == initial_state
                        and d.decay_channel == decay_channel
                        and d.polarization == polarization
                    ]
                    by_spin = {d.spin_mode: d for d in matches}
                    if {"sc", "iso"}.issubset(by_spin):
                        first, second = by_spin["sc"], by_spin["iso"]
                        first_moment = moment_results[first.sample_id + "::" + first.dataset]
                        second_moment = moment_results[second.sample_id + "::" + second.dataset]
                        rows, summary = _derived_comparison_rows(
                            first,
                            second,
                            derive_connected_correlation(first_moment),
                            derive_connected_correlation(second_moment),
                            "SC_minus_ISO_connected",
                        )
                        comparison_rows_all.extend(rows)
                        comparison_summaries.append(summary)

    # epmum/mupem at fixed dataset, initial state, polarization, spin mode.
    for dataset in sorted({d.dataset for d in descriptors}):
        for initial_state in sorted({d.initial_state for d in descriptors}):
            for polarization in sorted({d.polarization for d in descriptors}):
                for spin_mode in sorted({d.spin_mode for d in descriptors}):
                    matches = [
                        d for d in descriptors
                        if d.dataset == dataset
                        and d.initial_state == initial_state
                        and d.polarization == polarization
                        and d.spin_mode == spin_mode
                    ]
                    by_decay = {d.decay_channel: d for d in matches}
                    if {"epmum", "mupem"}.issubset(by_decay):
                        first, second = by_decay["epmum"], by_decay["mupem"]
                        rows, summary = _independent_comparison_rows(
                            first,
                            second,
                            moment_results[first.sample_id + "::" + first.dataset],
                            moment_results[second.sample_id + "::" + second.dataset],
                            "epmum_minus_mupem",
                        )
                        comparison_rows_all.extend(rows)
                        comparison_summaries.append(summary)

    # e+e- versus mu+mu- lepton-universality closure at fixed remaining labels.
    for dataset in sorted({d.dataset for d in descriptors}):
        for decay_channel in sorted({d.decay_channel for d in descriptors}):
            for polarization in sorted({d.polarization for d in descriptors}):
                for spin_mode in sorted({d.spin_mode for d in descriptors}):
                    matches = [
                        d for d in descriptors
                        if d.dataset == dataset
                        and d.decay_channel == decay_channel
                        and d.polarization == polarization
                        and d.spin_mode == spin_mode
                    ]
                    by_initial = {d.initial_state: d for d in matches}
                    if {"ee", "mumu"}.issubset(by_initial):
                        first, second = by_initial["ee"], by_initial["mumu"]
                        rows, summary = _independent_comparison_rows(
                            first, second,
                            moment_results[first.sample_id + "::" + first.dataset],
                            moment_results[second.sample_id + "::" + second.dataset],
                            "ee_minus_mumu",
                        )
                        comparison_rows_all.extend(rows)
                        comparison_summaries.append(summary)

    # Paired LHE/HepMC, requiring explicit event keys. Fall back to independent
    # comparison and record that the paired requirement was not met.
    physical_keys = sorted(
        {
            (d.initial_state, d.decay_channel, d.polarization, d.spin_mode)
            for d in descriptors
        }
    )
    for initial_state, decay_channel, polarization, spin_mode in physical_keys:
        matches = [
            d for d in descriptors
            if d.initial_state == initial_state
            and d.decay_channel == decay_channel
            and d.polarization == polarization
            and d.spin_mode == spin_mode
        ]
        by_stage = {d.stage: d for d in matches}
        if {"lhe", "hepmc"}.issubset(by_stage):
            lhe, hepmc = by_stage["lhe"], by_stage["hepmc"]
            lhe_key = lhe.sample_id + "::" + lhe.dataset
            hepmc_key = hepmc.sample_id + "::" + hepmc.dataset
            try:
                rows, summary = _paired_lhe_hepmc_rows(
                    lhe,
                    hepmc,
                    samples[lhe_key],
                    samples[hepmc_key],
                )
            except RuntimeError as error:
                rows, summary = _independent_comparison_rows(
                    hepmc,
                    lhe,
                    moment_results[hepmc_key],
                    moment_results[lhe_key],
                    "hepmc_minus_lhe_independent_fallback",
                )
                summary["paired_fallback_reason"] = str(error)
            comparison_rows_all.extend(rows)
            comparison_summaries.append(summary)

    pd.DataFrame(comparison_rows_all).to_csv(
        tables_dir / "paper_spin_comparison_details.csv", index=False
    )
    pd.DataFrame(comparison_summaries).to_csv(
        tables_dir / "paper_spin_comparison_summary.csv", index=False
    )

    manifest = {
        "schema_version": 1,
        "qualification_root": str(qualification_root),
        "output_root": str(output_root),
        "config_path": None if config_path is None else str(Path(config_path).resolve()),
        "samples": len(descriptors),
        "coefficient_rows": len(coefficient_records),
        "derived_rows": len(derived_records),
        "density_rows": len(density_records),
        "differential_rows": len(differential_records),
        "marginal_rows": len(marginal_records),
        "shape_rows": len(shape_records),
        "analytic_rows": len(analytic_records),
        "comparison_rows": len(comparison_rows_all),
        "comparison_groups": len(comparison_summaries),
        "convention": config["convention"],
        "baseline_modified": False,
    }
    write_json(output_root / "paper_spin_manifest.json", manifest)
    return manifest
