#!/usr/bin/env python3
"""Phase 11C.5 fresh-holdout single-grid vs multi-grid validator.

This validator implements the frozen C.5 decision rule:
  * four structurally valid, mutually disjoint 10k LHE components;
  * 48 hypothesis tests (24 KS + 24 quantile-binned chi2) in one
    Holm-Bonferroni family at FWER alpha=0.01;
  * practical-equivalence bounds |SMD| <= 0.05 and KS_D <= 0.02;
  * q05/q50/q95 shifts are diagnostics only and are NOT gating.

The script deliberately has a diagnostic mode. Diagnostic mode computes and
writes the same tables/plots, but it can never emit a C.5 PASS. This is intended
for code checks on already-inspected C.4 samples without contaminating the
fresh-holdout decision.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


VALIDATOR_NAME = "validate_single_vs_multigrid_c5.py"
VALIDATOR_VERSION = "phase11c5-v1"
SCHEMA_VERSION = 2

EXPECTED_EVENTS_PER_COMPONENT = 10_000
FAMILYWISE_ALPHA = 0.01
SMD_ABS_MAX = 0.05
KS_D_MAX = 0.02
QUANTILE_CHI2_BINS = 30
UNIT_WEIGHT_ATOL = 1.0e-15

OBSERVABLE_GROUPS = {
    "inclusive": [
        "pt_eplus",
        "pt_muminus",
        "eta_eplus",
        "eta_muminus",
        "energy_eplus",
        "energy_muminus",
        "pt_b",
        "pt_bbar",
        "eta_b",
        "eta_bbar",
    ],
    "resonance_isr": [
        "m_Wplus",
        "m_Wminus",
        "m_top",
        "m_tbar",
        "m_bb",
        "m_tt",
        "pt_tt",
        "abs_y_tt",
    ],
    "spin_angular": [
        "abs_dphi_ll",
        "deltaR_ll",
        "cos_opening_ll",
        "cos_helicity_eplus",
        "cos_helicity_muminus",
        "cos_helicity_product",
    ],
}

OBSERVABLES = [
    obs
    for group in OBSERVABLE_GROUPS.values()
    for obs in group
]

REQUIRED_PDGS = {
    "b": 5,
    "bbar": -5,
    "eplus": -11,
    "nue": 12,
    "muminus": 13,
    "numubar": -14,
}

EXPECTED_FINAL_STATE_COUNTER = Counter(REQUIRED_PDGS.values())
EXPECTED_FINAL_STATE_COUNTER.update({22: 2})

SAMPLE_ORDER = ["S0_C", "S0_D", "S1_B", "S2_B"]


# ---------------------------------------------------------------------------
# Basic helpers / provenance
# ---------------------------------------------------------------------------


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def require_regular_nonempty_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} is not a regular file: {path}")
    if path.stat().st_size <= 0:
        raise ValueError(f"{label} is empty: {path}")


# ---------------------------------------------------------------------------
# Four-vector utilities
# ---------------------------------------------------------------------------


def add(*vecs: np.ndarray) -> np.ndarray:
    return np.sum(np.asarray(vecs, dtype=float), axis=0)


def p3(v: np.ndarray) -> np.ndarray:
    return np.asarray(v[1:4], dtype=float)


def pt(v: np.ndarray) -> float:
    return math.hypot(float(v[1]), float(v[2]))


def mass(v: np.ndarray) -> float:
    m2 = float(v[0] * v[0] - np.dot(v[1:4], v[1:4]))
    return math.sqrt(max(m2, 0.0))


def eta(v: np.ndarray) -> float:
    transverse = pt(v)
    if transverse == 0:
        return math.copysign(float("inf"), float(v[3]))
    return math.asinh(float(v[3]) / transverse)


def phi(v: np.ndarray) -> float:
    return math.atan2(float(v[2]), float(v[1]))


def rapidity(v: np.ndarray) -> float:
    num = float(v[0] + v[3])
    den = float(v[0] - v[3])
    if num <= 0 or den <= 0:
        return float("nan")
    return 0.5 * math.log(num / den)


def unit(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    n = float(np.linalg.norm(x))
    if n == 0:
        return np.array([np.nan, np.nan, np.nan], dtype=float)
    return x / n


def boost_to_rest(v: np.ndarray, parent: np.ndarray) -> np.ndarray:
    parent = np.asarray(parent, dtype=float)
    v = np.asarray(v, dtype=float)

    if parent[0] == 0:
        return np.full(4, np.nan)

    beta = np.asarray(parent[1:4], dtype=float) / parent[0]
    b2 = float(np.dot(beta, beta))

    if b2 <= 0:
        return v.copy()
    if b2 >= 1:
        return np.full(4, np.nan)

    gamma = 1.0 / math.sqrt(1.0 - b2)
    e = float(v[0])
    p = np.asarray(v[1:4], dtype=float)
    bp = float(np.dot(beta, p))

    factor = ((gamma - 1.0) * bp / b2) - gamma * e
    out_p = p + factor * beta
    out_e = gamma * (e - bp)

    return np.array([out_e, out_p[0], out_p[1], out_p[2]], dtype=float)


def wrapped_abs_dphi(phi1: float, phi2: float) -> float:
    d = (phi1 - phi2 + math.pi) % (2.0 * math.pi) - math.pi
    return abs(d)


def cos_opening(a: np.ndarray, b: np.ndarray) -> float:
    ua = unit(p3(a))
    ub = unit(p3(b))
    return float(np.clip(np.dot(ua, ub), -1.0, 1.0))


# ---------------------------------------------------------------------------
# LHE parsing and observables
# ---------------------------------------------------------------------------


def parse_event_block(lines: list[str]) -> dict[str, Any]:
    payload = [
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]

    if not payload:
        raise ValueError("empty event block")

    header = payload[0].split()
    if len(header) < 3:
        raise ValueError("event header has fewer than three fields")

    nup = int(header[0])
    xwgtup = float(header[2])

    if nup < 0:
        raise ValueError(f"negative NUP={nup}")
    if len(payload) < nup + 1:
        raise ValueError(
            f"event declares {nup} particles but only {len(payload)-1} lines exist"
        )

    particles: list[dict[str, Any]] = []

    for line in payload[1 : nup + 1]:
        c = line.split()
        if len(c) < 11:
            raise ValueError(f"particle record has too few columns: {line}")

        pdg = int(c[0])
        status = int(c[1])
        px = float(c[6])
        py = float(c[7])
        pz = float(c[8])
        e = float(c[9])

        particles.append(
            {
                "pdg": pdg,
                "status": status,
                "v": np.array([e, px, py, pz], dtype=float),
            }
        )

    final = [p for p in particles if p["status"] == 1]
    final_counter = Counter(int(p["pdg"]) for p in final)

    selected: dict[str, np.ndarray] = {}
    for name, pdg in REQUIRED_PDGS.items():
        matches = [p for p in final if p["pdg"] == pdg]
        if len(matches) != 1:
            raise ValueError(
                f"required final-state PDG {pdg} ({name}) appears {len(matches)} times"
            )
        selected[name] = matches[0]["v"]

    return {
        "selected": selected,
        "xwgtup": xwgtup,
        "nup": nup,
        "final_counter": final_counter,
        "final_multiplicity": len(final),
    }


def compute_observables(x: dict[str, np.ndarray]) -> dict[str, float]:
    b = x["b"]
    bbar = x["bbar"]
    ep = x["eplus"]
    nue = x["nue"]
    mum = x["muminus"]
    numubar = x["numubar"]

    wp = add(ep, nue)
    wm = add(mum, numubar)
    top = add(b, wp)
    tbar = add(bbar, wm)
    tt = add(top, tbar)
    bb = add(b, bbar)

    dphi = wrapped_abs_dphi(phi(ep), phi(mum))
    dr = math.sqrt((eta(ep) - eta(mum)) ** 2 + dphi ** 2)

    # IMPORTANT: corrected sequential helicity-frame construction frozen
    # before C.4 unblinding: lab -> ttbar rest -> parent-top rest.
    top_in_tt = boost_to_rest(top, tt)
    tbar_in_tt = boost_to_rest(tbar, tt)

    ep_in_tt = boost_to_rest(ep, tt)
    mum_in_tt = boost_to_rest(mum, tt)

    ep_in_top = boost_to_rest(ep_in_tt, top_in_tt)
    mum_in_tbar = boost_to_rest(mum_in_tt, tbar_in_tt)

    axis_top = unit(p3(top_in_tt))
    axis_tbar = unit(p3(tbar_in_tt))
    lep_plus_dir = unit(p3(ep_in_top))
    lep_minus_dir = unit(p3(mum_in_tbar))

    c_plus = float(np.clip(np.dot(lep_plus_dir, axis_top), -1.0, 1.0))
    c_minus = float(np.clip(np.dot(lep_minus_dir, axis_tbar), -1.0, 1.0))

    return {
        "pt_eplus": pt(ep),
        "pt_muminus": pt(mum),
        "eta_eplus": eta(ep),
        "eta_muminus": eta(mum),
        "energy_eplus": float(ep[0]),
        "energy_muminus": float(mum[0]),
        "pt_b": pt(b),
        "pt_bbar": pt(bbar),
        "eta_b": eta(b),
        "eta_bbar": eta(bbar),
        "m_Wplus": mass(wp),
        "m_Wminus": mass(wm),
        "m_top": mass(top),
        "m_tbar": mass(tbar),
        "m_bb": mass(bb),
        "m_tt": mass(tt),
        "pt_tt": pt(tt),
        "abs_y_tt": abs(rapidity(tt)),
        "abs_dphi_ll": dphi,
        "deltaR_ll": dr,
        "cos_opening_ll": cos_opening(ep, mum),
        "cos_helicity_eplus": c_plus,
        "cos_helicity_muminus": c_minus,
        "cos_helicity_product": c_plus * c_minus,
    }


def read_lhe(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    require_regular_nonempty_file(path, "LHE input")

    values = {name: [] for name in OBSERVABLES}
    hashes: list[str] = []
    weights: list[float] = []
    issues: list[dict[str, Any]] = []
    final_state_counts: Counter[tuple[int, ...]] = Counter()
    final_multiplicities: Counter[int] = Counter()

    inside = False
    block: list[str] = []
    event_index = 0

    with path.open() as f:
        for line_number, raw in enumerate(f, start=1):
            stripped = raw.strip()

            if stripped.startswith("<event"):
                if inside:
                    issues.append(
                        {
                            "event_index": event_index + 1,
                            "error": f"nested <event> at file line {line_number}",
                        }
                    )
                inside = True
                block = []
                continue

            if stripped.startswith("</event"):
                if not inside:
                    issues.append(
                        {
                            "event_index": event_index + 1,
                            "error": f"unmatched </event> at file line {line_number}",
                        }
                    )
                    continue

                event_index += 1
                block_text = "".join(block)
                hashes.append(hashlib.sha256(block_text.encode("utf-8")).hexdigest())

                try:
                    parsed = parse_event_block(block)
                    obs = compute_observables(parsed["selected"])

                    weights.append(float(parsed["xwgtup"]))

                    final_counter: Counter[int] = parsed["final_counter"]
                    expanded: list[int] = []
                    for pdg, count in sorted(final_counter.items()):
                        expanded.extend([pdg] * count)
                    final_state_counts[tuple(expanded)] += 1
                    final_multiplicities[int(parsed["final_multiplicity"])] += 1

                    for key, value in obs.items():
                        values[key].append(value)

                except Exception as exc:
                    issues.append(
                        {
                            "event_index": event_index,
                            "error": str(exc),
                        }
                    )

                inside = False
                block = []
                continue

            if inside:
                block.append(raw)

    if inside:
        issues.append(
            {
                "event_index": event_index + 1,
                "error": "unterminated final <event> block at EOF",
            }
        )

    arrays = {key: np.asarray(vals, dtype=float) for key, vals in values.items()}

    return {
        "path": str(path),
        "file_size_bytes": int(path.stat().st_size),
        "file_sha256": sha256_file(path),
        "events_seen": event_index,
        "issues": issues,
        "hashes": hashes,
        "weights": np.asarray(weights, dtype=float),
        "final_state_counts": final_state_counts,
        "final_multiplicities": final_multiplicities,
        "arrays": arrays,
    }


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def quantile_chi2(a: np.ndarray, b: np.ndarray, n_bins: int = QUANTILE_CHI2_BINS) -> tuple[float, float, int]:
    pooled = np.concatenate([a, b])
    edges = np.unique(np.quantile(pooled, np.linspace(0.0, 1.0, n_bins + 1)))

    if len(edges) < 3:
        return 0.0, 1.0, max(0, len(edges) - 1)

    edges = edges.astype(float, copy=True)
    edges[0] = -np.inf
    edges[-1] = np.inf

    ca, _ = np.histogram(a, bins=edges)
    cb, _ = np.histogram(b, bins=edges)
    table = np.vstack([ca, cb])

    keep = table.sum(axis=0) > 0
    table = table[:, keep]

    if table.shape[1] < 2:
        return 0.0, 1.0, int(table.shape[1])

    chi2, p_value, _, _ = stats.chi2_contingency(table, correction=False)
    return float(chi2), float(p_value), int(table.shape[1])


def effect_metrics(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    var_a = float(np.var(a, ddof=1))
    var_b = float(np.var(b, ddof=1))

    denom_n = len(a) + len(b) - 2
    if denom_n <= 0:
        pooled_sd = 0.0
    else:
        pooled_sd = math.sqrt(
            max(
                0.0,
                ((len(a) - 1) * var_a + (len(b) - 1) * var_b) / denom_n,
            )
        )

    mean_a = float(np.mean(a))
    mean_b = float(np.mean(b))
    smd = (mean_a - mean_b) / pooled_sd if pooled_sd > 0 else 0.0

    pooled = np.concatenate([a, b])
    pooled_q25, pooled_q75 = np.quantile(pooled, [0.25, 0.75])
    pooled_iqr = float(pooled_q75 - pooled_q25)

    qa = np.quantile(a, [0.05, 0.50, 0.95])
    qb = np.quantile(b, [0.05, 0.50, 0.95])
    dq = qa - qb

    # Retain the old IQR-normalized values strictly as diagnostics. They are
    # intentionally not used in any C.5 gate.
    diagnostic_scale = pooled_iqr
    if diagnostic_scale <= 0:
        diagnostic_scale = float(np.std(pooled, ddof=1))
    if diagnostic_scale <= 0:
        diagnostic_scale = 1.0

    qshift_iqr = dq / diagnostic_scale

    return {
        "mean_a": mean_a,
        "mean_b": mean_b,
        "std_a": float(np.std(a, ddof=1)),
        "std_b": float(np.std(b, ddof=1)),
        "pooled_sd": float(pooled_sd),
        "smd": float(smd),
        "pooled_q25": float(pooled_q25),
        "pooled_q75": float(pooled_q75),
        "pooled_iqr": pooled_iqr,
        "q05_a": float(qa[0]),
        "q05_b": float(qb[0]),
        "q05_shift_raw": float(dq[0]),
        "q05_shift_iqr_diagnostic": float(qshift_iqr[0]),
        "q50_a": float(qa[1]),
        "q50_b": float(qb[1]),
        "q50_shift_raw": float(dq[1]),
        "q50_shift_iqr_diagnostic": float(qshift_iqr[1]),
        "q95_a": float(qa[2]),
        "q95_b": float(qb[2]),
        "q95_shift_raw": float(dq[2]),
        "q95_shift_iqr_diagnostic": float(qshift_iqr[2]),
    }


def holm_bonferroni(records: list[dict[str, Any]], alpha: float = FAMILYWISE_ALPHA) -> tuple[list[bool], list[float]]:
    n = len(records)
    order = sorted(range(n), key=lambda i: float(records[i]["p_value"]))

    rejected = [False] * n
    adjusted = [1.0] * n
    running_adjusted = 0.0
    keep_rejecting = True

    for rank, idx in enumerate(order):
        p_value = float(records[idx]["p_value"])
        factor = n - rank

        raw_adjusted = min(1.0, factor * p_value)
        running_adjusted = max(running_adjusted, raw_adjusted)
        adjusted[idx] = running_adjusted

        threshold = alpha / factor
        if keep_rejecting and p_value <= threshold:
            rejected[idx] = True
        else:
            keep_rejecting = False

    return rejected, adjusted


def compare(a: dict[str, np.ndarray], b: dict[str, np.ndarray], label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for obs in OBSERVABLES:
        x = np.asarray(a[obs], dtype=float)
        y = np.asarray(b[obs], dtype=float)

        ks = stats.ks_2samp(x, y, alternative="two-sided", method="asymp")
        chi2, chi2_p, n_bins = quantile_chi2(x, y)
        eff = effect_metrics(x, y)

        rows.append(
            {
                "comparison": label,
                "observable": obs,
                "n_a": int(len(x)),
                "n_b": int(len(y)),
                "ks_D": float(ks.statistic),
                "ks_p": float(ks.pvalue),
                "chi2": chi2,
                "chi2_p": chi2_p,
                "chi2_bins": n_bins,
                **eff,
            }
        )

    return rows


# ---------------------------------------------------------------------------
# Structural gate
# ---------------------------------------------------------------------------


def expected_final_signature() -> tuple[int, ...]:
    expanded: list[int] = []
    for pdg, count in sorted(EXPECTED_FINAL_STATE_COUNTER.items()):
        expanded.extend([pdg] * count)
    return tuple(expanded)


def structural_audit(data: dict[str, dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    failures: list[str] = []
    component_rows: list[dict[str, Any]] = []
    expected_signature = expected_final_signature()

    for name in SAMPLE_ORDER:
        d = data[name]
        nonfinite: dict[str, int] = {}
        wrong_lengths: dict[str, int] = {}

        for obs in OBSERVABLES:
            arr = d["arrays"][obs]
            if len(arr) != EXPECTED_EVENTS_PER_COMPONENT:
                wrong_lengths[obs] = int(len(arr))
            n_bad = int(np.sum(~np.isfinite(arr)))
            if n_bad:
                nonfinite[obs] = n_bad

        unique_hashes = len(set(d["hashes"]))
        weights = d["weights"]
        unit_weights = (
            len(weights) == EXPECTED_EVENTS_PER_COMPONENT
            and bool(np.allclose(weights, 1.0, rtol=0.0, atol=UNIT_WEIGHT_ATOL))
        )
        weight_min = float(np.min(weights)) if len(weights) else float("nan")
        weight_max = float(np.max(weights)) if len(weights) else float("nan")
        unique_weight_count = int(len(np.unique(weights))) if len(weights) else 0

        final_state_exact = (
            d["final_state_counts"]
            == Counter({expected_signature: EXPECTED_EVENTS_PER_COMPONENT})
        )
        final_multiplicity_exact = (
            d["final_multiplicities"]
            == Counter({8: EXPECTED_EVENTS_PER_COMPONENT})
        )

        row = {
            "sample": name,
            "path": d["path"],
            "file_size_bytes": d["file_size_bytes"],
            "file_sha256": d["file_sha256"],
            "events_seen": d["events_seen"],
            "events_parsed": int(len(d["arrays"][OBSERVABLES[0]])),
            "parse_issues": len(d["issues"]),
            "raw_event_hashes": len(d["hashes"]),
            "unique_event_hashes": unique_hashes,
            "weights_seen": int(len(weights)),
            "unique_weight_count": unique_weight_count,
            "weight_min": weight_min,
            "weight_max": weight_max,
            "unit_weights_pass": unit_weights,
            "expected_final_state_pass": final_state_exact,
            "expected_final_multiplicity_pass": final_multiplicity_exact,
            "wrong_observable_lengths": wrong_lengths,
            "nonfinite_observables": nonfinite,
        }
        component_rows.append(row)

        if d["events_seen"] != EXPECTED_EVENTS_PER_COMPONENT:
            failures.append(f"{name}: events_seen={d['events_seen']}")
        if len(d["issues"]) != 0:
            failures.append(f"{name}: parse_issues={len(d['issues'])}")
        if len(d["hashes"]) != EXPECTED_EVENTS_PER_COMPONENT:
            failures.append(f"{name}: raw_event_hashes={len(d['hashes'])}")
        if unique_hashes != EXPECTED_EVENTS_PER_COMPONENT:
            failures.append(f"{name}: unique_event_hashes={unique_hashes}")
        if wrong_lengths:
            failures.append(f"{name}: wrong_observable_lengths={wrong_lengths}")
        if nonfinite:
            failures.append(f"{name}: nonfinite_observables={nonfinite}")
        if not unit_weights:
            failures.append(f"{name}: unit_LHE_weights=FAIL")
        if not final_state_exact:
            failures.append(f"{name}: expected_final_state_signature=FAIL")
        if not final_multiplicity_exact:
            failures.append(f"{name}: expected_final_multiplicity=FAIL")

    overlap_rows: list[dict[str, Any]] = []
    for i, a in enumerate(SAMPLE_ORDER):
        for b in SAMPLE_ORDER[i + 1 :]:
            overlap = len(set(data[a]["hashes"]) & set(data[b]["hashes"]))
            same_position = sum(
                x == y for x, y in zip(data[a]["hashes"], data[b]["hashes"])
            )
            overlap_rows.append(
                {
                    "sample_a": a,
                    "sample_b": b,
                    "exact_event_overlap": int(overlap),
                    "same_position_event_hashes": int(same_position),
                }
            )
            if overlap != 0:
                failures.append(f"{a}/{b}: exact_event_overlap={overlap}")

    all_hashes = [h for name in SAMPLE_ORDER for h in data[name]["hashes"]]
    total_expected = EXPECTED_EVENTS_PER_COMPONENT * len(SAMPLE_ORDER)
    total_unique = len(set(all_hashes))
    if len(all_hashes) != total_expected:
        failures.append(f"global: total_event_hashes={len(all_hashes)} expected={total_expected}")
    if total_unique != total_expected:
        failures.append(f"global: total_unique_event_hashes={total_unique} expected={total_expected}")

    return failures, component_rows, overlap_rows


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def empirical_cdf_difference(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grid = np.unique(np.concatenate([a, b]))
    sa = np.sort(a)
    sb = np.sort(b)
    fa = np.searchsorted(sa, grid, side="right") / len(sa)
    fb = np.searchsorted(sb, grid, side="right") / len(sb)
    return grid, fa - fb


def make_overlays(single: dict[str, np.ndarray], multi: dict[str, np.ndarray], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    for obs in OBSERVABLES:
        a = single[obs]
        b = multi[obs]
        pooled = np.concatenate([a, b])

        lo, hi = np.quantile(pooled, [0.001, 0.999])
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            lo = float(np.nanmin(pooled))
            hi = float(np.nanmax(pooled))
        if hi <= lo:
            lo -= 0.5
            hi += 0.5

        bins = np.linspace(lo, hi, 51)
        h1, edges = np.histogram(a, bins=bins, density=True)
        h2, _ = np.histogram(b, bins=bins, density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])

        fig = plt.figure(figsize=(8, 9))
        gs = fig.add_gridspec(3, 1, height_ratios=[3.0, 1.2, 1.2], hspace=0.08)
        ax = fig.add_subplot(gs[0])
        rx = fig.add_subplot(gs[1], sharex=ax)
        dx = fig.add_subplot(gs[2])

        ax.step(centers, h1, where="mid", label="Single grid: S0_C + S0_D")
        ax.step(centers, h2, where="mid", label="Multi-grid: S1_B + S2_B")
        ax.set_ylabel("Normalized density")
        ax.set_title(obs)
        ax.legend()

        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(h2 > 0, h1 / h2, np.nan)
        rx.axhline(1.0, linewidth=1)
        rx.plot(centers, ratio, marker=".", linestyle="none")
        rx.set_ylabel("S/M")
        rx.set_ylim(0.5, 1.5)

        xcdf, dcdf = empirical_cdf_difference(a, b)
        dx.axhline(0.0, linewidth=1)
        dx.axhline(+KS_D_MAX, linestyle="--", linewidth=1)
        dx.axhline(-KS_D_MAX, linestyle="--", linewidth=1)
        dx.plot(xcdf, dcdf, linewidth=1)
        dx.set_ylabel("F_S - F_M")
        dx.set_xlabel(obs)
        ylim = max(0.03, KS_D_MAX * 1.5, 1.15 * float(np.max(np.abs(dcdf))))
        dx.set_ylim(-ylim, +ylim)

        fig.savefig(outdir / f"{obs}.png", dpi=160, bbox_inches="tight")
        plt.close(fig)


def make_summary_plots(primary: list[dict[str, Any]], plotdir: Path) -> None:
    labels = [row["observable"] for row in primary]
    y = np.arange(len(labels))

    smd = np.array([row["smd"] for row in primary], dtype=float)
    fig, ax = plt.subplots(figsize=(8, max(6, 0.32 * len(labels))))
    ax.axvline(0.0, linewidth=1)
    ax.axvline(-SMD_ABS_MAX, linestyle="--", linewidth=1)
    ax.axvline(+SMD_ABS_MAX, linestyle="--", linewidth=1)
    ax.plot(smd, y, marker="o", linestyle="none")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Standardized mean difference: SINGLE - MULTI")
    ax.set_title("Phase 11C.5 standardized mean differences")
    fig.savefig(plotdir / "summary_standardized_mean_differences.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    ks_d = np.array([row["ks_D"] for row in primary], dtype=float)
    fig, ax = plt.subplots(figsize=(8, max(6, 0.32 * len(labels))))
    ax.axvline(KS_D_MAX, linestyle="--", linewidth=1)
    ax.plot(ks_d, y, marker="o", linestyle="none")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Two-sample KS D")
    ax.set_title("Phase 11C.5 KS practical-equivalence metric")
    fig.savefig(plotdir / "summary_ks_D.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        if not rows:
            raise ValueError(f"cannot infer TSV fields for empty row list: {path}")
        fieldnames = list(rows[0].keys())

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_output_hash_manifest(outdir: Path) -> None:
    manifest = outdir / "OUTPUT_FILE_SHA256SUMS.txt"
    rows: list[tuple[str, str]] = []
    for path in sorted(outdir.rglob("*")):
        if not path.is_file() or path == manifest:
            continue
        rows.append((sha256_file(path), str(path.relative_to(outdir))))
    manifest.write_text("".join(f"{digest}  {rel}\n" for digest, rel in rows))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def run_self_test() -> int:
    failures: list[str] = []

    parent = np.array([5.0, 3.0, 0.0, 0.0])
    rest = boost_to_rest(parent, parent)
    if not np.allclose(rest[1:], 0.0, atol=1e-12):
        failures.append(f"boost_to_rest(parent,parent) spatial={rest[1:]}")
    if not math.isclose(rest[0], 4.0, rel_tol=0.0, abs_tol=1e-12):
        failures.append(f"boost_to_rest invariant mass expected 4, got {rest[0]}")

    x = np.arange(100.0)
    y = x.copy()
    rows = compare({obs: x for obs in OBSERVABLES}, {obs: y for obs in OBSERVABLES}, "SELFTEST")
    if any(row["ks_D"] != 0.0 for row in rows):
        failures.append("identical-array KS_D self-test failed")
    if any(abs(row["smd"]) > 1e-15 for row in rows):
        failures.append("identical-array SMD self-test failed")

    p_records = [
        {"p_value": 0.00001},
        {"p_value": 0.2},
        {"p_value": 0.9},
    ]
    rejected, adjusted = holm_bonferroni(p_records, alpha=0.01)
    if rejected != [True, False, False]:
        failures.append(f"Holm rejection self-test failed: {rejected}")
    if not all(0.0 <= x <= 1.0 for x in adjusted):
        failures.append(f"Holm adjusted-p range failed: {adjusted}")

    if len(OBSERVABLES) != 24:
        failures.append(f"expected 24 observables, got {len(OBSERVABLES)}")

    if failures:
        print("PHASE11C5_VALIDATOR_SELF_TEST=FAIL")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("PHASE11C5_VALIDATOR_SELF_TEST=PASS")
    print(f"OBSERVABLE_COUNT={len(OBSERVABLES)}")
    print(f"EXPECTED_HOLM_TEST_COUNT={2 * len(OBSERVABLES)}")
    print(f"FAMILYWISE_ALPHA={FAMILYWISE_ALPHA}")
    print(f"SMD_ABS_MAX={SMD_ABS_MAX}")
    print(f"KS_D_MAX={KS_D_MAX}")
    return 0


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Phase 11C.5 fresh-holdout single-grid vs multi-grid validator"
    )
    ap.add_argument("--self-test", action="store_true", help="run internal deterministic unit checks and exit")
    ap.add_argument(
        "--validation-mode",
        choices=["holdout", "diagnostic"],
        default="holdout",
        help="diagnostic mode can never emit a C.5 PASS",
    )
    ap.add_argument("--s0-c")
    ap.add_argument("--s0-d")
    ap.add_argument("--s1-b")
    ap.add_argument("--s2-b")
    ap.add_argument("--validation-plan")
    ap.add_argument("--outdir")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        return run_self_test()

    required_cli = {
        "--s0-c": args.s0_c,
        "--s0-d": args.s0_d,
        "--s1-b": args.s1_b,
        "--s2-b": args.s2_b,
        "--validation-plan": args.validation_plan,
        "--outdir": args.outdir,
    }
    missing = [flag for flag, value in required_cli.items() if not value]
    if missing:
        raise SystemExit("missing required arguments: " + ", ".join(missing))

    plan_path = Path(args.validation_plan).resolve()
    require_regular_nonempty_file(plan_path, "validation plan")

    component_paths = {
        "S0_C": Path(args.s0_c).resolve(),
        "S0_D": Path(args.s0_d).resolve(),
        "S1_B": Path(args.s1_b).resolve(),
        "S2_B": Path(args.s2_b).resolve(),
    }
    for name, path in component_paths.items():
        require_regular_nonempty_file(path, f"{name} input")

    if len(set(component_paths.values())) != len(component_paths):
        raise SystemExit("structural setup error: component input paths are not all distinct")

    outdir = Path(args.outdir).resolve()
    if outdir.exists():
        raise SystemExit(f"refusing to overwrite existing output directory: {outdir}")
    outdir.mkdir(parents=True, exist_ok=False)
    plotdir = outdir / "plots"
    plotdir.mkdir(parents=True, exist_ok=False)

    start_time = utc_now_iso()
    script_path = Path(__file__).resolve()

    provenance = {
        "schema_version": SCHEMA_VERSION,
        "validator_name": VALIDATOR_NAME,
        "validator_version": VALIDATOR_VERSION,
        "validation_mode": args.validation_mode,
        "started_utc": start_time,
        "argv": sys.argv,
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "matplotlib_version": matplotlib.__version__,
        "script_path": str(script_path),
        "script_sha256": sha256_file(script_path),
        "validation_plan_path": str(plan_path),
        "validation_plan_sha256": sha256_file(plan_path),
        "frozen_constants": {
            "expected_events_per_component": EXPECTED_EVENTS_PER_COMPONENT,
            "familywise_alpha": FAMILYWISE_ALPHA,
            "smd_abs_max": SMD_ABS_MAX,
            "ks_D_max": KS_D_MAX,
            "quantile_chi2_bins": QUANTILE_CHI2_BINS,
            "unit_weight_atol": UNIT_WEIGHT_ATOL,
            "observable_count": len(OBSERVABLES),
            "holm_test_count": 2 * len(OBSERVABLES),
        },
    }

    data: dict[str, dict[str, Any]] = {}
    for name in SAMPLE_ORDER:
        path = component_paths[name]
        print(f"Reading {name}: {path}")
        data[name] = read_lhe(path)

    structural_failures, component_summary, overlap_rows = structural_audit(data)

    write_tsv(outdir / "component_summary.tsv", component_summary)
    write_tsv(outdir / "event_overlap.tsv", overlap_rows)

    final_state_rows: list[dict[str, Any]] = []
    for name in SAMPLE_ORDER:
        for signature, count in sorted(data[name]["final_state_counts"].items()):
            final_state_rows.append(
                {
                    "sample": name,
                    "status1_pdg_signature": ",".join(str(x) for x in signature),
                    "count": int(count),
                }
            )
    write_tsv(
        outdir / "final_state_signatures.tsv",
        final_state_rows,
        fieldnames=["sample", "status1_pdg_signature", "count"],
    )

    event_hash_dir = outdir / "event_hashes"
    event_hash_dir.mkdir(parents=False, exist_ok=False)
    for name in SAMPLE_ORDER:
        (event_hash_dir / f"{name}.event_sha256.tsv").write_text(
            "event_index\tsha256\n"
            + "".join(
                f"{i}\t{digest}\n"
                for i, digest in enumerate(data[name]["hashes"], start=1)
            )
        )

    parse_issue_rows: list[dict[str, Any]] = []
    for name in SAMPLE_ORDER:
        for issue in data[name]["issues"]:
            parse_issue_rows.append(
                {
                    "sample": name,
                    "event_index": issue["event_index"],
                    "error": issue["error"],
                }
            )
    write_tsv(
        outdir / "parse_issues.tsv",
        parse_issue_rows,
        fieldnames=["sample", "event_index", "error"],
    )

    input_manifest = {
        name: {
            "path": data[name]["path"],
            "file_size_bytes": data[name]["file_size_bytes"],
            "sha256": data[name]["file_sha256"],
            "events_seen": data[name]["events_seen"],
            "unique_event_hashes": len(set(data[name]["hashes"])),
        }
        for name in SAMPLE_ORDER
    }
    write_json(outdir / "INPUT_MANIFEST.json", input_manifest)
    (outdir / "INPUT_FILE_SHA256SUMS.txt").write_text(
        "".join(
            f"{data[name]['file_sha256']}  {data[name]['path']}\n"
            for name in SAMPLE_ORDER
        )
    )

    # A structural failure blocks all physics-statistical evaluation. This
    # prevents malformed or overlapping samples from yielding a misleading
    # physics PASS/FAIL result.
    if structural_failures:
        result = {
            "schema_version": SCHEMA_VERSION,
            "validator_version": VALIDATOR_VERSION,
            "validation_mode": args.validation_mode,
            "gate": "FAIL" if args.validation_mode == "holdout" else "DIAGNOSTIC_ONLY",
            "physics_evaluation_performed": False,
            "structural_failures": structural_failures,
            "hypothesis_failures": [],
            "practical_equivalence_failures": [],
            "thresholds": {
                "familywise_alpha": FAMILYWISE_ALPHA,
                "abs_smd_max": SMD_ABS_MAX,
                "ks_D_max": KS_D_MAX,
            },
            "observable_groups": OBSERVABLE_GROUPS,
            "samples": component_summary,
        }
        write_json(outdir / "VALIDATION_RESULT.json", result)
        provenance["finished_utc"] = utc_now_iso()
        provenance["result_gate"] = result["gate"]
        write_json(outdir / "VALIDATION_PROVENANCE.json", provenance)

        with (outdir / "VALIDATION_SUMMARY.txt").open("w") as f:
            top = "FAIL" if args.validation_mode == "holdout" else "DIAGNOSTIC_ONLY"
            f.write(f"PHASE11C5_SINGLE_VS_MULTIGRID={top}\n\n")
            f.write("Physics evaluation performed: NO\n")
            f.write(f"Structural failures: {len(structural_failures)}\n")
            for failure in structural_failures:
                f.write(f"  {failure}\n")

        write_output_hash_manifest(outdir)
        print("PHASE11C5_SINGLE_VS_MULTIGRID=" + ("FAIL" if args.validation_mode == "holdout" else "DIAGNOSTIC_ONLY"))
        print(f"Structural failures: {len(structural_failures)}")
        print("Physics evaluation performed: NO")
        return 2 if args.validation_mode == "holdout" else 0

    single = {
        obs: np.concatenate([data["S0_C"]["arrays"][obs], data["S0_D"]["arrays"][obs]])
        for obs in OBSERVABLES
    }
    multi = {
        obs: np.concatenate([data["S1_B"]["arrays"][obs], data["S2_B"]["arrays"][obs]])
        for obs in OBSERVABLES
    }

    primary = compare(single, multi, "SINGLE_S0CD_vs_MULTI_S1B_S2B")
    internal_s0 = compare(data["S0_C"]["arrays"], data["S0_D"]["arrays"], "S0_C_vs_S0_D")
    internal_multi = compare(data["S1_B"]["arrays"], data["S2_B"]["arrays"], "S1_B_vs_S2_B")

    p_records: list[dict[str, Any]] = []
    for row in primary:
        p_records.append({"observable": row["observable"], "test": "KS", "p_value": row["ks_p"]})
        p_records.append({"observable": row["observable"], "test": "CHI2", "p_value": row["chi2_p"]})

    if len(p_records) != 48:
        raise RuntimeError(f"internal invariant broken: expected 48 hypothesis tests, got {len(p_records)}")

    rejected, adjusted = holm_bonferroni(p_records, alpha=FAMILYWISE_ALPHA)
    for rec, reject, adj in zip(p_records, rejected, adjusted):
        rec["holm_reject"] = bool(reject)
        rec["holm_adjusted_p"] = float(adj)

    lookup = {(r["observable"], r["test"]): r for r in p_records}

    practical_failures: list[str] = []
    smd_failures: list[str] = []
    ks_d_failures: list[str] = []

    for row in primary:
        obs = row["observable"]
        row["ks_holm_reject"] = lookup[(obs, "KS")]["holm_reject"]
        row["ks_holm_adjusted_p"] = lookup[(obs, "KS")]["holm_adjusted_p"]
        row["chi2_holm_reject"] = lookup[(obs, "CHI2")]["holm_reject"]
        row["chi2_holm_adjusted_p"] = lookup[(obs, "CHI2")]["holm_adjusted_p"]

        row["smd_pass"] = abs(row["smd"]) <= SMD_ABS_MAX
        row["ks_D_pass"] = row["ks_D"] <= KS_D_MAX
        row["quantile_diagnostics_gate"] = "NOT_GATING_IN_C5"

        if not row["smd_pass"]:
            msg = f"{obs}: |SMD|={abs(row['smd']):.6g} > {SMD_ABS_MAX:.6g}"
            smd_failures.append(msg)
            practical_failures.append(msg)
        if not row["ks_D_pass"]:
            msg = f"{obs}: KS_D={row['ks_D']:.6g} > {KS_D_MAX:.6g}"
            ks_d_failures.append(msg)
            practical_failures.append(msg)

    hypothesis_failures = [
        f"{r['observable']}:{r['test']}"
        for r in p_records
        if r["holm_reject"]
    ]

    holdout_pass = not structural_failures and not hypothesis_failures and not practical_failures
    reported_gate = (
        ("PASS" if holdout_pass else "FAIL")
        if args.validation_mode == "holdout"
        else "DIAGNOSTIC_ONLY"
    )

    write_tsv(outdir / "observable_comparison.tsv", primary)
    write_tsv(outdir / "component_diagnostics.tsv", internal_s0 + internal_multi)
    write_tsv(outdir / "hypothesis_tests.tsv", p_records)

    npz: dict[str, np.ndarray] = {}
    for sample in SAMPLE_ORDER:
        for obs in OBSERVABLES:
            npz[f"{sample}__{obs}"] = data[sample]["arrays"][obs]
    np.savez_compressed(outdir / "component_observables.npz", **npz)

    make_overlays(single, multi, plotdir)
    make_summary_plots(primary, plotdir)

    result = {
        "schema_version": SCHEMA_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "validation_mode": args.validation_mode,
        "gate": reported_gate,
        "holdout_rule_would_pass": bool(holdout_pass),
        "physics_evaluation_performed": True,
        "familywise_alpha": FAMILYWISE_ALPHA,
        "holm_test_count": len(p_records),
        "structural_failures": structural_failures,
        "hypothesis_failures": hypothesis_failures,
        "practical_equivalence_failures": practical_failures,
        "smd_failures": smd_failures,
        "ks_D_failures": ks_d_failures,
        "observable_groups": OBSERVABLE_GROUPS,
        "thresholds": {
            "abs_smd_max": SMD_ABS_MAX,
            "ks_D_max": KS_D_MAX,
            "old_abs_quantile_shift_over_iqr_gate": "REMOVED_FROM_C5_DECISION_RULE",
        },
        "quantile_diagnostics": {
            "reported_quantiles": [0.05, 0.50, 0.95],
            "raw_shifts_reported": True,
            "iqr_normalized_shifts_reported_for_diagnosis_only": True,
            "gating": False,
        },
        "samples": component_summary,
    }
    write_json(outdir / "VALIDATION_RESULT.json", result)

    with (outdir / "VALIDATION_SUMMARY.txt").open("w") as f:
        f.write(f"PHASE11C5_SINGLE_VS_MULTIGRID={reported_gate}\n\n")
        if args.validation_mode == "diagnostic":
            f.write("IMPORTANT: diagnostic mode cannot constitute a Phase-11C.5 PASS.\n")
            f.write(f"Holdout rule would pass on these diagnostic inputs: {'YES' if holdout_pass else 'NO'}\n\n")

        f.write("Physics evaluation performed: YES\n")
        f.write(f"Structural failures: {len(structural_failures)}\n")
        for failure in structural_failures:
            f.write(f"  {failure}\n")

        f.write(f"\nHolm-rejected tests: {len(hypothesis_failures)} / {len(p_records)}\n")
        for failure in hypothesis_failures:
            f.write(f"  {failure}\n")

        f.write(f"\nPractical-equivalence failures: {len(practical_failures)}\n")
        for failure in practical_failures:
            f.write(f"  {failure}\n")

        f.write(f"\nSMD failures: {len(smd_failures)} (limit |SMD| <= {SMD_ABS_MAX})\n")
        f.write(f"KS_D failures: {len(ks_d_failures)} (limit KS_D <= {KS_D_MAX})\n")
        f.write("q05/q50/q95 shifts: DIAGNOSTIC ONLY; NOT A C.5 GATE\n")

        f.write("\nLargest |SMD| values:\n")
        for row in sorted(primary, key=lambda r: abs(r["smd"]), reverse=True)[:10]:
            f.write(
                f"  {row['observable']:28s} SMD={row['smd']:+.6f} "
                f"KS_D={row['ks_D']:.6f} KS_p={row['ks_p']:.6g}\n"
            )

        f.write("\nLargest KS_D values:\n")
        for row in sorted(primary, key=lambda r: r["ks_D"], reverse=True)[:10]:
            f.write(
                f"  {row['observable']:28s} KS_D={row['ks_D']:.6f} "
                f"SMD={row['smd']:+.6f} KS_p={row['ks_p']:.6g}\n"
            )

    provenance["finished_utc"] = utc_now_iso()
    provenance["result_gate"] = reported_gate
    provenance["holdout_rule_would_pass"] = bool(holdout_pass)
    provenance["input_manifest"] = input_manifest
    write_json(outdir / "VALIDATION_PROVENANCE.json", provenance)

    write_output_hash_manifest(outdir)

    print(f"PHASE11C5_SINGLE_VS_MULTIGRID={reported_gate}")
    if args.validation_mode == "diagnostic":
        print("DIAGNOSTIC_MODE=YES")
        print(f"HOLDOUT_RULE_WOULD_PASS={'YES' if holdout_pass else 'NO'}")
    print(f"Structural failures: {len(structural_failures)}")
    print(f"Holm-rejected tests: {len(hypothesis_failures)} / {len(p_records)}")
    print(f"Practical-equivalence failures: {len(practical_failures)}")
    print(f"SMD failures: {len(smd_failures)}")
    print(f"KS_D failures: {len(ks_d_failures)}")

    print("\nLargest |SMD| values:")
    for row in sorted(primary, key=lambda r: abs(r["smd"]), reverse=True)[:10]:
        print(f"  {row['observable']:28s} {row['smd']:+.6f}")

    print("\nLargest KS_D values:")
    for row in sorted(primary, key=lambda r: r["ks_D"], reverse=True)[:10]:
        print(f"  {row['observable']:28s} {row['ks_D']:.6f}")

    if args.validation_mode == "diagnostic":
        return 0
    return 0 if holdout_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
