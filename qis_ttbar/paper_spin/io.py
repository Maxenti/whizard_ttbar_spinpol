"""Configuration, ntuple discovery, and analyzer-source adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml

from .basis import (
    boost_four_vectors,
    reconstruct_from_frame,
    unit,
)
from .contracts import SpinConvention, get_convention


@dataclass(frozen=True)
class AnalyzerSample:
    plus: np.ndarray
    minus: np.ndarray
    weights: np.ndarray
    event_keys: np.ndarray | None
    source_path: Path
    convention_name: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SampleDescriptor:
    dataset: str
    sample_id: str
    initial_state: str
    decay_channel: str
    polarization: str
    spin_mode: str
    stage: str
    source_path: Path


DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "convention": {
        "name": "lepton_collider_paper_v1",

        # Backward-compatible default. Existing callers using
        # load_config(None) continue to exercise the frozen legacy adapter.
        "analyzer_source": "legacy_columns",

        # Legacy stored-column adapter.
        "legacy_map_reviewed": True,
        "plus_columns": ["b1k", "b1r", "b1n"],
        "minus_columns": ["b2k", "b2r", "b2n"],
        "plus_component_transform": np.eye(3).tolist(),
        "minus_component_transform": np.eye(3).tolist(),
        "raw_plus_sign": 1.0,
        "raw_minus_sign": -1.0,

        # Canonical publication analyzer reconstruction.
        "four_vector_reconstruction_reviewed": False,
        "four_vectors": {},

        # Optional canonical production kinematics derived from the same
        # four-vectors and incoming-positive-lepton convention used by the
        # publication analyzer reconstruction.
        "derived_kinematics": {
            "enabled": False,
            "reviewed": False,
            "costheta_column": "paper_cos_theta_t",
            "overwrite_existing": False,
            "comparison_tolerance": 1.0e-12,
            "bound_tolerance": 1.0e-12,
        },

        "singular_tolerance": 1.0e-10,
        "singular_policy": "error",
        "max_orthonormal_residual": 1.0e-10,
        "max_handedness_deviation": 1.0e-10,

        # Common analyzer checks.
        "max_norm_deviation": 1.0e-6,
        "renormalize_within_tolerance": False,
    },
    "weights": {
        "candidates": ["weight", "event_weight", "nominal_weight"],
        "allow_negative": False,
    },
    "event_key_candidates": [
        "event_id",
        "event",
        "event_number",
        "event_index",
        "source_event_index",
    ],
}


def deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_config(
    path: str | Path | None,
) -> dict[str, Any]:
    if path is None:
        return DEFAULT_CONFIG

    source = Path(path)
    loaded = yaml.safe_load(source.read_text()) or {}
    config = deep_merge(DEFAULT_CONFIG, loaded)

    if int(config.get("schema_version", -1)) != 1:
        raise ValueError(
            "Unsupported paper-spin config schema "
            f"{config.get('schema_version')!r}"
        )

    return config


def discover_ntuples(
    qualification_root: str | Path,
) -> list[SampleDescriptor]:
    root = Path(qualification_root)
    ntuple_root = root / "ntuples"

    if not ntuple_root.is_dir():
        raise FileNotFoundError(
            f"Missing ntuple directory: {ntuple_root}"
        )

    descriptors: list[SampleDescriptor] = []

    for source in sorted(ntuple_root.glob("*/*.parquet")):
        dataset = source.parent.name
        sample_id = source.stem
        parts = sample_id.split("_")

        if len(parts) < 7:
            raise ValueError(
                f"Cannot parse sample ID: {sample_id}"
            )

        initial_state = parts[0]

        decay_channel = next(
            (
                part
                for part in parts
                if part in {"epmum", "mupem"}
            ),
            "unknown",
        )

        polarization = next(
            (
                part
                for part in parts
                if part
                in {
                    "LR100",
                    "RL100",
                    "LL100",
                    "RR100",
                }
            ),
            "unknown",
        )

        spin_mode = (
            "sc"
            if "_sc_" in f"_{sample_id}_"
            else "iso"
        )

        stage = (
            "hepmc"
            if dataset.startswith("hepmc")
            else "lhe"
        )

        descriptors.append(
            SampleDescriptor(
                dataset=dataset,
                sample_id=sample_id,
                initial_state=initial_state,
                decay_channel=decay_channel,
                polarization=polarization,
                spin_mode=spin_mode,
                stage=stage,
                source_path=source,
            )
        )

    if not descriptors:
        raise FileNotFoundError(
            f"No Parquet ntuples found under {ntuple_root}"
        )

    return descriptors


def _first_present(
    frame: pd.DataFrame,
    names: Iterable[str],
) -> str | None:
    for name in names:
        if name in frame.columns:
            return name

    return None


def _validate_component_transform(
    value: Any,
    label: str,
) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)

    if matrix.shape != (3, 3):
        raise ValueError(
            f"{label} must have shape (3,3), "
            f"got {matrix.shape}"
        )

    gram = matrix @ matrix.T

    if not np.allclose(
        gram,
        np.eye(3),
        atol=1.0e-12,
        rtol=0.0,
    ):
        raise ValueError(
            f"{label} is not orthogonal: "
            f"matrix*matrix^T={gram}"
        )

    return matrix


def _legacy_column_analyzers(
    frame: pd.DataFrame,
    source_path: str | Path,
    convention_config: dict[str, Any],
    convention: SpinConvention,
) -> tuple[
    np.ndarray,
    np.ndarray,
    dict[str, Any],
]:
    if not bool(
        convention_config.get(
            "legacy_map_reviewed",
            False,
        )
    ):
        raise RuntimeError(
            "Refusing to assign publication convention "
            "from legacy analyzer columns: "
            "convention.legacy_map_reviewed is false. "
            "Either review the legacy map explicitly or "
            "select convention.analyzer_source=four_vectors."
        )

    plus_columns = list(
        convention_config["plus_columns"]
    )
    minus_columns = list(
        convention_config["minus_columns"]
    )

    missing = [
        column
        for column in plus_columns + minus_columns
        if column not in frame.columns
    ]

    if missing:
        raise KeyError(
            f"Missing required analyzer columns {missing} "
            f"in {source_path}; available columns: "
            f"{list(frame.columns)}"
        )

    plus_raw = frame[
        plus_columns
    ].to_numpy(dtype=float)

    minus_raw = frame[
        minus_columns
    ].to_numpy(dtype=float)

    if (
        not np.all(np.isfinite(plus_raw))
        or not np.all(np.isfinite(minus_raw))
    ):
        raise ValueError(
            "Non-finite legacy analyzer entries "
            f"in {source_path}"
        )

    plus_transform = _validate_component_transform(
        convention_config[
            "plus_component_transform"
        ],
        "plus_component_transform",
    )

    minus_transform = _validate_component_transform(
        convention_config[
            "minus_component_transform"
        ],
        "minus_component_transform",
    )

    plus_sign = float(
        convention_config.get(
            "raw_plus_sign",
            convention.plus_analyzer_sign,
        )
    )

    minus_sign = float(
        convention_config.get(
            "raw_minus_sign",
            convention.minus_analyzer_sign,
        )
    )

    plus = (
        plus_sign
        * plus_raw
        @ plus_transform.T
    )

    minus = (
        minus_sign
        * minus_raw
        @ minus_transform.T
    )

    return (
        plus,
        minus,
        {
            "analyzer_source": "legacy_columns",
            "plus_columns": plus_columns,
            "minus_columns": minus_columns,
            "plus_component_transform":
                plus_transform.tolist(),
            "minus_component_transform":
                minus_transform.tolist(),
            "raw_plus_sign": plus_sign,
            "raw_minus_sign": minus_sign,
            "legacy_map_reviewed": True,
        },
    )



def _mapped_four_vector(
    frame: pd.DataFrame,
    mapping: dict[str, dict[str, str]],
    name: str,
    source_path: str | Path,
) -> np.ndarray:
    """Read one mapped (E,px,py,pz) four-vector array."""

    if name not in mapping:
        raise KeyError(
            f"Missing four-vector mapping {name!r} "
            f"for {source_path}"
        )

    component_mapping = mapping[name]

    if not isinstance(component_mapping, dict):
        raise TypeError(
            f"Four-vector mapping {name!r} must be a dictionary"
        )

    required_components = ("e", "px", "py", "pz")

    missing_components = [
        component
        for component in required_components
        if component not in component_mapping
    ]

    if missing_components:
        raise KeyError(
            f"Four-vector mapping {name!r} is missing components "
            f"{missing_components}"
        )

    columns = [
        str(component_mapping[component])
        for component in required_components
    ]

    missing_columns = [
        column
        for column in columns
        if column not in frame.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing four-vector columns {missing_columns} "
            f"for mapping {name!r} in {source_path}"
        )

    vectors = frame[columns].to_numpy(dtype=float)

    if vectors.shape != (len(frame), 4):
        raise ValueError(
            f"Expected mapped four-vector shape {(len(frame), 4)} "
            f"for {name!r}, got {vectors.shape}"
        )

    if not np.all(np.isfinite(vectors)):
        raise ValueError(
            f"Non-finite mapped four-vector values for {name!r} "
            f"in {source_path}"
        )

    return vectors


def _canonical_positive_beam_costheta(
    frame: pd.DataFrame,
    mapping: dict[str, dict[str, str]],
    source_path: str | Path,
    bound_tolerance: float,
) -> np.ndarray:
    """Calculate the canonical positive-beam top production angle.

    The definition is

        cos(theta_t,+) =
            unit(p_top in the ttbar ZMF)
            dot
            unit(p_positive-incoming-lepton in the ttbar ZMF).

    This is deliberately reconstructed from four-vectors rather than inferred
    from the frozen negative-beam ``cos_theta_t`` column.
    """

    incoming_positive = _mapped_four_vector(
        frame,
        mapping,
        "incoming_positive",
        source_path,
    )

    top = _mapped_four_vector(
        frame,
        mapping,
        "top",
        source_path,
    )

    antitop = _mapped_four_vector(
        frame,
        mapping,
        "antitop",
        source_path,
    )

    ttbar = top + antitop

    if np.any(ttbar[:, 0] <= 0.0):
        raise ValueError(
            f"Non-positive ttbar energy encountered in {source_path}"
        )

    ttbar_beta = (
        ttbar[:, 1:]
        / ttbar[:, 0, None]
    )

    incoming_positive_ttbar = boost_four_vectors(
        incoming_positive,
        -ttbar_beta,
    )

    top_ttbar = boost_four_vectors(
        top,
        -ttbar_beta,
    )

    incoming_positive_hat = unit(
        incoming_positive_ttbar[:, 1:]
    )

    top_hat = unit(
        top_ttbar[:, 1:]
    )

    costheta = np.einsum(
        "ni,ni->n",
        incoming_positive_hat,
        top_hat,
    )

    if not np.all(np.isfinite(costheta)):
        raise ValueError(
            f"Non-finite canonical cos(theta) values in {source_path}"
        )

    maximum_absolute_value = float(
        np.max(
            np.abs(costheta),
            initial=0.0,
        )
    )

    if maximum_absolute_value > 1.0 + bound_tolerance:
        raise ValueError(
            "Canonical cos(theta) exceeds physical bounds in "
            f"{source_path}: max |cos(theta)|="
            f"{maximum_absolute_value:.16g}"
        )

    # Remove only floating-point excursions beyond [-1,1].
    return np.clip(
        costheta,
        -1.0,
        1.0,
    )


def _attach_canonical_kinematics(
    frame: pd.DataFrame,
    source_path: str | Path,
    convention_config: dict[str, Any],
    mapping: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Attach reviewed canonical production variables to ``frame``.

    The input DataFrame is intentionally updated in place so that the same
    derived column is used by differential binning, event-conditioned analytic
    comparisons, and any later frame-level diagnostics.
    """

    derived_config = convention_config.get(
        "derived_kinematics",
        {},
    )

    if not bool(
        derived_config.get(
            "enabled",
            False,
        )
    ):
        return {
            "derived_kinematics_enabled": False,
        }

    if not bool(
        derived_config.get(
            "reviewed",
            False,
        )
    ):
        raise RuntimeError(
            "Refusing to attach canonical production kinematics: "
            "convention.derived_kinematics.reviewed is false."
        )

    column = str(
        derived_config.get(
            "costheta_column",
            "paper_cos_theta_t",
        )
    ).strip()

    if not column:
        raise ValueError(
            "convention.derived_kinematics.costheta_column "
            "must be non-empty"
        )

    comparison_tolerance = float(
        derived_config.get(
            "comparison_tolerance",
            1.0e-12,
        )
    )

    bound_tolerance = float(
        derived_config.get(
            "bound_tolerance",
            1.0e-12,
        )
    )

    overwrite_existing = bool(
        derived_config.get(
            "overwrite_existing",
            False,
        )
    )

    costheta = _canonical_positive_beam_costheta(
        frame,
        mapping,
        source_path,
        bound_tolerance,
    )

    action = "created"
    maximum_existing_residual = 0.0

    if column in frame.columns:
        existing = pd.to_numeric(
            frame[column],
            errors="coerce",
        ).to_numpy(dtype=float)

        existing_is_finite = bool(
            np.all(
                np.isfinite(existing)
            )
        )

        if existing_is_finite:
            maximum_existing_residual = float(
                np.max(
                    np.abs(
                        existing
                        - costheta
                    ),
                    initial=0.0,
                )
            )
        else:
            maximum_existing_residual = float("inf")

        if (
            existing_is_finite
            and maximum_existing_residual
            <= comparison_tolerance
        ):
            action = "validated_existing"

        elif not overwrite_existing:
            raise ValueError(
                f"Derived kinematic column {column!r} already exists "
                f"in {source_path} and disagrees with canonical "
                "four-vector reconstruction: max residual="
                f"{maximum_existing_residual:.6e}. "
                "Refusing to overwrite it."
            )

        else:
            frame.loc[:, column] = costheta
            action = "overwritten"

    else:
        frame.loc[:, column] = costheta

    attached = pd.to_numeric(
        frame[column],
        errors="coerce",
    ).to_numpy(dtype=float)

    if not np.all(np.isfinite(attached)):
        raise ValueError(
            f"Attached canonical kinematic column {column!r} "
            f"contains non-finite values in {source_path}"
        )

    return {
        "derived_kinematics_enabled": True,
        "derived_kinematics_reviewed": True,
        "derived_costheta_column": column,
        "derived_costheta_definition":
            "dot(unit(top_ttbar),unit(incoming_positive_ttbar))",
        "derived_costheta_beam_reference":
            "incoming_positive_lepton",
        "derived_costheta_frame":
            "ttbar_zero_momentum_frame",
        "derived_costheta_action": action,
        "derived_costheta_min":
            float(np.min(attached)),
        "derived_costheta_max":
            float(np.max(attached)),
        "derived_costheta_max_existing_residual":
            maximum_existing_residual,
        "derived_costheta_comparison_tolerance":
            comparison_tolerance,
        "derived_costheta_bound_tolerance":
            bound_tolerance,
    }

