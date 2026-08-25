#!/usr/bin/env python3

import json
import math
import re
import sys
from pathlib import Path


REF_VALUE = 12.0403
REF_ERROR = 0.0201

MAX_INDIVIDUAL_RELERR_PCT = 10.0
MAX_COMBINED_RELERR_PCT = 2.0
MAX_PAIR_PULL = 3.0
MAX_REFERENCE_PULL = 3.0

MODES = [
    ("F5_S0", "F5", "S0", 5),
    ("F5_S1", "F5", "S1", 5),
    ("F5_S2", "F5", "S2", 5),
    ("F6_S0", "F6", "S0", 6),
    ("F6_S1", "F6", "S1", 6),
    ("F6_S2", "F6", "S2", 6),
    ("F7_S0", "F7", "S0", 7),
    ("F7_S1", "F7", "S1", 7),
    ("F7_S2", "F7", "S2", 7),
]

ROW_RE = re.compile(
    r"^\s*"
    r"(?P<iteration>\d+)\s+"
    r"(?P<calls>\d+)\s+"
    r"(?P<value>[+-]?\d+(?:\.\d+)?E[+-]\d+)\s+"
    r"(?P<error>\d+(?:\.\d+)?E[+-]\d+)"
)


def relerr_pct(value, error):
    return 100.0 * abs(error / value)


def pull(v1, e1, v2, e2):
    denom = math.sqrt(e1 * e1 + e2 * e2)

    if denom == 0:
        return math.inf if v1 != v2 else 0.0

    return abs(v1 - v2) / denom


def parse_rows(path):
    by_iteration = {}

    with path.open() as f:
        for line in f:
            m = ROW_RE.match(line)

            if not m:
                continue

            row = {
                "iteration": int(m.group("iteration")),
                "calls": int(m.group("calls")),
                "value": float(m.group("value")),
                "error": float(m.group("error")),
                "raw": line.rstrip(),
            }

            by_iteration.setdefault(
                row["iteration"],
                [],
            ).append(row)

    return by_iteration


def finite_positive(row):
    return (
        math.isfinite(row["value"])
        and math.isfinite(row["error"])
        and row["value"] > 0
        and row["error"] >= 0
    )


if len(sys.argv) != 2:
    raise SystemExit(
        "usage: qualify_f_series.py F_OUT"
    )

root = Path(sys.argv[1])

if not root.is_dir():
    raise SystemExit(f"ERROR: missing F_OUT: {root}")

results = []


for mode, family, seed_name, nadapt in MODES:

    mode_dir = root / mode
    log = mode_dir / "console.log"
    meta_path = mode_dir / "metadata.json"

    failures = []

    execution_pass = (
        (mode_dir / "EXECUTION_SUCCESS").is_file()
        and meta_path.is_file()
    )

    if not execution_pass:
        failures.append("execution_not_pass")

    metadata = {}

    if meta_path.is_file():
        metadata = json.loads(
            meta_path.read_text()
        )

        if metadata.get("whizard_rc") != 0:
            execution_pass = False
            failures.append(
                "whizard_rc_nonzero"
            )

    if not log.is_file():
        failures.append("console_log_missing")

        results.append({
            "mode": mode,
            "family": family,
            "seed_name": seed_name,
            "execution_pass": execution_pass,
            "integration_pass": False,
            "failures": failures,
        })

        continue

    rows = parse_rows(log)

    fixed_iterations = [
        nadapt + 1,
        nadapt + 2,
        nadapt + 3,
    ]

    individual = []

    for it in fixed_iterations:
        candidates = rows.get(it, [])

        if not candidates:
            failures.append(
                f"fixed_iteration_{it}_missing"
            )
            continue

        # First occurrence is the individual iteration.
        # For the final fixed iteration, WHIZARD then prints
        # a second aggregate row with the same iteration number.
        individual.append(candidates[0])

    final_candidates = rows.get(
        nadapt + 3,
        [],
    )

    combined = (
        final_candidates[1]
        if len(final_candidates) >= 2
        else None
    )

    if combined is None:
        failures.append(
            "combined_fixed_result_missing"
        )

    if len(individual) == 3:

        for idx, row in enumerate(
            individual,
            start=1,
        ):
            if not finite_positive(row):
                failures.append(
                    f"fixed_{idx}_nonfinite_or_nonpositive"
                )
                continue

            r = relerr_pct(
                row["value"],
                row["error"],
            )

            if not (
                r < MAX_INDIVIDUAL_RELERR_PCT
            ):
                failures.append(
                    f"fixed_{idx}_relerr_ge_"
                    f"{MAX_INDIVIDUAL_RELERR_PCT:g}pct"
                )

    pair_pulls = []

    if len(individual) == 3:
        for i in range(3):
            for j in range(i + 1, 3):
                p = pull(
                    individual[i]["value"],
                    individual[i]["error"],
                    individual[j]["value"],
                    individual[j]["error"],
                )

                pair_pulls.append(p)

                if not (p < MAX_PAIR_PULL):
                    failures.append(
                        f"fixed_pair_{i+1}_{j+1}_"
                        f"pull_ge_{MAX_PAIR_PULL:g}"
                    )

    reference_pull = None
    combined_relerr = None

    if combined is not None:

        if not finite_positive(combined):
            failures.append(
                "combined_nonfinite_or_nonpositive"
            )

        else:
            combined_relerr = relerr_pct(
                combined["value"],
                combined["error"],
            )

            if not (
                combined_relerr
                < MAX_COMBINED_RELERR_PCT
            ):
                failures.append(
                    "combined_relerr_ge_"
                    f"{MAX_COMBINED_RELERR_PCT:g}pct"
                )

            reference_pull = pull(
                combined["value"],
                combined["error"],
                REF_VALUE,
                REF_ERROR,
            )

            if not (
                reference_pull
                < MAX_REFERENCE_PULL
            ):
                failures.append(
                    "reference_pull_ge_"
                    f"{MAX_REFERENCE_PULL:g}"
                )

    integration_pass = (
        execution_pass
        and len(failures) == 0
    )

    result = {
        "mode": mode,
        "family": family,
        "seed_name": seed_name,
        "seed": metadata.get("seed"),
        "condor_cluster_id":
            metadata.get("condor_cluster_id"),
        "condor_proc_id":
            metadata.get("condor_proc_id"),
        "execution_pass":
            execution_pass,
        "integration_pass":
            integration_pass,
        "fixed_iterations":
            fixed_iterations,
        "individual_fixed":
            individual,
        "combined_fixed":
            combined,
        "combined_relerr_pct":
            combined_relerr,
        "max_pair_pull":
            max(pair_pulls)
            if pair_pulls else None,
        "reference_pull":
            reference_pull,
        "failures":
            failures,
    }

    results.append(result)


