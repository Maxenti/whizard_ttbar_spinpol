from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Callable

import numpy as np

from .qis.measures import all_measures
from .tomography.density import density_matrix_from_coefficients, project_density_matrix, validate_density_matrix


@dataclasses.dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    value: object
    detail: str


def synthetic_states() -> dict[str, np.ndarray]:
    zero = np.array([1, 0, 0, 0], complex)
    one_one = np.array([0, 0, 0, 1], complex)
    singlet = np.array([0, 1, -1, 0], complex) / np.sqrt(2)
    phi_plus = np.array([1, 0, 0, 1], complex) / np.sqrt(2)
    return {
        "00": np.outer(zero, zero.conj()),
        "11": np.outer(one_one, one_one.conj()),
        "singlet": np.outer(singlet, singlet.conj()),
        "phi_plus": np.outer(phi_plus, phi_plus.conj()),
        "maximally_mixed": np.eye(4, dtype=complex) / 4.0,
    }


def validate_synthetic_states() -> list[Check]:
    states = synthetic_states()
    checks: list[Check] = []
    for name, rho in states.items():
        validation = validate_density_matrix(rho)
        checks.append(Check(f"{name}.density_valid", validation.valid, validation.minimum_eigenvalue, "PSD trace-one Hermitian"))
    singlet = all_measures(states["singlet"])
    checks += [
        Check("singlet.concurrence", abs(float(singlet["concurrence"]) - 1.0) < 1e-10, singlet["concurrence"], "expected 1"),
        Check("singlet.negativity", abs(float(singlet["negativity"]) - 0.5) < 1e-10, singlet["negativity"], "expected 0.5"),
        Check("singlet.chsh", abs(float(singlet["chsh_max"]) - 2 * np.sqrt(2)) < 1e-10, singlet["chsh_max"], "expected 2sqrt2"),
    ]
    mixed = all_measures(states["maximally_mixed"])
    checks += [
        Check("mixed.purity", abs(float(mixed["purity"]) - 0.25) < 1e-10, mixed["purity"], "expected 0.25"),
        Check("mixed.concurrence", abs(float(mixed["concurrence"])) < 1e-10, mixed["concurrence"], "expected 0"),
    ]
    raw = density_matrix_from_coefficients(np.array([2, 0, 0]), np.zeros(3), np.zeros((3, 3)))
    projected = project_density_matrix(raw)
    checks.append(Check("projection.physical", validate_density_matrix(projected).valid, validate_density_matrix(projected).minimum_eigenvalue, "projected matrix physical"))
    return checks


def write_validation(checks: list[Check], output_base: str | Path) -> int:
    base = Path(output_base)
    base.parent.mkdir(parents=True, exist_ok=True)
    payload = [{**dataclasses.asdict(check), "passed": bool(check.passed), "value": check.value.item() if hasattr(check.value, "item") else check.value} for check in checks]
    base.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    passed = sum(bool(check.passed) for check in checks)
    lines = ["# QIS framework validation", "", f"- Checks: **{len(checks)}**", f"- PASS: **{passed}**", f"- FAIL: **{len(checks)-passed}**", "", "| Check | Verdict | Value | Detail |", "|---|---|---:|---|"]
    for check in checks:
        lines.append(f"| `{check.name}` | {'PASS' if check.passed else 'FAIL'} | `{check.value}` | {check.detail} |")
    base.with_suffix(".md").write_text("\n".join(lines) + "\n")
    return 0 if passed == len(checks) else 1
