#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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
    x
    for group in OBSERVABLE_GROUPS.values()
    for x in group
]

REQUIRED_PDGS = {
    "b": 5,
    "bbar": -5,
    "eplus": -11,
    "nue": 12,
    "muminus": 13,
    "numubar": -14,
}


def add(*vecs):
    return np.sum(np.asarray(vecs, dtype=float), axis=0)


def p3(v):
    return np.asarray(v[1:4], dtype=float)


def pt(v):
    return math.hypot(v[1], v[2])


def mass(v):
    m2 = v[0] * v[0] - np.dot(v[1:4], v[1:4])
    return math.sqrt(max(m2, 0.0))


def eta(v):
    transverse = pt(v)
    if transverse == 0:
        return math.copysign(float("inf"), v[3])
    return math.asinh(v[3] / transverse)


def phi(v):
    return math.atan2(v[2], v[1])


def rapidity(v):
    num = v[0] + v[3]
    den = v[0] - v[3]
    if num <= 0 or den <= 0:
        return float("nan")
    return 0.5 * math.log(num / den)


def unit(x):
    n = np.linalg.norm(x)
    if n == 0:
        return np.array([np.nan, np.nan, np.nan])
    return x / n


def boost_to_rest(v, parent):
    beta = np.asarray(parent[1:4], dtype=float) / parent[0]
    b2 = float(np.dot(beta, beta))

    if b2 <= 0:
        return np.asarray(v, dtype=float).copy()

    if b2 >= 1:
        return np.full(4, np.nan)

    gamma = 1.0 / math.sqrt(1.0 - b2)

    e = float(v[0])
    p = np.asarray(v[1:4], dtype=float)

    bp = float(np.dot(beta, p))

    factor = ((gamma - 1.0) * bp / b2) - gamma * e

    out_p = p + factor * beta
    out_e = gamma * (e - bp)

    return np.array(
        [out_e, out_p[0], out_p[1], out_p[2]],
        dtype=float,
    )


def wrapped_abs_dphi(phi1, phi2):
    d = (phi1 - phi2 + math.pi) % (2 * math.pi) - math.pi
    return abs(d)


def cos_opening(a, b):
    ua = unit(p3(a))
    ub = unit(p3(b))
    return float(np.clip(np.dot(ua, ub), -1.0, 1.0))


def parse_event_block(lines):
    payload = [
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]

    if not payload:
        raise ValueError("empty event block")

    header = payload[0].split()

    nup = int(header[0])

    if len(payload) < nup + 1:
        raise ValueError(
            f"event declares {nup} particles but only "
            f"{len(payload)-1} lines exist"
        )

    particles = []

    for line in payload[1 : nup + 1]:
        c = line.split()

        if len(c) < 11:
            raise ValueError(
                f"particle record has too few columns: {line}"
            )

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

    selected = {}

    for name, pdg in REQUIRED_PDGS.items():
        matches = [p for p in final if p["pdg"] == pdg]

        if len(matches) != 1:
            raise ValueError(
                f"required final-state PDG {pdg} ({name}) "
                f"appears {len(matches)} times"
            )

        selected[name] = matches[0]["v"]

    return selected