def _four_vector_analyzers(
    frame: pd.DataFrame,
    source_path: str | Path,
    convention_config: dict[str, Any],
) -> tuple[
    np.ndarray,
    np.ndarray,
    dict[str, Any],
]:
    if not bool(
        convention_config.get(
            "four_vector_reconstruction_reviewed",
            False,
        )
    ):
        raise RuntimeError(
            "Refusing to assign publication convention "
            "from four-vectors: "
            "convention."
            "four_vector_reconstruction_reviewed "
            "is false."
        )

    mapping = convention_config.get(
        "four_vectors"
    )

    if (
        not isinstance(mapping, dict)
        or not mapping
    ):
        raise ValueError(
            "convention.four_vectors must define "
            "incoming_positive, top, antitop, "
            "lepton_positive, and lepton_negative "
            "four-vector mappings."
        )

    singular_tolerance = float(
        convention_config.get(
            "singular_tolerance",
            1.0e-10,
        )
    )

    result = reconstruct_from_frame(
        frame,
        mapping,
        singular_tolerance=singular_tolerance,
    )

    derived_kinematics_metadata = _attach_canonical_kinematics(
        frame,
        source_path,
        convention_config,
        mapping,
    )

    singular_events = int(
        np.count_nonzero(
            result.singular
        )
    )

    singular_policy = str(
        convention_config.get(
            "singular_policy",
            "error",
        )
    ).strip().lower()

    if singular_policy != "error":
        raise ValueError(
            "Only convention.singular_policy=error "
            "is currently supported. Dropping rows "
            "requires synchronized filtering of the "
            "analysis frame and every differential "
            "observable."
        )

    if singular_events:
        raise ValueError(
            "Canonical four-vector reconstruction "
            f"found {singular_events} singular k,r,n "
            f"events in {source_path} at tolerance "
            f"{singular_tolerance:.6g}."
        )

    max_orthonormal_residual = float(
        np.max(
            result.orthonormal_residual,
            initial=0.0,
        )
    )

    orthonormal_limit = float(
        convention_config.get(
            "max_orthonormal_residual",
            1.0e-10,
        )
    )

    if (
        max_orthonormal_residual
        > orthonormal_limit
    ):
        raise ValueError(
            "Canonical basis orthonormality failed "
            f"in {source_path}: max residual="
            f"{max_orthonormal_residual:.6g} > "
            f"{orthonormal_limit:.6g}"
        )

    expected_handedness = float(
        result.metadata.get(
            "expected_labelled_handedness",
            -1.0,
        )
    )

    max_handedness_deviation = float(
        np.max(
            np.abs(
                result.handedness
                - expected_handedness
            ),
            initial=0.0,
        )
    )

    handedness_limit = float(
        convention_config.get(
            "max_handedness_deviation",
            1.0e-10,
        )
    )

    if (
        max_handedness_deviation
        > handedness_limit
    ):
        raise ValueError(
            "Canonical basis handedness failed "
            f"in {source_path}: max deviation="
            f"{max_handedness_deviation:.6g} > "
            f"{handedness_limit:.6g}"
        )

    return (
        result.plus,
        result.minus,
        {
            "analyzer_source": "four_vectors",
            "four_vectors": mapping,
            "four_vector_reconstruction_reviewed":
                True,
            "singular_tolerance":
                singular_tolerance,
            "singular_policy":
                singular_policy,
            "singular_events":
                singular_events,
            "max_orthonormal_residual":
                max_orthonormal_residual,
            "handedness_min":
                float(
                    np.min(
                        result.handedness
                    )
                ),
            "handedness_max":
                float(
                    np.max(
                        result.handedness
                    )
                ),
            "max_handedness_deviation":
                max_handedness_deviation,
            "basis_metadata":
                result.metadata,
            **derived_kinematics_metadata,
        },
    )


