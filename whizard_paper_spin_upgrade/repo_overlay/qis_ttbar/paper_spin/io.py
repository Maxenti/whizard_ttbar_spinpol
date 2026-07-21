"""Configuration, ntuple discovery, and legacy-to-canonical adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml

from .contracts import AXES, SpinConvention, get_convention


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
        "legacy_map_reviewed": True,
        "plus_columns": ["b1k", "b1r", "b1n"],
        "minus_columns": ["b2k", "b2r", "b2n"],
        "plus_component_transform": np.eye(3).tolist(),
        "minus_component_transform": np.eye(3).tolist(),
        "raw_plus_sign": 1.0,
        "raw_minus_sign": -1.0,
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
        "source_event_index",
    ],
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
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


def load_config(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return DEFAULT_CONFIG
    source = Path(path)
    loaded = yaml.safe_load(source.read_text()) or {}
    config = deep_merge(DEFAULT_CONFIG, loaded)
    if int(config.get("schema_version", -1)) != 1:
        raise ValueError(
            f"Unsupported paper-spin config schema {config.get('schema_version')!r}"
        )
    return config


def discover_ntuples(qualification_root: str | Path) -> list[SampleDescriptor]:
    root = Path(qualification_root)
    ntuple_root = root / "ntuples"
    if not ntuple_root.is_dir():
        raise FileNotFoundError(f"Missing ntuple directory: {ntuple_root}")

    descriptors: list[SampleDescriptor] = []
    for source in sorted(ntuple_root.glob("*/*.parquet")):
        dataset = source.parent.name
        sample_id = source.stem
        parts = sample_id.split("_")
        if len(parts) < 7:
            raise ValueError(f"Cannot parse sample ID: {sample_id}")
        initial_state = parts[0]
        decay_channel = next(
            (part for part in parts if part in {"epmum", "mupem"}),
            "unknown",
        )
        polarization = next(
            (part for part in parts if part in {"LR100", "RL100", "LL100", "RR100"}),
            "unknown",
        )
        spin_mode = "sc" if "_sc_" in f"_{sample_id}_" else "iso"
        stage = "hepmc" if dataset.startswith("hepmc") else "lhe"
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
        raise FileNotFoundError(f"No Parquet ntuples found under {ntuple_root}")
    return descriptors


def _first_present(frame: pd.DataFrame, names: Iterable[str]) -> str | None:
    for name in names:
        if name in frame.columns:
            return name
    return None


def _validate_component_transform(value: Any, label: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError(f"{label} must have shape (3,3), got {matrix.shape}")
    gram = matrix @ matrix.T
    if not np.allclose(gram, np.eye(3), atol=1.0e-12, rtol=0.0):
        raise ValueError(f"{label} is not orthogonal: matrix*matrix^T={gram}")
    return matrix


def frame_to_analyzers(
    frame: pd.DataFrame,
    source_path: str | Path,
    config: dict[str, Any],
) -> AnalyzerSample:
    convention_config = config["convention"]
    if not bool(convention_config.get("legacy_map_reviewed", False)):
        raise RuntimeError(
            "Refusing to assign publication convention: convention.legacy_map_reviewed "
            "is false. Review docs/qis/spin_convention.md and set it true explicitly."
        )

    convention: SpinConvention = get_convention(str(convention_config["name"]))
    plus_columns = list(convention_config["plus_columns"])
    minus_columns = list(convention_config["minus_columns"])
    missing = [
        column
        for column in plus_columns + minus_columns
        if column not in frame.columns
    ]
    if missing:
        raise KeyError(
            f"Missing required analyzer columns {missing} in {source_path}; "
            f"available columns: {list(frame.columns)}"
        )

    plus_raw = frame[plus_columns].to_numpy(dtype=float)
    minus_raw = frame[minus_columns].to_numpy(dtype=float)
    if not np.all(np.isfinite(plus_raw)) or not np.all(np.isfinite(minus_raw)):
        raise ValueError(f"Non-finite analyzer entries in {source_path}")

    plus_transform = _validate_component_transform(
        convention_config["plus_component_transform"],
        "plus_component_transform",
    )
    minus_transform = _validate_component_transform(
        convention_config["minus_component_transform"],
        "minus_component_transform",
    )

    plus = (
        float(convention_config.get("raw_plus_sign", convention.plus_analyzer_sign))
        * plus_raw
        @ plus_transform.T
    )
    minus = (
        float(convention_config.get("raw_minus_sign", convention.minus_analyzer_sign))
        * minus_raw
        @ minus_transform.T
    )

    plus_norm = np.linalg.norm(plus, axis=1)
    minus_norm = np.linalg.norm(minus, axis=1)
    max_deviation = float(convention_config.get("max_norm_deviation", 1.0e-6))
    plus_dev = np.abs(plus_norm - 1.0)
    minus_dev = np.abs(minus_norm - 1.0)
    worst = float(max(plus_dev.max(initial=0.0), minus_dev.max(initial=0.0)))
    if worst > max_deviation:
        raise ValueError(
            f"Analyzer vectors are not unit length in {source_path}: "
            f"max |norm-1|={worst:.6g} > {max_deviation:.6g}"
        )
    if bool(convention_config.get("renormalize_within_tolerance", False)):
        plus = plus / plus_norm[:, None]
        minus = minus / minus_norm[:, None]

    weight_name = _first_present(frame, config["weights"]["candidates"])
    if weight_name is None:
        weights = np.ones(len(frame), dtype=float)
    else:
        weights = pd.to_numeric(frame[weight_name], errors="coerce").to_numpy(dtype=float)
        if not np.all(np.isfinite(weights)):
            raise ValueError(f"Non-finite weights in {source_path} column {weight_name}")
    if not bool(config["weights"].get("allow_negative", False)) and np.any(weights < 0):
        raise ValueError(
            f"Negative weights found in {source_path}; enable weights.allow_negative only "
            "after validating the covariance treatment for signed weights."
        )
    if np.sum(weights) <= 0:
        raise ValueError(f"Non-positive total event weight in {source_path}")

    event_key_name = _first_present(frame, config["event_key_candidates"])
    event_keys = None if event_key_name is None else frame[event_key_name].to_numpy()

    return AnalyzerSample(
        plus=plus,
        minus=minus,
        weights=weights,
        event_keys=event_keys,
        source_path=Path(source_path),
        convention_name=convention.name,
        metadata={
            "plus_columns": plus_columns,
            "minus_columns": minus_columns,
            "weight_column": weight_name,
            "event_key_column": event_key_name,
            "max_norm_deviation_observed": worst,
            "events": int(len(frame)),
        },
    )


def load_analyzer_sample(
    source_path: str | Path,
    config: dict[str, Any],
) -> AnalyzerSample:
    source = Path(source_path)
    frame = pd.read_parquet(source)
    return frame_to_analyzers(frame, source, config)