families = {}

for family in ("F5", "F6", "F7"):
    members = [
        r for r in results
        if r["family"] == family
    ]

    families[family] = {
        "pass": (
            len(members) == 3
            and all(
                r["integration_pass"]
                for r in members
            )
        ),
        "members": [
            r["mode"] for r in members
        ],
    }


json_out = root / "F_SERIES_QUALIFICATION.json"

json_out.write_text(
    json.dumps(
        {
            "reference": {
                "value_fb": REF_VALUE,
                "error_fb": REF_ERROR,
            },
            "criteria": {
                "max_individual_relerr_pct":
                    MAX_INDIVIDUAL_RELERR_PCT,
                "max_combined_relerr_pct":
                    MAX_COMBINED_RELERR_PCT,
                "max_pair_pull":
                    MAX_PAIR_PULL,
                "max_reference_pull":
                    MAX_REFERENCE_PULL,
            },
            "results": results,
            "families": families,
        },
        indent=2,
        sort_keys=True,
    )
    + "\n"
)


tsv_out = root / "F_SERIES_QUALIFICATION.tsv"

with tsv_out.open("w") as f:

    f.write(
        "mode\tfamily\tseed\t"
        "execution\tintegration\t"
        "fixed_value_fb\tfixed_error_fb\t"
        "fixed_relerr_pct\t"
        "max_pair_pull\t"
        "reference_pull\t"
        "failures\n"
    )

    for r in results:

        c = r.get("combined_fixed")

        f.write(
            f"{r['mode']}\t"
            f"{r['family']}\t"
            f"{r.get('seed')}\t"
            f"{'PASS' if r['execution_pass'] else 'FAIL'}\t"
            f"{'PASS' if r['integration_pass'] else 'FAIL'}\t"
            f"{c['value'] if c else ''}\t"
            f"{c['error'] if c else ''}\t"
            f"{r.get('combined_relerr_pct') or ''}\t"
            f"{r.get('max_pair_pull') or ''}\t"
            f"{r.get('reference_pull') or ''}\t"
            f"{','.join(r['failures'])}\n"
        )


summary_out = (
    root / "F_SERIES_QUALIFICATION_SUMMARY.txt"
)

with summary_out.open("w") as f:

    f.write(
        "Phase 11 F-series frozen-criteria qualification\n\n"
    )

    f.write(
        f"Reference = {REF_VALUE:.4f} "
        f"+/- {REF_ERROR:.4f} fb\n\n"
    )

    f.write(
        "          S0      S1      S2      FAMILY\n"
    )

    f.write(
        "------------------------------------------\n"
    )

    for family in ("F5", "F6", "F7"):

        states = []

        for seed_name in ("S0", "S1", "S2"):
            r = next(
                x for x in results
                if (
                    x["family"] == family
                    and x["seed_name"] == seed_name
                )
            )

            states.append(
                "PASS"
                if r["integration_pass"]
                else "FAIL"
            )

        family_state = (
            "PASS"
            if families[family]["pass"]
            else "FAIL"
        )

        f.write(
            f"{family:<8}"
            f"{states[0]:<8}"
            f"{states[1]:<8}"
            f"{states[2]:<8}"
            f"{family_state}\n"
        )

    f.write("\nDetailed results:\n\n")

    for r in results:

        c = r.get("combined_fixed")

        f.write(
            f"{r['mode']}:\n"
            f"  execution = "
            f"{'PASS' if r['execution_pass'] else 'FAIL'}\n"
            f"  integration = "
            f"{'PASS' if r['integration_pass'] else 'FAIL'}\n"
        )

        if c:
            f.write(
                f"  combined fixed = "
                f"{c['value']:.8g} +/- "
                f"{c['error']:.5g} fb\n"
                f"  combined relerr = "
                f"{r['combined_relerr_pct']:.3f}%\n"
                f"  max pair pull = "
                f"{r['max_pair_pull']:.3f}\n"
                f"  reference pull = "
                f"{r['reference_pull']:.3f}\n"
            )

        if r["failures"]:
            f.write(
                "  failures = "
                + ", ".join(r["failures"])
                + "\n"
            )

        f.write("\n")


print(f"WROTE={json_out}")
print(f"WROTE={tsv_out}")
print(f"WROTE={summary_out}")

print()
print(summary_out.read_text())
