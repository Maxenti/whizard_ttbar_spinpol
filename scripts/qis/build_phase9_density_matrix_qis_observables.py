#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

COMPONENTS = ("r", "n", "k")


def pauli_matrices():
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return I, {"r": sx, "n": sy, "k": sz}


def build_rho(Bplus: dict[str, float], Bminus: dict[str, float], C: dict[str, float]) -> np.ndarray:
    I, sigma = pauli_matrices()

    rho = np.kron(I, I).astype(complex)

    for i in COMPONENTS:
        rho += float(Bplus[i]) * np.kron(sigma[i], I)
        rho += float(Bminus[i]) * np.kron(I, sigma[i])

    for i in COMPONENTS:
        for j in COMPONENTS:
            rho += float(C[f"{i}{j}"]) * np.kron(sigma[i], sigma[j])

    return 0.25 * rho


def partial_transpose_second_qubit(rho: np.ndarray) -> np.ndarray:
    # rho indices: (a,b),(c,d), with b,d being second-qubit indices.
    out = np.zeros_like(rho)
    for a in range(2):
        for b in range(2):
            for c in range(2):
                for d in range(2):
                    out[2 * a + b, 2 * c + d] = rho[2 * a + d, 2 * c + b]
    return out


def concurrence_candidate(rho: np.ndarray) -> float:
    _, sigma = pauli_matrices()
    sy = sigma["n"]

    yy = np.kron(sy, sy)
    rho_tilde = yy @ rho.conjugate() @ yy
    R = rho @ rho_tilde

    eig = np.linalg.eigvals(R)
    vals = sorted([math.sqrt(max(0.0, float(x.real))) for x in eig], reverse=True)

    if len(vals) != 4:
        return float("nan")

    return max(0.0, vals[0] - vals[1] - vals[2] - vals[3])


def horodecki_chsh_max(C: dict[str, float]) -> tuple[float, list[float]]:
    T = np.array([[float(C[f"{i}{j}"]) for j in COMPONENTS] for i in COMPONENTS], dtype=float)
    U = T.T @ T
    eig = sorted([float(x.real) for x in np.linalg.eigvals(U)], reverse=True)

    if len(eig) < 2:
        return float("nan"), eig

    return 2.0 * math.sqrt(max(0.0, eig[0] + eig[1])), eig


def as_real_matrix_entries(mat: np.ndarray) -> list[list[float]]:
    out = []
    for row in mat:
        out.append([float(x.real) for x in row])
    return out


