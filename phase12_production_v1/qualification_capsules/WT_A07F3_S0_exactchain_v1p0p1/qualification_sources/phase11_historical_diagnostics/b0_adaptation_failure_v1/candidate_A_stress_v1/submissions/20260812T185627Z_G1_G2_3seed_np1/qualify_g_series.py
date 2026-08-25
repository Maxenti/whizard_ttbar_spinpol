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
    ("G1_S0", "G1", "S0", 5, 5),
    ("G1_S1", "G1", "S1", 5, 5),
    ("G1_S2", "G1", "S2", 5, 5),
    ("G2_S0", "G2", "S0", 5, 3),
    ("G2_S1", "G2", "S1", 5, 3),
    ("G2_S2", "G2", "S2", 5, 3),
]

ROW_RE = re.compile(
    r"^\s*"
    r"(?P<iteration>\d+)\s+"
    r"(?P<calls>\d+)\s+"
    r"(?P<value>[+-]?\d+(?:\.\d+)?E[+-]\d+)\s+"
    r"(?P<error>\d+(?:\.\d+)?E[+-]\d+)"
)


def relerr(value, error):
    return 100.0 * abs(error / value)


def pull(v1, e1, v2, e2):
    d = math.sqrt(e1 * e1 + e2 * e2)
    return abs(v1 - v2) / d if d else math.inf


def parse_rows(path):
    rows = {}

    for line in path.read_text().splitlines():
        m = ROW_RE.match(line)

        if not m:
            continue

        r = {
            "iteration": int(m.group("iteration")),
            "calls": int(m.group("calls")),
            "value": float(m.group("value")),
            "error": float(m.group("error")),
            "raw": line,
        }

        rows.setdefault(
            r["iteration"], []
        ).append(r)

    return rows


if len(sys.argv) != 2:
    raise SystemExit(
        "usage: qualify_g_series.py G_OUT"
    )

root = Path(sys.argv[1])

results = []


for mode, family, seed_name, nadapt, nfixed in MODES:

    d = root / mode
    log = d / "console.log"
    meta_path = d / "metadata.json"

    failures = []

    metadata = {}

    if meta_path.is_file():
        metadata = json.loads(
            meta_path.read_text()
        )
    else:
        failures.append("metadata_missing")

    execution_pass = (
        (d / "EXECUTION_SUCCESS").is_file()
        and metadata.get("whizard_rc") == 0
    )

    if not execution_pass:
        failures.append("execution_not_pass")

    if not log.is_file():
        failures.append("console_log_missing")
        rows = {}
    else:
        rows = parse_rows(log)

    fixed = []

    for iteration in range(
        nadapt + 1,
        nadapt + nfixed + 1,
    ):
        candidates = rows.get(iteration, [])

        if not candidates:
            failures.append(
                f"fixed_iteration_{iteration}_missing"
            )
            continue

        fixed.append(candidates[0])

    final_iteration = nadapt + nfixed
    final_rows = rows.get(final_iteration, [])

    combined = (
        final_rows[1]
        if len(final_rows) >= 2
        else None
    )

    if combined is None:
        failures.append(
            "combined_fixed_result_missing"
        )

    for i, r in enumerate(fixed, start=1):

        if (
            not math.isfinite(r["value"])
            or not math.isfinite(r["error"])
            or r["value"] <= 0
            or r["error"] < 0
        ):
            failures.append(
                f"fixed_{i}_invalid"
            )
            continue

        if relerr(
            r["value"], r["error"]
        ) >= MAX_INDIVIDUAL_RELERR_PCT:

            failures.append(
                f"fixed_{i}_relerr_ge_10pct"
            )

    pair_pulls = []

    for i in range(len(fixed)):
        for j in range(i + 1, len(fixed)):

            p = pull(
                fixed[i]["value"],
                fixed[i]["error"],
                fixed[j]["value"],
                fixed[j]["error"],
            )

            pair_pulls.append(p)

            if p >= MAX_PAIR_PULL:
                failures.append(
                    f"fixed_pair_{i+1}_{j+1}_"
                    "pull_ge_3"
                )

    combined_relerr = None
    reference_pull = None

    if combined:

        combined_relerr = relerr(
            combined["value"],
            combined["error"],
        )

        if combined_relerr >= MAX_COMBINED_RELERR_PCT:
            failures.append(
                "combined_relerr_ge_2pct"
            )

        reference_pull = pull(
            combined["value"],
            combined["error"],
            REF_VALUE,
            REF_ERROR,
        )

        if reference_pull >= MAX_REFERENCE_PULL:
            failures.append(
                "reference_pull_ge_3"
            )

    integration_pass = (
        execution_pass
        and not failures
    )

    results.append({
        "mode": mode,
        "family": family,
        "seed_name": seed_name,
        "seed": metadata.get("seed"),
        "execution_pass": execution_pass,
        "integration_pass": integration_pass,
        "fixed": fixed,
        "combined": combined,
        "combined_relerr_pct": combined_relerr,
        "max_pair_pull": (
            max(pair_pulls)
            if pair_pulls else None
        ),
        "reference_pull": reference_pull,
        "failures": failures,
    })


family_results = {}

for family in ("G1", "G2"):

    members = [
        r for r in results
        if r["family"] == family
    ]

    family_results[family] = (
        len(members) == 3
        and all(
            r["integration_pass"]
            for r in members
        )
    )


json_path = root / "G_SERIES_QUALIFICATION.json"

json_path.write_text(
    json.dumps(
        {
            "reference": {
                "value_fb": REF_VALUE,
                "error_fb": REF_ERROR,
            },
            "results": results,
            "families": family_results,
        },
        indent=2,
        sort_keys=True,
    ) + "\n"
)


tsv_path = root / "G_SERIES_QUALIFICATION.tsv"

with tsv_path.open("w") as f:

    f.write(
        "mode\tfamily\tseed\t"
        "execution\tintegration\t"
        "fixed_value_fb\tfixed_error_fb\t"
        "fixed_relerr_pct\t"
        "max_pair_pull\t"
        "reference_pull\tfailures\n"
    )

    for r in results:

        c = r["combined"]

        f.write(
            f"{r['mode']}\t"
            f"{r['family']}\t"
            f"{r['seed']}\t"
            f"{'PASS' if r['execution_pass'] else 'FAIL'}\t"
            f"{'PASS' if r['integration_pass'] else 'FAIL'}\t"
            f"{c['value'] if c else ''}\t"
            f"{c['error'] if c else ''}\t"
            f"{r['combined_relerr_pct'] or ''}\t"
            f"{r['max_pair_pull'] or ''}\t"
            f"{r['reference_pull'] or ''}\t"
            f"{','.join(r['failures'])}\n"
        )


summary_path = (
    root / "G_SERIES_QUALIFICATION_SUMMARY.txt"
)

with summary_path.open("w") as f:

    f.write(
        "Phase 11 Candidate-A G-series qualification\n\n"
    )

    f.write(
        "          S0      S1      S2      FAMILY\n"
    )

    f.write(
        "------------------------------------------\n"
    )

    for family in ("G1", "G2"):

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

        fam = (
            "PASS"
            if family_results[family]
            else "FAIL"
        )

        f.write(
            f"{family:<8}"
            f"{states[0]:<8}"
            f"{states[1]:<8}"
            f"{states[2]:<8}"
            f"{fam}\n"
        )

    f.write("\nDetailed results:\n\n")

    for r in results:

        c = r["combined"]

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


print(summary_path.read_text())

print(f"WROTE={json_path}")
print(f"WROTE={tsv_path}")
print(f"WROTE={summary_path}")
