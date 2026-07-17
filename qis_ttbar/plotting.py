from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig, base: Path, formats: Iterable[str]) -> list[str]:
    outputs = []
    for extension in formats:
        path = base.with_suffix(f".{extension}")
        fig.savefig(path, bbox_inches="tight")
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def plot_observable_overlay(
    frames: dict[str, pd.DataFrame], column: str, *, bins: int | np.ndarray = 50,
    density: bool = True, output_base: str | Path, xlabel: str | None = None,
    formats: Iterable[str] = ("png", "pdf"), title: str | None = None,
) -> list[str]:
    fig, ax = plt.subplots(figsize=(7.0, 5.2))
    for label, frame in frames.items():
        ax.hist(frame[column].to_numpy(float), bins=bins, density=density, histtype="step", linewidth=1.5, label=label)
    ax.set_xlabel(xlabel or column)
    ax.set_ylabel("Normalized events" if density else "Events")
    if title:
        ax.set_title(title)
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    return _save(fig, Path(output_base), formats)


def plot_correlation_matrix(matrix: np.ndarray, *, labels: tuple[str, str, str] = ("k", "r", "n"), output_base: str | Path, formats: Iterable[str] = ("png", "pdf"), title: str = "Spin-correlation matrix") -> list[str]:
    matrix = np.asarray(matrix, float).reshape(3, 3)
    fig, ax = plt.subplots(figsize=(5.7, 5.0))
    image = ax.imshow(matrix, vmin=-1.0, vmax=1.0, aspect="equal")
    ax.set_xticks(range(3), labels)
    ax.set_yticks(range(3), labels)
    ax.set_xlabel("Antitop axis")
    ax.set_ylabel("Top axis")
    ax.set_title(title)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{matrix[i,j]:.3f}", ha="center", va="center")
    fig.colorbar(image, ax=ax, label="Cij")
    return _save(fig, Path(output_base), formats)


def plot_density_matrix(rho: np.ndarray, *, output_base: str | Path, formats: Iterable[str] = ("png", "pdf"), title: str = "Density matrix") -> list[str]:
    rho = np.asarray(rho, complex).reshape(4, 4)
    outputs = []
    for component, matrix in (("real", rho.real), ("imag", rho.imag)):
        fig, ax = plt.subplots(figsize=(5.7, 5.0))
        limit = max(float(np.max(np.abs(matrix))), 1e-9)
        image = ax.imshow(matrix, vmin=-limit, vmax=limit, aspect="equal")
        ax.set_xticks(range(4))
        ax.set_yticks(range(4))
        ax.set_title(f"{title} ({component})")
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{matrix[i,j]:.3f}", ha="center", va="center")
        fig.colorbar(image, ax=ax)
        outputs.extend(_save(fig, Path(str(output_base) + f"_{component}"), formats))
    return outputs