def load_spin_samples(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    # Current builder writes either a top-level "samples" list or a dict-like
    # sample payload depending on script version. Support both.
    if isinstance(payload.get("samples"), list):
        return payload["samples"]

    if isinstance(payload.get("results"), list):
        return payload["results"]

    if isinstance(payload.get("moments_by_parent_label"), dict):
        samples = []
        for parent, m in payload["moments_by_parent_label"].items():
            row = {"parent_label": parent}
            row.update(m)
            samples.append(row)
        return samples

    raise SystemExit(f"ERROR: unsupported spin moment JSON schema in {path}")


def normalize_sample(sample: dict[str, Any]) -> dict[str, Any]:
    parent = sample.get("parent_label") or sample.get("sample") or sample.get("name")

    if parent is None:
        raise ValueError(f"sample missing parent label: {sample.keys()}")

    # Accept either nested blocks or flat columns.
    if all(k in sample for k in ["Bplus", "Bminus", "C"]):
        Bplus = {c: float(sample["Bplus"][c]) for c in COMPONENTS}
        Bminus = {c: float(sample["Bminus"][c]) for c in COMPONENTS}
        C = {f"{i}{j}": float(sample["C"][f"{i}{j}"]) for i in COMPONENTS for j in COMPONENTS}
    else:
        Bplus = {c: float(sample[f"Bplus_{c}"]) for c in COMPONENTS}
        Bminus = {c: float(sample[f"Bminus_{c}"]) for c in COMPONENTS}
        C = {f"{i}{j}": float(sample[f"C_{i}{j}"]) for i in COMPONENTS for j in COMPONENTS}

    n_events = int(sample.get("n_events", sample.get("events", 0)))

    return {
        "parent_label": str(parent),
        "n_events": n_events,
        "Bplus": Bplus,
        "Bminus": Bminus,
        "C": C,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spin-moments-json", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--summary-json", required=True)
    args = ap.parse_args()

    spin_path = Path(args.spin_moments_json)
    raw_samples = load_spin_samples(spin_path)
    samples = [normalize_sample(s) for s in raw_samples]

    rows = []

    for sample in samples:
        parent = sample["parent_label"]
        Bplus = sample["Bplus"]
        Bminus = sample["Bminus"]
        C = sample["C"]

        rho = build_rho(Bplus, Bminus, C)

        trace = np.trace(rho)
        herm_resid = np.max(np.abs(rho - rho.conjugate().T))

        eigvals = sorted([float(x.real) for x in np.linalg.eigvalsh(rho)])
        min_eig = min(eigvals)

        purity = float(np.real(np.trace(rho @ rho)))
        linear_entropy = float(1.0 - purity)

        rho_pt = partial_transpose_second_qubit(rho)
        pt_eigvals = sorted([float(x.real) for x in np.linalg.eigvalsh(rho_pt)])
        negativity = float(sum(abs(x) for x in pt_eigvals if x < 0.0))

        chsh_max, chsh_eigs = horodecki_chsh_max(C)
        concurrence = concurrence_candidate(rho)

        physicality = "physical_with_tolerance" if min_eig >= -1.0e-8 else "raw_nonpositive"

        row = {
            "parent_label": parent,
            "n_events": sample["n_events"],
            "basis": "rnk_common_v1_nominal_beam_phase9",
            "rho_trace_real": float(trace.real),
            "rho_trace_imag": float(trace.imag),
            "rho_hermiticity_max_abs_residual": float(herm_resid),
            "rho_min_eigenvalue": min_eig,
            "rho_eigenvalues": eigvals,
            "rho_physicality_flag": physicality,
            "purity_tr_rho2": purity,
            "linear_entropy_1_minus_purity": linear_entropy,
            "partial_transpose_min_eigenvalue": min(pt_eigvals),
            "negativity_candidate": negativity,
            "concurrence_candidate": concurrence,
            "bell_chsh_horodecki_max": chsh_max,
            "bell_chsh_violation_candidate": bool(chsh_max > 2.0),
            "horodecki_TtT_eigenvalues": chsh_eigs,
            "Bplus": Bplus,
            "Bminus": Bminus,
            "C": C,
            "rho_real": as_real_matrix_entries(rho),
        }

        rows.append(row)

    rows.sort(key=lambda r: r["parent_label"])

    payload = {
        "schema_version": 1,
        "status": "PASS",
        "spin_moments_json": str(spin_path),
        "basis": "rnk_common_v1_nominal_beam_phase9",
        "component_order": list(COMPONENTS),
        "samples": rows,
        "notes": [
            "Density matrices are built from raw Phase 9 truth-candidate spin moments.",
            "QIS quantities are diagnostic candidates; they should not be used as final publication claims until full physics-sample settings are frozen.",
            "Negative rho eigenvalues indicate that the raw estimated moment set is not exactly positive semidefinite; this can happen from statistical fluctuations or from non-final sample definitions.",
            "Bell-CHSH maximum uses the Horodecki criterion with the C matrix as the two-qubit correlation tensor.",
        ],
    }

    out_json = Path(args.output_json)
    out_csv = Path(args.output_csv)
    out_summary = Path(args.summary_json)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fields = [
        "parent_label",
        "n_events",
        "rho_trace_real",
        "rho_trace_imag",
        "rho_hermiticity_max_abs_residual",
        "rho_min_eigenvalue",
        "rho_physicality_flag",
        "purity_tr_rho2",
        "linear_entropy_1_minus_purity",
        "partial_transpose_min_eigenvalue",
        "negativity_candidate",
        "concurrence_candidate",
        "bell_chsh_horodecki_max",
        "bell_chsh_violation_candidate",
        "Bplus_r",
        "Bplus_n",
        "Bplus_k",
        "Bminus_r",
        "Bminus_n",
        "Bminus_k",
        "C_rr",
        "C_rn",
        "C_rk",
        "C_nr",
        "C_nn",
        "C_nk",
        "C_kr",
        "C_kn",
        "C_kk",
    ]

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()

        for r in rows:
            flat = {k: r.get(k) for k in fields}
            for c in COMPONENTS:
                flat[f"Bplus_{c}"] = r["Bplus"][c]
                flat[f"Bminus_{c}"] = r["Bminus"][c]
            for i in COMPONENTS:
                for j in COMPONENTS:
                    flat[f"C_{i}{j}"] = r["C"][f"{i}{j}"]
            writer.writerow(flat)

    summary = {
        "schema_version": 1,
        "status": "PASS",
        "spin_moments_json": str(spin_path),
        "qis_json": str(out_json),
        "qis_csv": str(out_csv),
        "basis": payload["basis"],
        "component_order": payload["component_order"],
        "samples": [
            {
                "parent_label": r["parent_label"],
                "n_events": r["n_events"],
                "rho_min_eigenvalue": r["rho_min_eigenvalue"],
                "rho_physicality_flag": r["rho_physicality_flag"],
                "purity_tr_rho2": r["purity_tr_rho2"],
                "negativity_candidate": r["negativity_candidate"],
                "concurrence_candidate": r["concurrence_candidate"],
                "bell_chsh_horodecki_max": r["bell_chsh_horodecki_max"],
                "bell_chsh_violation_candidate": r["bell_chsh_violation_candidate"],
            }
            for r in rows
        ],
        "notes": payload["notes"],
    }

    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("PHASE9_QIS_OBSERVABLE_STATUS=PASS")
    print(f"N_SAMPLES={len(rows)}")
    for r in rows:
        print(
            f"{r['parent_label']:20s} "
            f"minEig={r['rho_min_eigenvalue']:+.6f} "
            f"purity={r['purity_tr_rho2']:.6f} "
            f"CHSH={r['bell_chsh_horodecki_max']:.6f} "
            f"conc={r['concurrence_candidate']:.6f} "
            f"neg={r['negativity_candidate']:.6f} "
            f"{r['rho_physicality_flag']}"
        )

    print(f"WROTE_JSON={out_json}")
    print(f"WROTE_CSV={out_csv}")
    print(f"WROTE_SUMMARY={out_summary}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
