#!/usr/bin/env python3

from pathlib import Path
import csv
import os
import re
import sys


if len(sys.argv) != 4:
    raise SystemExit(
        "usage: make_resonance_workers.py "
        "<template> <sources_root> <output_dir>"
    )


template = Path(sys.argv[1]).resolve()
sources = Path(sys.argv[2]).resolve()
outdir = Path(sys.argv[3]).resolve()

if not template.is_file():
    raise SystemExit(
        f"ERROR: template not found: {template}"
    )

if not sources.is_dir():
    raise SystemExit(
        f"ERROR: sources root not found: {sources}"
    )

outdir.mkdir(parents=True, exist_ok=True)

base = template.read_text()


# ----------------------------------------------------------------------
# Frozen qualified-template properties
# ----------------------------------------------------------------------

BASE_MODE = "G2_S0"

BASE_SCHEDULE = '5:50000:"gw",3:200000:""'

BASE_DIAGNOSTIC = "phase11_candidate_A_stress_v1"

BASE_WORKER_PREFIX = "candidate_A_stress_v1/"

BASE_BANNER = "PHASE11_CANDIDATE_A_STRESS_V1_"

EXPECTED_SEED = "1740114216"


jobs = [
    {
        "mode": "W_G2",
        "variant": "W_restricted",
        "iterations": '5:50000:"gw",3:200000:""',
    },
    {
        "mode": "WT_G2",
        "variant": "WT_fccstyle",
        "iterations": '5:50000:"gw",3:200000:""',
    },
    {
        "mode": "U_2M",
        "variant": "U_unrestricted",
        "iterations": '5:50000:"gw",1:2000000:""',
    },
    {
        "mode": "W_2M",
        "variant": "W_restricted",
        "iterations": '5:50000:"gw",1:2000000:""',
    },
    {
        "mode": "WT_2M",
        "variant": "WT_fccstyle",
        "iterations": '5:50000:"gw",1:2000000:""',
    },
    {
        "mode": "WT_W23",
        "variant": "WT_fccstyle",
        "iterations": '10:100000:"gw",10:200000:""',
    },
]


# ----------------------------------------------------------------------
# Audit source-card machinery in the template
# ----------------------------------------------------------------------

source_card_assignments = list(
    re.finditer(
        r'(?m)^SOURCE_CARD=.*$',
        base,
    )
)

if len(source_card_assignments) != 2:
    raise RuntimeError(
        "Expected exactly two SOURCE_CARD assignments "
        "(initial assignment + readlink canonicalization); "
        f"found {len(source_card_assignments)}"
    )

first_source_assignment = source_card_assignments[0].group(0)
second_source_assignment = source_card_assignments[1].group(0)

expected_second = 'SOURCE_CARD="$(readlink -f "$SOURCE_CARD")"'

if second_source_assignment != expected_second:
    raise RuntimeError(
        "Unexpected SOURCE_CARD canonicalization line:\n"
        f"  {second_source_assignment}"
    )


source_dir_assignments = list(
    re.finditer(
        r'(?m)^SOURCE_DIR=.*$',
        base,
    )
)

if len(source_dir_assignments) != 1:
    raise RuntimeError(
        "Expected exactly one SOURCE_DIR assignment; "
        f"found {len(source_dir_assignments)}"
    )

expected_source_dir = 'SOURCE_DIR="$(dirname "$SOURCE_CARD")"'

if source_dir_assignments[0].group(0) != expected_source_dir:
    raise RuntimeError(
        "Unexpected SOURCE_DIR derivation:\n"
        f"  {source_dir_assignments[0].group(0)}"
    )


if base.count(BASE_SCHEDULE) < 2:
    raise RuntimeError(
        "Expected integration schedule not found often enough"
    )

if base.count(EXPECTED_SEED) < 2:
    raise RuntimeError(
        "Expected integration seed not found often enough"
    )

if base.count(BASE_MODE) < 2:
    raise RuntimeError(
        "Template does not look like G2_S0 worker"
    )


print("===== TEMPLATE AUDIT =====")
print(f"template={template}")
print(f"initial_source_card={first_source_assignment}")
print(f"canonicalizer={second_source_assignment}")
print(f"source_dir_derivation={expected_source_dir}")
print(f"seed={EXPECTED_SEED}")
print(f"base_schedule={BASE_SCHEDULE}")
print("TEMPLATE_AUDIT=PASS")


manifest = []