def _validate_analyzer_vectors(
    plus: np.ndarray,
    minus: np.ndarray,
    source_path: str | Path,
    convention_config: dict[str, Any],
    expected_events: int,
) -> tuple[
    np.ndarray,
    np.ndarray,
    float,
]:
    plus = np.asarray(
        plus,
        dtype=float,
    )

    minus = np.asarray(
        minus,
        dtype=float,
    )

    expected_shape = (
        expected_events,
        3,
    )

    if (
        plus.shape != expected_shape
        or minus.shape != expected_shape
    ):
        raise ValueError(
            f"Expected analyzer shape "
            f"{expected_shape} in {source_path}, "
            f"got plus={plus.shape}, "
            f"minus={minus.shape}"
        )

    if (
        not np.all(np.isfinite(plus))
        or not np.all(np.isfinite(minus))
    ):
        raise ValueError(
            "Non-finite analyzer entries "
            f"in {source_path}"
        )

    plus_norm = np.linalg.norm(
        plus,
        axis=1,
    )

    minus_norm = np.linalg.norm(
        minus,
        axis=1,
    )

    max_deviation = float(
        convention_config.get(
            "max_norm_deviation",
            1.0e-6,
        )
    )

    plus_deviation = np.abs(
        plus_norm - 1.0
    )

    minus_deviation = np.abs(
        minus_norm - 1.0
    )

    worst = float(
        max(
            plus_deviation.max(
                initial=0.0
            ),
            minus_deviation.max(
                initial=0.0
            ),
        )
    )

    if worst > max_deviation:
        raise ValueError(
            "Analyzer vectors are not unit length "
            f"in {source_path}: max |norm-1|="
            f"{worst:.6g} > {max_deviation:.6g}"
        )

    if bool(
        convention_config.get(
            "renormalize_within_tolerance",
            False,
        )
    ):
        if (
            np.any(plus_norm <= 0.0)
            or np.any(minus_norm <= 0.0)
        ):
            raise ValueError(
                "Cannot renormalize zero analyzer "
                f"vector in {source_path}"
            )

        plus = (
            plus
            / plus_norm[:, None]
        )

        minus = (
            minus
            / minus_norm[:, None]
        )

    return plus, minus, worst


