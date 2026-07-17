from __future__ import annotations

import dataclasses
import numpy as np
from scipy.interpolate import RegularGridInterpolator


@dataclasses.dataclass
class DifferentialReweighter:
    axes: tuple[np.ndarray, ...]
    values: np.ndarray
    bounds_error: bool = False
    fill_value: float | None = None

    def __post_init__(self) -> None:
        self._interpolator = RegularGridInterpolator(
            self.axes, np.asarray(self.values, float), bounds_error=self.bounds_error, fill_value=self.fill_value
        )

    def weights(self, coordinates: np.ndarray) -> np.ndarray:
        return np.asarray(self._interpolator(np.asarray(coordinates, float)), float)
