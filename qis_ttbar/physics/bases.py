from __future__ import annotations

import dataclasses
import numpy as np

from ..models import FourVector


@dataclasses.dataclass(frozen=True)
class SpinBasis:
    """Right-handed top and antitop spin bases in the ttbar rest frame.

    Columns are stored in the requested order. The default order is (k,r,n).
    For the antitop, kbar=-k, nbar=n, and rbar=nbar x kbar.
    """

    order: tuple[str, str, str]
    top_axes: np.ndarray
    antitop_axes: np.ndarray

    def axis(self, particle: str, name: str) -> np.ndarray:
        idx = self.order.index(name)
        matrix = self.top_axes if particle == "top" else self.antitop_axes
        return matrix[:, idx]


def _unit(vector: np.ndarray, *, atol: float = 1e-12) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= atol:
        raise ValueError("degenerate spin basis vector")
    return vector / norm


def build_krn_basis(
    beam_minus_tt: FourVector,
    top_tt: FourVector,
    antitop_tt: FourVector,
    *,
    order: tuple[str, str, str] = ("k", "r", "n"),
) -> SpinBasis:
    if sorted(order) != ["k", "n", "r"]:
        raise ValueError("order must contain k,r,n")
    k = _unit(top_tt.spatial)
    beam = _unit(beam_minus_tt.spatial)
    normal_raw = np.cross(beam, k)
    if np.linalg.norm(normal_raw) < 1e-10:
        # At exactly forward/backward production the normal is undefined.
        # Choose a deterministic transverse reference orthogonal to k.
        reference = np.array([1.0, 0.0, 0.0])
        if abs(float(np.dot(reference, k))) > 0.9:
            reference = np.array([0.0, 1.0, 0.0])
        normal_raw = np.cross(reference, k)
    n = _unit(normal_raw)
    r = _unit(np.cross(n, k))

    kbar = _unit(antitop_tt.spatial)
    nbar = n.copy()
    rbar = _unit(np.cross(nbar, kbar))
    named_top = {"k": k, "r": r, "n": n}
    named_bar = {"k": kbar, "r": rbar, "n": nbar}
    top_axes = np.column_stack([named_top[name] for name in order])
    antitop_axes = np.column_stack([named_bar[name] for name in order])
    if not np.allclose(top_axes.T @ top_axes, np.eye(3), atol=1e-10):
        raise ValueError("top basis is not orthonormal")
    if np.linalg.det(top_axes) < 0.0:
        raise ValueError("top basis is not right-handed")
    if not np.allclose(antitop_axes.T @ antitop_axes, np.eye(3), atol=1e-10):
        raise ValueError("antitop basis is not orthonormal")
    return SpinBasis(order=order, top_axes=top_axes, antitop_axes=antitop_axes)


def rotation_from_bases(source: SpinBasis, target: SpinBasis, particle: str = "top") -> np.ndarray:
    a = source.top_axes if particle == "top" else source.antitop_axes
    b = target.top_axes if particle == "top" else target.antitop_axes
    return b.T @ a


def rotate_coefficients(
    b_plus: np.ndarray,
    b_minus: np.ndarray,
    correlation: np.ndarray,
    rotation_top: np.ndarray,
    rotation_antitop: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        rotation_top @ np.asarray(b_plus),
        rotation_antitop @ np.asarray(b_minus),
        rotation_top @ np.asarray(correlation) @ rotation_antitop.T,
    )