def _weights_and_event_keys(
    frame: pd.DataFrame,
    source_path: str | Path,
    config: dict[str, Any],
) -> tuple[
    np.ndarray,
    np.ndarray | None,
    str | None,
    str | None,
]:
    weight_name = _first_present(
        frame,
        config["weights"]["candidates"],
    )

    if weight_name is None:
        weights = np.ones(
            len(frame),
            dtype=float,
        )
    else:
        weights = pd.to_numeric(
            frame[weight_name],
            errors="coerce",
        ).to_numpy(dtype=float)

        if not np.all(
            np.isfinite(weights)
        ):
            raise ValueError(
                f"Non-finite weights in "
                f"{source_path} column "
                f"{weight_name}"
            )

    if (
        not bool(
            config["weights"].get(
                "allow_negative",
                False,
            )
        )
        and np.any(weights < 0)
    ):
        raise ValueError(
            f"Negative weights found in "
            f"{source_path}; enable "
            "weights.allow_negative only after "
            "validating the covariance treatment "
            "for signed weights."
        )

    if np.sum(weights) <= 0:
        raise ValueError(
            "Non-positive total event weight "
            f"in {source_path}"
        )

    event_key_name = _first_present(
        frame,
        config[
            "event_key_candidates"
        ],
    )

    event_keys = (
        None
        if event_key_name is None
        else frame[
            event_key_name
        ].to_numpy()
    )

    return (
        weights,
        event_keys,
        weight_name,
        event_key_name,
    )