def compute_observables(x):
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

    dr = math.sqrt(
        (eta(ep) - eta(mum)) ** 2 + dphi ** 2
    )

    # Helicity-frame construction:
    #
    #   lab -> ttbar rest frame -> parent-top rest frame
    #
    # The helicity axis is the corresponding top direction in the
    # ttbar rest frame.  The charged lepton is therefore transformed
    # through the same sequential frame construction before evaluating
    # the helicity angle.
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

    c_plus = float(
        np.clip(
            np.dot(lep_plus_dir, axis_top),
            -1.0,
            1.0,
        )
    )

    c_minus = float(
        np.clip(
            np.dot(lep_minus_dir, axis_tbar),
            -1.0,
            1.0,
        )
    )

    return {
        "pt_eplus": pt(ep),
        "pt_muminus": pt(mum),
        "eta_eplus": eta(ep),
        "eta_muminus": eta(mum),
        "energy_eplus": ep[0],
        "energy_muminus": mum[0],
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


def read_lhe(path):
    path = Path(path)

    values = {name: [] for name in OBSERVABLES}
    hashes = []
    issues = []

    inside = False
    block = []
    event_index = 0

    with path.open() as f:
        for raw in f:
            stripped = raw.strip()

            if stripped.startswith("<event"):
                inside = True
                block = []
                continue

            if stripped.startswith("</event"):
                event_index += 1

                block_text = "".join(block)

                hashes.append(
                    hashlib.sha256(
                        block_text.encode("utf-8")
                    ).hexdigest()
                )

                try:
                    selected = parse_event_block(block)
                    obs = compute_observables(selected)

                    for k, v in obs.items():
                        values[k].append(v)

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

    arrays = {
        k: np.asarray(v, dtype=float)
        for k, v in values.items()
    }

    return {
        "path": str(path),
        "events_seen": event_index,
        "issues": issues,
        "hashes": hashes,
        "arrays": arrays,
    }


def quantile_chi2(a, b, n_bins=30):
    pooled = np.concatenate([a, b])

    q = np.linspace(0, 1, n_bins + 1)

    edges = np.unique(
        np.quantile(pooled, q)
    )

    if len(edges) < 3:
        return 0.0, 1.0, len(edges) - 1

    edges[0] = -np.inf
    edges[-1] = np.inf

    ca, _ = np.histogram(a, bins=edges)
    cb, _ = np.histogram(b, bins=edges)

    table = np.vstack([ca, cb])

    keep = table.sum(axis=0) > 0
    table = table[:, keep]

    if table.shape[1] < 2:
        return 0.0, 1.0, table.shape[1]

    chi2, p, _, _ = stats.chi2_contingency(
        table,
        correction=False,
    )

    return float(chi2), float(p), table.shape[1]


def effect_metrics(a, b):
    pooled = np.concatenate([a, b])

    var_a = np.var(a, ddof=1)
    var_b = np.var(b, ddof=1)

    pooled_sd = math.sqrt(
        (
            (len(a) - 1) * var_a
            + (len(b) - 1) * var_b
        )
        / (len(a) + len(b) - 2)
    )

    smd = (
        (np.mean(a) - np.mean(b)) / pooled_sd
        if pooled_sd > 0
        else 0.0
    )

    q25, q75 = np.quantile(
        pooled,
        [0.25, 0.75],
    )

    scale = q75 - q25

    if scale <= 0:
        scale = np.std(pooled, ddof=1)

    if scale <= 0:
        scale = 1.0

    qa = np.quantile(a, [0.05, 0.50, 0.95])
    qb = np.quantile(b, [0.05, 0.50, 0.95])

    qshift = (qa - qb) / scale

    return {
        "mean_a": float(np.mean(a)),
        "mean_b": float(np.mean(b)),
        "std_a": float(np.std(a, ddof=1)),
        "std_b": float(np.std(b, ddof=1)),
        "smd": float(smd),
        "q05_shift_iqr": float(qshift[0]),
        "q50_shift_iqr": float(qshift[1]),
        "q95_shift_iqr": float(qshift[2]),
    }


def holm_bonferroni(records, alpha=0.01):
    n = len(records)

    order = sorted(
        range(n),
        key=lambda i: records[i]["p_value"],
    )

    rejected = [False] * n
    adjusted = [1.0] * n

    running_adj = 0.0
    keep_rejecting = True

    for rank, idx in enumerate(order):
        p = records[idx]["p_value"]

        factor = n - rank

        adj = min(1.0, factor * p)

        running_adj = max(running_adj, adj)
        adjusted[idx] = running_adj

        threshold = alpha / factor

        if keep_rejecting and p <= threshold:
            rejected[idx] = True
        else:
            keep_rejecting = False

    return rejected, adjusted


def compare(a, b, label):
    rows = []

    for obs in OBSERVABLES:
        x = a[obs]
        y = b[obs]

        ks = stats.ks_2samp(
            x,
            y,
            alternative="two-sided",
            method="asymp",
        )

        chi2, chi2_p, n_bins = quantile_chi2(x, y)

        eff = effect_metrics(x, y)

        row = {
            "comparison": label,
            "observable": obs,
            "n_a": len(x),
            "n_b": len(y),
            "ks_D": float(ks.statistic),
            "ks_p": float(ks.pvalue),
            "chi2": chi2,
            "chi2_p": chi2_p,
            "chi2_bins": n_bins,
            **eff,
        }

        rows.append(row)

    return rows


def make_overlays(single, multi, outdir):
    outdir.mkdir(parents=True, exist_ok=True)

    for obs in OBSERVABLES:
        a = single[obs]
        b = multi[obs]

        pooled = np.concatenate([a, b])

        lo, hi = np.quantile(
            pooled,
            [0.001, 0.999],
        )

        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            lo = np.nanmin(pooled)
            hi = np.nanmax(pooled)

        bins = np.linspace(lo, hi, 51)

        h1, edges = np.histogram(
            a,
            bins=bins,
            density=True,
        )

        h2, _ = np.histogram(
            b,
            bins=bins,
            density=True,
        )

        centers = 0.5 * (edges[:-1] + edges[1:])

        fig = plt.figure(figsize=(8, 7))

        gs = fig.add_gridspec(
            2,
            1,
            height_ratios=[3, 1],
            hspace=0.05,
        )

        ax = fig.add_subplot(gs[0])
        rx = fig.add_subplot(gs[1], sharex=ax)

        ax.step(
            centers,
            h1,
            where="mid",
            label="Single grid: S0_A + S0_B",
        )

        ax.step(
            centers,
            h2,
            where="mid",
            label="Multi-grid: S1 + S2",
        )

        ax.set_ylabel("Normalized density")
        ax.set_title(obs)
        ax.legend()

        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(
                h2 > 0,
                h1 / h2,
                np.nan,
            )

        rx.axhline(1.0, linewidth=1)
        rx.plot(centers, ratio, marker=".", linestyle="none")

        rx.set_ylabel("S/M")
        rx.set_xlabel(obs)
        rx.set_ylim(0.5, 1.5)

        fig.savefig(
            outdir / f"{obs}.png",
            dpi=160,
            bbox_inches="tight",
        )

        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--s0-a", required=True)
    ap.add_argument("--s0-b", required=True)
    ap.add_argument("--s1", required=True)
    ap.add_argument("--s2", required=True)
    ap.add_argument("--outdir", required=True)

    args = ap.parse_args()

    outdir = Path(args.outdir)
    plotdir = outdir / "plots"

    outdir.mkdir(parents=True, exist_ok=True)

    component_paths = {
        "S0_A": args.s0_a,
        "S0_B": args.s0_b,
        "S1_A": args.s1,
        "S2_A": args.s2,
    }

    data = {}

    for name, path in component_paths.items():
        print(f"Reading {name}: {path}")
        data[name] = read_lhe(path)

    structural_failures = []

    component_summary = []

    for name, d in data.items():
        nonfinite = {}

        for obs, arr in d["arrays"].items():
            n_bad = int(np.sum(~np.isfinite(arr)))
            if n_bad:
                nonfinite[obs] = n_bad

        row = {
            "sample": name,
            "path": d["path"],
            "events_seen": d["events_seen"],
            "events_parsed": len(
                d["arrays"][OBSERVABLES[0]]
            ),
            "parse_issues": len(d["issues"]),
            "nonfinite_observables": nonfinite,
        }

        component_summary.append(row)

        if d["events_seen"] != 10000:
            structural_failures.append(
                f"{name}: events_seen={d['events_seen']}"
            )

        if len(d["issues"]) != 0:
            structural_failures.append(
                f"{name}: parse_issues={len(d['issues'])}"
            )

        if nonfinite:
            structural_failures.append(
                f"{name}: nonfinite={nonfinite}"
            )

    # Exact event-block overlap diagnostics.
    overlap_rows = []

    names = list(data)

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]

            n_overlap = len(
                set(data[a]["hashes"])
                & set(data[b]["hashes"])
            )

            overlap_rows.append(
                {
                    "sample_a": a,
                    "sample_b": b,
                    "exact_event_overlap": n_overlap,
                }
            )

            if n_overlap != 0:
                structural_failures.append(
                    f"{a}/{b}: exact_event_overlap={n_overlap}"
                )

    single = {
        obs: np.concatenate(
            [
                data["S0_A"]["arrays"][obs],
                data["S0_B"]["arrays"][obs],
            ]
        )
        for obs in OBSERVABLES
    }

    multi = {
        obs: np.concatenate(
            [
                data["S1_A"]["arrays"][obs],
                data["S2_A"]["arrays"][obs],
            ]
        )
        for obs in OBSERVABLES
    }

    primary = compare(
        single,
        multi,
        "SINGLE_S0AB_vs_MULTI_S1S2",
    )

    internal_s0 = compare(
        data["S0_A"]["arrays"],
        data["S0_B"]["arrays"],
        "S0_A_vs_S0_B",
    )

    internal_multi = compare(
        data["S1_A"]["arrays"],
        data["S2_A"]["arrays"],
        "S1_A_vs_S2_A",
    )

    # One Holm family containing both KS and chi-square tests.
    p_records = []

    for row in primary:
        p_records.append(
            {
                "observable": row["observable"],
                "test": "KS",
                "p_value": row["ks_p"],
            }
        )
        p_records.append(
            {
                "observable": row["observable"],
                "test": "CHI2",
                "p_value": row["chi2_p"],
            }
        )

    rejected, adjusted = holm_bonferroni(
        p_records,
        alpha=0.01,
    )

    for rec, rej, adj in zip(
        p_records,
        rejected,
        adjusted,
    ):
        rec["holm_reject"] = bool(rej)
        rec["holm_adjusted_p"] = float(adj)

    lookup = {
        (r["observable"], r["test"]): r
        for r in p_records
    }

    effect_failures = []

    for row in primary:
        obs = row["observable"]

        row["ks_holm_reject"] = lookup[
            (obs, "KS")
        ]["holm_reject"]

        row["ks_holm_adjusted_p"] = lookup[
            (obs, "KS")
        ]["holm_adjusted_p"]

        row["chi2_holm_reject"] = lookup[
            (obs, "CHI2")
        ]["holm_reject"]

        row["chi2_holm_adjusted_p"] = lookup[
            (obs, "CHI2")
        ]["holm_adjusted_p"]

        qmax = max(
            abs(row["q05_shift_iqr"]),
            abs(row["q50_shift_iqr"]),
            abs(row["q95_shift_iqr"]),
        )

        row["max_abs_quantile_shift_iqr"] = qmax

        row["smd_pass"] = abs(row["smd"]) <= 0.05
        row["quantile_pass"] = qmax <= 0.10

        if not row["smd_pass"]:
            effect_failures.append(
                f"{obs}: |SMD|={abs(row['smd']):.6g}"
            )

        if not row["quantile_pass"]:
            effect_failures.append(
                f"{obs}: max normalized quantile shift="
                f"{qmax:.6g}"
            )

    hypothesis_failures = [
        f"{r['observable']}:{r['test']}"
        for r in p_records
        if r["holm_reject"]
    ]

    overall_pass = (
        not structural_failures
        and not hypothesis_failures
        and not effect_failures
    )

    # Save primary table.
    primary_fields = list(primary[0].keys())

    with (outdir / "observable_comparison.tsv").open(
        "w",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=primary_fields,
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(primary)

    # Save internal diagnostic table.
    internal = internal_s0 + internal_multi

    with (outdir / "component_diagnostics.tsv").open(
        "w",
        newline="",
    ) as f:
        fields = list(internal[0].keys())

        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(internal)

    with (outdir / "event_overlap.tsv").open(
        "w",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_a",
                "sample_b",
                "exact_event_overlap",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(overlap_rows)

    # Parse issues.
    with (outdir / "parse_issues.tsv").open(
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            ["sample", "event_index", "error"]
        )

        for name, d in data.items():
            for issue in d["issues"]:
                writer.writerow(
                    [
                        name,
                        issue["event_index"],
                        issue["error"],
                    ]
                )

    make_overlays(single, multi, plotdir)

    # Effect summary plot.
    labels = [row["observable"] for row in primary]
    smd = np.array([row["smd"] for row in primary])

    fig, ax = plt.subplots(
        figsize=(8, max(6, 0.32 * len(labels)))
    )

    y = np.arange(len(labels))

    ax.axvline(0.0, linewidth=1)
    ax.axvline(-0.05, linestyle="--", linewidth=1)
    ax.axvline(+0.05, linestyle="--", linewidth=1)

    ax.plot(
        smd,
        y,
        marker="o",
        linestyle="none",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Standardized mean difference: single - multi")
    ax.set_title("Phase 11C single-grid vs multi-grid effects")

    fig.savefig(
        plotdir / "summary_standardized_mean_differences.png",
        dpi=170,
        bbox_inches="tight",
    )

    plt.close(fig)

    # Save component observables.
    npz = {}

    for sample, d in data.items():
        for obs, arr in d["arrays"].items():
            npz[f"{sample}__{obs}"] = arr

    np.savez_compressed(
        outdir / "component_observables.npz",
        **npz,
    )

    result = {
        "schema_version": 1,
        "gate": "PASS" if overall_pass else "FAIL",
        "familywise_alpha": 0.01,
        "holm_test_count": len(p_records),
        "samples": component_summary,
        "structural_failures": structural_failures,
        "hypothesis_failures": hypothesis_failures,
        "effect_failures": effect_failures,
        "observable_groups": OBSERVABLE_GROUPS,
        "thresholds": {
            "abs_smd_max": 0.05,
            "abs_quantile_shift_over_iqr_max": 0.10,
        },
    }

    (outdir / "VALIDATION_RESULT.json").write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    with (
        outdir / "VALIDATION_SUMMARY.txt"
    ).open("w") as f:
        f.write(
            f"PHASE11C_SINGLE_VS_MULTIGRID="
            f"{'PASS' if overall_pass else 'FAIL'}\n\n"
        )

        f.write(
            f"Structural failures: "
            f"{len(structural_failures)}\n"
        )

        for x in structural_failures:
            f.write(f"  {x}\n")

        f.write(
            f"\nHolm-rejected tests: "
            f"{len(hypothesis_failures)}\n"
        )

        for x in hypothesis_failures:
            f.write(f"  {x}\n")

        f.write(
            f"\nEffect-size failures: "
            f"{len(effect_failures)}\n"
        )

        for x in effect_failures:
            f.write(f"  {x}\n")

        f.write("\nWorst standardized mean differences:\n")

        for row in sorted(
            primary,
            key=lambda r: abs(r["smd"]),
            reverse=True,
        )[:10]:
            f.write(
                f"  {row['observable']:28s} "
                f"SMD={row['smd']:+.6f} "
                f"KS_D={row['ks_D']:.6f} "
                f"KS_p={row['ks_p']:.6g}\n"
            )

    print(
        "PHASE11C_SINGLE_VS_MULTIGRID="
        + ("PASS" if overall_pass else "FAIL")
    )

    print(
        f"Structural failures: "
        f"{len(structural_failures)}"
    )

    print(
        f"Holm-rejected tests: "
        f"{len(hypothesis_failures)}"
    )

    print(
        f"Effect-size failures: "
        f"{len(effect_failures)}"
    )

    print("\nLargest |SMD| values:")

    for row in sorted(
        primary,
        key=lambda r: abs(r["smd"]),
        reverse=True,
    )[:10]:
        print(
            f"  {row['observable']:28s} "
            f"{row['smd']:+.6f}"
        )


if __name__ == "__main__":
    main()
