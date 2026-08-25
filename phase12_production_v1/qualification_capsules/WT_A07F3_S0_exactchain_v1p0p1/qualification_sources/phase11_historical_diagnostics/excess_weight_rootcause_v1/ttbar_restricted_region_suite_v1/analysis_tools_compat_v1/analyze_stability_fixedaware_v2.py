#!/usr/bin/env python3
"""
Fixed-aware numerical stability analyzer for Phase-11 WHIZARD campaigns.

This supersedes the original analyze_stability.py for post-run analysis.

Problem corrected
-----------------
A reused-grid fixed child contains:

  1. the inherited parent adaptive iteration history,
  2. the inherited parent aggregate result,
  3. newly executed fixed-grid validation iteration(s),
  4. a final WHIZARD result/summary.

The old analyzer preferred the last row classified as "aggregate".  For
reused-grid jobs this could select the inherited parent aggregate rather than
the new fixed result.

This analyzer instead:

  * sorts all numerical rows by WHIZARD log line number;
  * uses the last numerical row as the final result;
  * for fixed children, identifies the first explicit parent aggregate as the
    inherited-history boundary;
  * evaluates fixed-stage numerical diagnostics only on the newly executed
    fixed segment;
  * preserves parent-screen information separately;
  * supports both:
        - the old 480-scan collector schema, where identifier == mode
        - the new suite collector schema, where identifier == node

No campaign inputs, grids, or WHIZARD outputs are modified.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path


ROW_RE = re.compile(
    r"^\s*"
    r"(?P<iteration>\d+)\s+"
    r"(?P<calls>\d+)\s+"
    r"(?P<integral>[+-]?\d+(?:\.\d*)?[Ee][+-]\d+)\s+"
    r"(?P<error>[+-]?\d+(?:\.\d*)?[Ee][+-]\d+)\s+"
    r"(?P<errpct>[+-]?\d+(?:\.\d*)?)\s+"
    r"(?P<acc>[+-]?\d+(?:\.\d*)?)\*?\s+"
    r"(?P<eff>[+-]?\d+(?:\.\d*)?)"
    r"(?P<tail>.*)$"
)


NUMERIC_FIELDS = (
    "integral_fb",
    "error_fb",
    "reported_err_pct",
    "accuracy",
    "efficiency_pct",
)


def write_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("")
        return

    fields: list[str] = []

    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)

    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def as_float(value, default=math.nan) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value, default=-1) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_row(row: dict) -> dict:
    out = dict(row)

    out["line_number"] = as_int(
        out.get("line_number")
    )

    out["iteration"] = as_int(
        out.get("iteration")
    )

    out["calls"] = as_int(
        out.get("calls")
    )

    for key in NUMERIC_FIELDS:
        out[key] = as_float(
            out.get(key)
        )

    if math.isfinite(out["integral_fb"]) and out["integral_fb"] != 0:
        out["relative_error"] = abs(
            out["error_fb"] / out["integral_fb"]
        )
    else:
        out["relative_error"] = math.inf

    return out


def explicit_aggregate(row: dict) -> bool:
    """
    WHIZARD's ordinary parent aggregate line has additional fields after
    efficiency, e.g.

      ... 0.85  4.25  6.14  0.15  5

    The final duplicate summary after a one-pass fixed continuation may not
    have those trailing fields, so this is used only to identify the
    parent-history boundary.
    """

    raw = row.get("raw_line", "")

    match = ROW_RE.match(raw)

    if not match:
        return False

    tail = match.group("tail").strip().split()

    return len(tail) >= 2


def same_numeric_result(a: dict, b: dict) -> bool:
    if (
        a["iteration"] != b["iteration"]
        or a["calls"] != b["calls"]
    ):
        return False

    for key in (
        "integral_fb",
        "error_fb",
        "reported_err_pct",
        "accuracy",
        "efficiency_pct",
    ):
        av = a[key]
        bv = b[key]

        if not (
            math.isfinite(av)
            and math.isfinite(bv)
        ):
            return False

        scale = max(
            1.0,
            abs(av),
            abs(bv),
        )

        if abs(av - bv) > 1.0e-12 * scale:
            return False

    return True


def physical_iteration_rows(
    rows: list[dict],
) -> list[dict]:
    """
    Remove WHIZARD summary/aggregate rows while retaining genuinely executed
    integration passes.

    Rules:
      * explicit aggregate rows are summaries;
      * if a later row exactly duplicates the preceding numerical result,
        the later row is a final printout/summary and is removed.
    """

    if not rows:
        return []

    result: list[dict] = []

    for i, row in enumerate(rows):
        if explicit_aggregate(row):
            continue

        if (
            i > 0
            and same_numeric_result(
                rows[i - 1],
                row,
            )
        ):
            # Later duplicate = WHIZARD final summary print.
            continue

        result.append(row)

    return result


def split_fixed_history(
    rows: list[dict],
) -> tuple[list[dict], list[dict], str]:
    """
    Split a fixed child into inherited parent history and newly executed fixed
    validation segment.

    Preferred boundary:
      first explicit WHIZARD aggregate in the inherited parent history.

    All rows after that aggregate belong to the requested fixed continuation.
    """

    for i, row in enumerate(rows):
        if explicit_aggregate(row):
            parent = rows[: i + 1]
            fixed = rows[i + 1 :]

            if fixed:
                return (
                    parent,
                    fixed,
                    "first_explicit_parent_aggregate",
                )

    # This should not occur for the current campaigns. Keep a visible fallback
    # rather than silently treating inherited rows as fixed validation.
    return (
        [],
        rows,
        "fallback_no_parent_aggregate",
    )


def normalized_jumps(
    rows: list[dict],
) -> list[float]:
    jumps = []

    for first, second in zip(
        rows,
        rows[1:],
    ):
        denominator = math.hypot(
            first["error_fb"],
            second["error_fb"],
        )

        if denominator > 0:
            jumps.append(
                abs(
                    second["integral_fb"]
                    - first["integral_fb"]
                )
                / denominator
            )
        else:
            jumps.append(math.inf)

    return jumps


def segment_metrics(
    segment_rows: list[dict],
    stage: str,
) -> dict:
    if not segment_rows:
        return {}

    segment_rows = sorted(
        segment_rows,
        key=lambda row: row["line_number"],
    )

    final = segment_rows[-1]

    iterations = physical_iteration_rows(
        segment_rows
    )

    if not iterations:
        iterations = [final]

    jumps = normalized_jumps(
        iterations
    )

    if stage == "adaptive":
        # Preserve original adaptive semantics:
        # first adaptive iteration is a warm-up and is omitted from this
        # trajectory maximum.
        error_rows = (
            iterations[1:]
            if len(iterations) > 1
            else iterations
        )
    else:
        # Every new fixed pass is a validation draw and therefore all of them
        # count toward the fixed-stage diagnostic.
        error_rows = iterations

    return {
        "n_segment_rows": len(segment_rows),
        "n_iteration_rows": len(iterations),
        "final_line_number": final["line_number"],
        "final_iteration": final["iteration"],
        "final_calls": final["calls"],
        "final_integral_fb": final["integral_fb"],
        "final_error_fb": final["error_fb"],
        "final_relative_error_pct": (
            100.0 * final["relative_error"]
        ),
        "max_postfirst_reported_error_pct": max(
            row["reported_err_pct"]
            for row in error_rows
        ),
        "max_accuracy": max(
            row["accuracy"]
            for row in iterations
        ),
        "min_efficiency_pct": min(
            row["efficiency_pct"]
            for row in iterations
        ),
        "max_normalized_iteration_jump": (
            max(jumps)
            if jumps
            else 0.0
        ),
    }


def screen_pass(
    metrics: dict,
    thresholds: dict,
) -> int:
    if not metrics:
        return 0

    cfg = thresholds["adaptive"]

    return int(
        metrics[
            "max_postfirst_reported_error_pct"
        ]
        <= cfg[
            "max_postfirst_reported_error_pct"
        ]
        and metrics["max_accuracy"]
        <= cfg["max_accuracy"]
        and metrics[
            "max_normalized_iteration_jump"
        ]
        <= cfg[
            "max_normalized_iteration_jump"
        ]
        and metrics[
            "final_relative_error_pct"
        ]
        <= cfg[
            "max_final_relative_error_pct"
        ]
    )


def weighted_family_summary(
    rows: list[dict],
) -> dict:
    finite = [
        row
        for row in rows
        if math.isfinite(
            row["final_integral_fb"]
        )
    ]

    values = [
        row["final_integral_fb"]
        for row in finite
    ]

    if len(values) > 1:
        mean_value = statistics.mean(values)

        if mean_value != 0:
            relative_range = (
                max(values) - min(values)
            ) / abs(mean_value)
        else:
            relative_range = math.inf
    else:
        relative_range = 0.0

    weighted = [
        row
        for row in finite
        if row["final_error_fb"] > 0
        and math.isfinite(
            row["final_error_fb"]
        )
    ]

    if weighted:
        sum_weight = sum(
            1.0
            / row["final_error_fb"] ** 2
            for row in weighted
        )

        weighted_mean = (
            sum(
                row["final_integral_fb"]
                / row["final_error_fb"] ** 2
                for row in weighted
            )
            / sum_weight
        )

        chi2 = sum(
            (
                row["final_integral_fb"]
                - weighted_mean
            )
            ** 2
            / row["final_error_fb"] ** 2
            for row in weighted
        )

        ndf = max(
            1,
            len(weighted) - 1,
        )

        weighted_error = math.sqrt(
            1.0 / sum_weight
        )

        reduced_chi2 = chi2 / ndf
    else:
        weighted_mean = math.nan
        weighted_error = math.nan
        reduced_chi2 = math.nan

    return {
        "n": len(rows),
        "screen_pass": sum(
            int(row["numerical_screen_pass"])
            for row in rows
        ),
        "grid_candidate_pass": sum(
            int(row["grid_candidate_screen_pass"])
            for row in rows
        ),
        "relative_range": relative_range,
        "reduced_chi2": reduced_chi2,
        "weighted_mean_fb": weighted_mean,
        "weighted_error_fb": weighted_error,
        "arithmetic_mean_fb": (
            statistics.mean(values)
            if values
            else math.nan
        ),
        "median_fb": (
            statistics.median(values)
            if values
            else math.nan
        ),
        "min_fb": (
            min(values)
            if values
            else math.nan
        ),
        "max_fb": (
            max(values)
            if values
            else math.nan
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--campaign-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--thresholds",
        type=Path,
        default=None,
    )

    args = parser.parse_args()

    campaign = args.campaign_dir.resolve()

    collected = campaign / "collected"
    output = campaign / "analysis"

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    threshold_path = (
        args.thresholds.resolve()
        if args.thresholds
        else campaign
        / "frozen_config"
        / "validation_thresholds.json"
    )

    if not threshold_path.is_file():
        raise SystemExit(
            f"ERROR: missing thresholds: {threshold_path}"
        )

    thresholds = json.loads(
        threshold_path.read_text()
    )

    rows_path = (
        collected
        / "iteration_rows.tsv"
    )

    if not rows_path.is_file():
        raise SystemExit(
            f"ERROR: missing {rows_path}"
        )

    with rows_path.open(newline="") as handle:
        source_rows = list(
            csv.DictReader(
                handle,
                delimiter="\t",
            )
        )

    grouped: dict[str, list[dict]] = defaultdict(list)

    for source in source_rows:
        try:
            row = normalize_row(source)

            identifier = (
                row.get("node")
                or row.get("mode")
            )

            if not identifier:
                continue

            grouped[identifier].append(row)

        except Exception:
            continue

    metrics: list[dict] = []

    for identifier, rows in grouped.items():
        rows.sort(
            key=lambda row: row["line_number"]
        )

        first = rows[0]

        stage = first.get(
            "stage",
            "",
        )

        inherited_rows: list[dict] = []

        if stage == "fixed":
            (
                inherited_rows,
                analysis_rows,
                boundary_method,
            ) = split_fixed_history(rows)
        else:
            analysis_rows = rows
            boundary_method = "full_adaptive_history"

        local_metrics = segment_metrics(
            analysis_rows,
            stage,
        )

        if not local_metrics:
            continue

        record = {
            "node": identifier,
            "stage": stage,
            "mode": first.get(
                "mode",
                "",
            ),
            "adaptive_id": first.get(
                "adaptive_id",
                "",
            ),
            "fixed_id": first.get(
                "fixed_id",
                "",
            ),
            "seed_id": first.get(
                "seed_id",
                "",
            ),
            "recipe_id": first.get(
                "recipe_id",
                "",
            ),
            "region_id": first.get(
                "region_id",
                "",
            ),
            "window_id": first.get(
                "window_id",
                "",
            ),
            "history_boundary_method": boundary_method,
            "n_total_log_rows": len(rows),
            "n_inherited_parent_rows": len(
                inherited_rows
            ),
        }

        record.update(
            local_metrics
        )

        record[
            "numerical_screen_pass"
        ] = screen_pass(
            local_metrics,
            thresholds,
        )

        metrics.append(record)

    # ------------------------------------------------------------------
    # Attach parent adaptive-screen status to fixed descendants.
    # ------------------------------------------------------------------

    parent_index: dict[
        tuple[str, str, str, str, str],
        dict,
    ] = {}

    for row in metrics:
        if row["stage"] != "adaptive":
            continue

        key = (
            row["adaptive_id"],
            row["seed_id"],
            row["recipe_id"],
            row["region_id"],
            row["window_id"],
        )

        parent_index[key] = row

    for row in metrics:
        if row["stage"] == "adaptive":
            row[
                "parent_numerical_screen_pass"
            ] = ""

            row[
                "grid_candidate_screen_pass"
            ] = row[
                "numerical_screen_pass"
            ]

            continue

        key = (
            row["adaptive_id"],
            row["seed_id"],
            row["recipe_id"],
            row["region_id"],
            row["window_id"],
        )

        parent = parent_index.get(key)

        parent_pass = (
            int(
                parent[
                    "numerical_screen_pass"
                ]
            )
            if parent
            else 0
        )

        row[
            "parent_numerical_screen_pass"
        ] = parent_pass

        row[
            "grid_candidate_screen_pass"
        ] = int(
            parent_pass
            and row[
                "numerical_screen_pass"
            ]
        )

    metrics.sort(
        key=lambda row: (
            row["stage"],
            row["window_id"],
            row["region_id"],
            row["recipe_id"],
            row["adaptive_id"],
            row["fixed_id"],
            row["seed_id"],
        )
    )

    metrics_path = (
        output
        / "node_numerical_metrics.tsv"
    )

    write_tsv(
        metrics_path,
        metrics,
    )

    # ------------------------------------------------------------------
    # Family summaries
    # ------------------------------------------------------------------

    families: dict[
        tuple[str, str, str, str, str, str],
        list[dict],
    ] = defaultdict(list)

    for row in metrics:
        key = (
            row["stage"],
            row["adaptive_id"],
            row["fixed_id"],
            row["recipe_id"],
            row["region_id"],
            row["window_id"],
        )

        families[key].append(row)

    family_rows: list[dict] = []

    family_cfg = thresholds["family"]

    for key, rows in sorted(
        families.items()
    ):
        summary = weighted_family_summary(
            rows
        )

        family_pass = int(
            summary["n"] > 0
            and summary["screen_pass"]
            == summary["n"]
            and summary["relative_range"]
            <= family_cfg[
                "max_final_integral_relative_range"
            ]
            and summary["reduced_chi2"]
            <= family_cfg[
                "max_reduced_chi2"
            ]
        )

        grid_family_pass = int(
            summary["n"] > 0
            and summary["grid_candidate_pass"]
            == summary["n"]
            and summary["relative_range"]
            <= family_cfg[
                "max_final_integral_relative_range"
            ]
            and summary["reduced_chi2"]
            <= family_cfg[
                "max_reduced_chi2"
            ]
        )

        family = {
            "stage": key[0],
            "adaptive_id": key[1],
            "fixed_id": key[2],
            "recipe_id": key[3],
            "region_id": key[4],
            "window_id": key[5],
        }

        family.update(
            summary
        )

        family[
            "family_screen_pass"
        ] = family_pass

        family[
            "grid_family_screen_pass"
        ] = grid_family_pass

        family_rows.append(
            family
        )

    family_path = (
        output
        / "family_stability.tsv"
    )

    write_tsv(
        family_path,
        family_rows,
    )

    # ------------------------------------------------------------------
    # F0/F1/F2 paired comparisons where available.
    # ------------------------------------------------------------------

    fixed_index = {
        (
            row["adaptive_id"],
            row["seed_id"],
            row["recipe_id"],
            row["region_id"],
            row["window_id"],
            row["fixed_id"],
        ): row
        for row in metrics
        if row["stage"] == "fixed"
    }

    pair_rows = []

    pair_defs = (
        ("F0", "F1"),
        ("F1", "F2"),
        ("F0", "F2"),
    )

    base_keys = sorted(
        set(
            (
                row["adaptive_id"],
                row["seed_id"],
                row["recipe_id"],
                row["region_id"],
                row["window_id"],
            )
            for row in metrics
            if row["stage"] == "fixed"
        )
    )

    for base in base_keys:
        for left_id, right_id in pair_defs:
            left = fixed_index.get(
                base + (left_id,)
            )

            right = fixed_index.get(
                base + (right_id,)
            )

            if not left or not right:
                continue

            difference = (
                left["final_integral_fb"]
                - right["final_integral_fb"]
            )

            denominator = math.hypot(
                left["final_error_fb"],
                right["final_error_fb"],
            )

            normalized = (
                difference / denominator
                if denominator > 0
                else math.nan
            )

            pair_rows.append(
                {
                    "adaptive_id": base[0],
                    "seed_id": base[1],
                    "recipe_id": base[2],
                    "region_id": base[3],
                    "window_id": base[4],
                    "left_fixed_id": left_id,
                    "right_fixed_id": right_id,
                    "left_integral_fb": left[
                        "final_integral_fb"
                    ],
                    "left_error_fb": left[
                        "final_error_fb"
                    ],
                    "right_integral_fb": right[
                        "final_integral_fb"
                    ],
                    "right_error_fb": right[
                        "final_error_fb"
                    ],
                    "difference_fb": difference,
                    "normalized_difference": normalized,
                }
            )

    pair_path = (
        output
        / "fixed_pair_comparison.tsv"
    )

    write_tsv(
        pair_path,
        pair_rows,
    )

    print(
        f"NODE_METRICS={metrics_path}"
    )

    print(
        f"FAMILY_STABILITY={family_path}"
    )

    print(
        f"FIXED_PAIR_COMPARISON={pair_path}"
    )

    print(
        f"NODES_ANALYZED={len(metrics)}"
    )

    print(
        f"FAMILIES_ANALYZED={len(family_rows)}"
    )

    print(
        f"FIXED_PAIRS={len(pair_rows)}"
    )

    print(
        "ANALYZE_STABILITY_FIXEDAWARE_V2=PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