def frame_to_analyzers(
    frame: pd.DataFrame,
    source_path: str | Path,
    config: dict[str, Any],
) -> AnalyzerSample:
    convention_config = config[
        "convention"
    ]

    convention: SpinConvention = (
        get_convention(
            str(
                convention_config[
                    "name"
                ]
            )
        )
    )

    analyzer_source = str(
        convention_config.get(
            "analyzer_source",
            "legacy_columns",
        )
    ).strip().lower()

    if analyzer_source == "legacy_columns":
        (
            plus,
            minus,
            source_metadata,
        ) = _legacy_column_analyzers(
            frame,
            source_path,
            convention_config,
            convention,
        )

    elif analyzer_source == "four_vectors":
        (
            plus,
            minus,
            source_metadata,
        ) = _four_vector_analyzers(
            frame,
            source_path,
            convention_config,
        )

    else:
        raise ValueError(
            "Unsupported "
            "convention.analyzer_source "
            f"{analyzer_source!r}; expected "
            "'legacy_columns' or 'four_vectors'."
        )

    plus, minus, worst = (
        _validate_analyzer_vectors(
            plus,
            minus,
            source_path,
            convention_config,
            len(frame),
        )
    )

    (
        weights,
        event_keys,
        weight_name,
        event_key_name,
    ) = _weights_and_event_keys(
        frame,
        source_path,
        config,
    )

    return AnalyzerSample(
        plus=plus,
        minus=minus,
        weights=weights,
        event_keys=event_keys,
        source_path=Path(source_path),
        convention_name=convention.name,
        metadata={
            **source_metadata,
            "weight_column":
                weight_name,
            "event_key_column":
                event_key_name,
            "max_norm_deviation_observed":
                worst,
            "events":
                int(len(frame)),
        },
    )


def load_analyzer_sample(
    source_path: str | Path,
    config: dict[str, Any],
) -> AnalyzerSample:
    source = Path(source_path)
    frame = pd.read_parquet(source)

    return frame_to_analyzers(
        frame,
        source,
        config,
    )