for job in jobs:

    mode = job["mode"]
    variant = job["variant"]
    schedule = job["iterations"]

    source_dir = (
        sources / variant
    ).resolve()

    source_card = (
        source_dir / "process.sin"
    ).resolve()

    source_common = (
        source_dir / "common"
    ).resolve()

    source_context = (
        source_dir / "render_context.json"
    ).resolve()


    # --------------------------------------------------------------
    # Validate complete variant source tree
    # --------------------------------------------------------------

    if not source_card.is_file():
        raise RuntimeError(
            f"{mode}: missing process card: {source_card}"
        )

    if not source_common.is_dir():
        raise RuntimeError(
            f"{mode}: missing common directory: {source_common}"
        )

    if not source_context.is_file():
        raise RuntimeError(
            f"{mode}: missing render_context.json: {source_context}"
        )


    text = base


    # --------------------------------------------------------------
    # Mode/provenance identity
    # --------------------------------------------------------------

    text = text.replace(
        BASE_MODE,
        mode,
    )

    text = text.replace(
        BASE_DIAGNOSTIC,
        "phase11_excess_resonance_matrix_v1",
    )

    text = text.replace(
        BASE_WORKER_PREFIX,
        "excess_resonance_matrix_v1/",
    )

    text = text.replace(
        BASE_BANNER,
        "PHASE11_EXCESS_RESONANCE_MATRIX_V1_",
    )


    # --------------------------------------------------------------
    # Source tree
    #
    # IMPORTANT:
    #
    # Replace ONLY the initial SOURCE_CARD assignment.
    #
    # Preserve:
    #
    #   SOURCE_CARD="$(readlink -f "$SOURCE_CARD")"
    #   SOURCE_DIR="$(dirname "$SOURCE_CARD")"
    #   SOURCE_COMMON="$SOURCE_DIR/common"
    #   SOURCE_CONTEXT="$SOURCE_DIR/render_context.json"
    #
    # This keeps the qualified source-tree contract intact.
    # --------------------------------------------------------------

    new_source_assignment = (
        f'SOURCE_CARD="{source_card}"'
    )

    text = text.replace(
        first_source_assignment,
        new_source_assignment,
        1,
    )


    # --------------------------------------------------------------
    # Integration schedule
    # --------------------------------------------------------------

    text = text.replace(
        BASE_SCHEDULE,
        schedule,
    )


    # --------------------------------------------------------------
    # Hard checks on generated worker
    # --------------------------------------------------------------

    required_literal_lines = [
        new_source_assignment,
        expected_second,
        expected_source_dir,
        'SOURCE_COMMON="$SOURCE_DIR/common"',
        'SOURCE_CONTEXT="$SOURCE_DIR/render_context.json"',
    ]

    for required in required_literal_lines:
        if required not in text:
            raise RuntimeError(
                f"{mode}: missing required worker line:\n"
                f"  {required}"
            )


    required_numerical_tokens = [
        '$integration_method = "vamp2"',
        '$rng_method = "rng_stream"',
        '$vamp_parallel_method = "simple"',
    ]

    for token in required_numerical_tokens:
        if token not in text:
            raise RuntimeError(
                f"{mode}: missing numerical token: {token}"
            )


    if EXPECTED_SEED not in text:
        raise RuntimeError(
            f"{mode}: integration seed disappeared"
        )

    if schedule not in text:
        raise RuntimeError(
            f"{mode}: integration schedule missing"
        )

    if mode not in text:
        raise RuntimeError(
            f"{mode}: mode replacement missing"
        )


    # The old generated process path must NOT remain as the active
    # initial SOURCE_CARD assignment.
    generated_source_assignment = first_source_assignment

    if generated_source_assignment in text:
        raise RuntimeError(
            f"{mode}: original SOURCE_CARD assignment still present"
        )


    # --------------------------------------------------------------
    # Write worker
    # --------------------------------------------------------------

    worker = (
        outdir / f"run_{mode}.sh"
    )

    worker.write_text(text)
    os.chmod(worker, 0o755)


    manifest.append(
        {
            "mode": mode,
            "variant": variant,
            "source_dir": str(source_dir),
            "source_card": str(source_card),
            "iterations": schedule,
            "integration_seed": EXPECTED_SEED,
            "worker": str(worker),
        }
    )


manifest_path = (
    outdir / "RESONANCE_MATRIX_MANIFEST.tsv"
)


with manifest_path.open(
    "w",
    newline="",
) as f:

    writer = csv.DictWriter(
        f,
        delimiter="\t",
        lineterminator="\n",
        fieldnames=[
            "mode",
            "variant",
            "source_dir",
            "source_card",
            "iterations",
            "integration_seed",
            "worker",
        ],
    )

    writer.writeheader()
    writer.writerows(manifest)


print()
print(f"CREATED_WORKERS={len(manifest)}")
print(f"MANIFEST={manifest_path}")

for row in manifest:
    print(
        f"{row['mode']} "
        f"variant={row['variant']} "
        f"seed={row['integration_seed']} "
        f"iterations={row['iterations']} "
        f"source_card={row['source_card']}"
    )

print("RESONANCE_WORKER_BUILD=PASS")
