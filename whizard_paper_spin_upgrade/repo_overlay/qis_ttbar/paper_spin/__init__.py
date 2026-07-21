"""Paper-grade ttbar spin-density-matrix analysis.

This package is additive.  It does not replace or mutate the validated legacy
Spin-15 qualification products.  It consumes their event-level ntuples and
creates a convention-locked, covariance-aware tomography layer.
"""

from .contracts import (
    AXES,
    COEFFICIENT_NAMES,
    LEPTON_COLLIDER_PAPER_V1,
    LEGACY_INTERNAL_V1,
    SpinConvention,
    get_convention,
)

__all__ = [
    "AXES",
    "COEFFICIENT_NAMES",
    "LEPTON_COLLIDER_PAPER_V1",
    "LEGACY_INTERNAL_V1",
    "SpinConvention",
    "get_convention",
]

__version__ = "2.0.0"
