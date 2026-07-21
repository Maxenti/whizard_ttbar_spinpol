"""Differential spin tomography in reviewed kinematic bins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .io import AnalyzerSample
from .moments import MomentResult, estimate_moments


@dataclass(frozen=True)
class DifferentialBinResult:
    variable: str
    bin_index: int
    bin_low: float
    bin_high: float
    events: int
    moment: MomentResult
    metadata: dict[str, Any]


def first_present(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    return next((name for name in candidates if name in frame.columns), None)


def resolve_variable(
    frame: pd.DataFrame,
    variable_config: dict[str, Any],
) -> tuple[str, np.ndarray]:
    column = variable_config.get("column") or first_present(
        frame,
        list(variable_config.get("candidates", [])),
    )
    if column is None:
        raise KeyError(
            f"No column found for differential variable {variable_config.get('name')}; "
            f"available={list(frame.columns)}"
        )
    values = (
        float(variable_config.get("sign", 1.0))
        * pd.to_numeric(frame[column], errors="coerce").to_numpy(float)
    )
    return str(column), values


def estimate_differential(
    frame: pd.DataFrame,
    sample: AnalyzerSample,
    variable_config: dict[str, Any],
) -> list[DifferentialBinResult]:
    if not bool(variable_config.get("mapping_reviewed", False)):
        raise RuntimeError(
            f"Differential variable {variable_config.get('name')} mapping is not reviewed"
        )
    column, values = resolve_variable(frame, variable_config)
    edges = np.asarray(variable_config["edges"], dtype=float)
    if len(edges) < 2 or not np.all(np.diff(edges) > 0.0):
        raise ValueError("Differential bin edges must be strictly increasing")
    bin_index = np.searchsorted(edges, values, side="right") - 1
    bin_index[values == edges[-1]] = len(edges) - 2
    results: list[DifferentialBinResult] = []
    minimum_events = int(variable_config.get("minimum_events", 50))

    for index in range(len(edges) - 1):
        selected = np.isfinite(values) & (bin_index == index)
        count = int(np.count_nonzero(selected))
        if count < minimum_events:
            continue
        subset = AnalyzerSample(
            plus=sample.plus[selected],
            minus=sample.minus[selected],
            weights=sample.weights[selected],
            event_keys=None if sample.event_keys is None else sample.event_keys[selected],
            source_path=sample.source_path,
            convention_name=sample.convention_name,
            metadata={
                **sample.metadata,
                "differential_variable": variable_config["name"],
                "differential_column": column,
                "bin_index": index,
            },
        )
        results.append(
            DifferentialBinResult(
                variable=str(variable_config["name"]),
                bin_index=index,
                bin_low=float(edges[index]),
                bin_high=float(edges[index + 1]),
                events=count,
                moment=estimate_moments(subset),
                metadata={"column": column, "sign": float(variable_config.get("sign", 1.0))},
            )
        )
    return results
