from __future__ import annotations

import dataclasses
from typing import Iterable
import numpy as np
import pandas as pd


@dataclasses.dataclass(frozen=True)
class BinSelection:
    name: str
    mask: np.ndarray
    metadata: dict[str, float | str | int]


def inclusive_selection(frame: pd.DataFrame) -> BinSelection:
    return BinSelection("inclusive", np.ones(len(frame), dtype=bool), {"dimension": 0})


def one_dimensional_bins(frame: pd.DataFrame, column: str, edges: Iterable[float]) -> list[BinSelection]:
    edges = np.asarray(list(edges), dtype=float)
    values = frame[column].to_numpy(float)
    output = []
    for i in range(len(edges) - 1):
        lo, hi = float(edges[i]), float(edges[i + 1])
        mask = (values >= lo) & (values < hi)
        output.append(BinSelection(f"{column}_{i:03d}", mask, {"dimension": 1, "column": column, "low": lo, "high": hi}))
    return output


def two_dimensional_bins(
    frame: pd.DataFrame,
    x_column: str,
    x_edges: Iterable[float],
    y_column: str,
    y_edges: Iterable[float],
) -> list[BinSelection]:
    x_edges, y_edges = np.asarray(list(x_edges), float), np.asarray(list(y_edges), float)
    x, y = frame[x_column].to_numpy(float), frame[y_column].to_numpy(float)
    output = []
    for ix in range(len(x_edges) - 1):
        for iy in range(len(y_edges) - 1):
            mask = (x >= x_edges[ix]) & (x < x_edges[ix + 1]) & (y >= y_edges[iy]) & (y < y_edges[iy + 1])
            output.append(BinSelection(
                f"{x_column}_{ix:03d}__{y_column}_{iy:03d}", mask,
                {"dimension": 2, "x_column": x_column, "x_low": float(x_edges[ix]), "x_high": float(x_edges[ix+1]),
                 "y_column": y_column, "y_low": float(y_edges[iy]), "y_high": float(y_edges[iy+1])},
            ))
    return output
