#!/usr/bin/env bash
set -euo pipefail

# =====================================================================
# Phase 12 formal production freeze
#
# Physics recipe:
#   WT_A07F3_S0_exactchain_v1p0p1
#
# This script:
#   - verifies the already-qualified recipe
#   - verifies final production gates
#   - verifies the QED-systematics closeout
#   - hashes/counts every hard LHE shard
#   - hashes/counts every final HepMC shard
#   - verifies the merged 1M parent LHE
#   - independently repeats the nominal-G0_H0 physics-record test
#   - freezes small reference products
#   - creates a reproduction capsule on EOS
#
# It does NOT modify physics-event files.
# =====================================================================


# ---------------------------------------------------------------------
# Canonical locations
# ---------------------------------------------------------------------

REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

BASE="$REPO/phase12_production_v1"

PROD=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/full6f_365gev_ee_ttbar_spinpol_v1

P12="$PROD/phase12_production_v1/20260821T162202Z_WT_A07F3_S0_1M_40x25k_v1p0p1"

SAMPLE_ID=full6f365_ee_LR100_epmum_WT_A07F3_S0

RECIPE_ID=WT_A07F3_S0_exactchain_v1p0p1

RECIPE="$BASE/recipe_freeze/$RECIPE_ID"

P12_SUB="$BASE/submissions/20260821T162202Z_WT_A07F3_S0_1M_40x25k_v1p0p1"

P12B_SUB="$BASE/phase12b_exactchain_v1/submissions/20260821T175012Z_P12B_1M_40x25k_P6_exact_v1"

P12B_OUT="$P12/shower/phase12b_exactchain_v1/20260821T175012Z_P12B_1M_40x25k_P6_exact_v1"

P12B_MANIFEST="$P12B_SUB/phase12b_worker_manifest.tsv"

CANONICAL_SHOWER_WORKER="$BASE/phase12b_exactchain_v1/worker_revisions/frozen_exact_worker_v1p0p1_string_join"

PARENT_LHE="$P12/closeout_v1/${SAMPLE_ID}__P12_1M.lhe"

QED_TAG=20260824T154629Z_P12_QED4x25k_samehard_seed812100001_v1

QED_SUB="$BASE/qed_systematics_v1/submissions/$QED_TAG"

QED_OUT="$P12/shower/qed_systematics_v1/$QED_TAG"

QED_ANALYSIS="$QED_OUT/analysis_v1"

SPIN_DIR="$QED_ANALYSIS/spin_lepton_25k_v3"

PARTICLE_DIR="$QED_ANALYSIS/particle_content"

NOMINAL_HEPMC="$P12B_OUT/hepmc3/$SAMPLE_ID/${SAMPLE_ID}__P12_1M_0001.hepmc3"

G0H0_HEPMC="$QED_OUT/G0_H0/hepmc3/$SAMPLE_ID/${SAMPLE_ID}__P12_1M_0001_G0_H0.hepmc3"

FREEZE_ROOT="$BASE/production_closeout_v1"

FREEZE="$FREEZE_ROOT/$RECIPE_ID"

EOS_FREEZE="$P12/production_closeout_v1"

EXPECTED_PARENT_LHE_SHA256=a8504e3b8b56cdacd0adccd251c57aade5259a844e5ae1031f5a956371abb133

EXPECTED_NOMINAL_PHYSICS_SHA256=68d7ef9666043644e319f9323d857d52fe9fbc6898570857c52f57eefed88bb2


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

die() {
    echo "ERROR: $*" >&2
    exit 1
}

require_file() {
    [[ -f "$1" ]] || die "missing file: $1"
}

require_dir() {
    [[ -d "$1" ]] || die "missing directory: $1"
}

pass() {
    echo "$1=PASS"
}


# ---------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------

echo
echo "================================================================"
echo "PHASE 12 FINAL FREEZE — PREFLIGHT"
echo "================================================================"

require_dir "$REPO"
require_dir "$P12"
require_dir "$RECIPE"
require_dir "$P12_SUB"
require_dir "$P12B_SUB"
require_dir "$P12B_OUT"
require_dir "$CANONICAL_SHOWER_WORKER"
require_dir "$QED_SUB"
require_dir "$QED_OUT"
require_dir "$SPIN_DIR"
require_dir "$PARTICLE_DIR"

require_file "$P12B_MANIFEST"
require_file "$PARENT_LHE"
require_file "$NOMINAL_HEPMC"
require_file "$G0H0_HEPMC"

require_file \
  "$SPIN_DIR/spin15_factorial_contrasts.csv"

require_file \
  "$SPIN_DIR/spin15_paired_differences.csv"

require_file \
  "$SPIN_DIR/spin15_coefficients.csv"

require_file \
  "$SPIN_DIR/spin_lepton_systematics_report.json"

require_file \
  "$PARTICLE_DIR/qed_particle_content_report.json"

require_file \
  "$QED_SUB/validation/qed_systematics_validation.txt"

require_file \
  "$QED_SUB/analysis/qed_spin_lepton_25k_v3.log"

require_file \
  "$QED_SUB/analysis/qed_particle_content_analysis.log"

pass "SOURCE_TREE_PREFLIGHT"


# ---------------------------------------------------------------------
# Do not freeze while related Condor jobs are still active.
# ---------------------------------------------------------------------

ACTIVE_JOBS=$(
    condor_q "${USER:-cglenn}" \
      -af ClusterId ProcId Cmd Args \
      2>/dev/null \
    | grep -E \
      'P12_1M|P12B_1M|P12_QED4x25k|WT_A07F3_S0_1M' \
    || true
)

if [[ -n "$ACTIVE_JOBS" ]]; then

    echo
    echo "Related jobs are still present in Condor:"
    echo "$ACTIVE_JOBS"

    die "refusing to freeze an actively referenced production"

fi

pass "NO_ACTIVE_PHASE12_CONDOR_JOBS"


# ---------------------------------------------------------------------
# Do not overwrite an existing formal freeze.
# ---------------------------------------------------------------------

if [[ -e "$FREEZE" ]]; then
    die "formal freeze already exists: $FREEZE"
fi

if [[ -e "$EOS_FREEZE" ]]; then
    die "EOS formal freeze already exists: $EOS_FREEZE"
fi


BUILD="${FREEZE}.build.$$"

rm -rf "$BUILD"

mkdir -p \
  "$BUILD/manifests" \
  "$BUILD/validation" \
  "$BUILD/reference/qed_particle_content" \
  "$BUILD/reference/qed_spin15" \
  "$BUILD/reference/scripts" \
  "$BUILD/reference/cards" \
  "$BUILD/provenance" \
  "$BUILD/tools"


# ---------------------------------------------------------------------
# Record current closeout host/repository state.
#
# IMPORTANT:
# this Git HEAD is the CLOSEOUT-time repository state, not a replacement
# for the already-frozen production snapshots.
# ---------------------------------------------------------------------

{
    echo "FREEZE_TIME_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "HOST=$(hostname -f)"
    echo "USER=${USER:-unknown}"
    echo "REPO=$REPO"

    if git -C "$REPO" rev-parse --is-inside-work-tree \
        >/dev/null 2>&1
    then
        echo "GIT_HEAD=$(git -C "$REPO" rev-parse HEAD)"
        echo "GIT_BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
    else
        echo "GIT_HEAD=NOT_A_GIT_REPOSITORY"
        echo "GIT_BRANCH=NOT_A_GIT_REPOSITORY"
    fi
} \
> "$BUILD/provenance/CLOSEOUT_ENVIRONMENT.txt"

git -C "$REPO" status --short \
  > "$BUILD/provenance/GIT_STATUS_AT_CLOSEOUT.txt" \
  2>/dev/null \
  || true


# ---------------------------------------------------------------------
# Source pointer registry
# ---------------------------------------------------------------------

cat > "$BUILD/SOURCE_POINTERS.tsv" <<EOF
role	path
repository	$REPO
phase12_output_root	$P12
qualified_recipe	$RECIPE
phase12_hard_submission	$P12_SUB
phase12b_submission	$P12B_SUB
phase12b_output	$P12B_OUT
phase12b_worker_manifest	$P12B_MANIFEST
canonical_future_shower_worker	$CANONICAL_SHOWER_WORKER
merged_parent_lhe	$PARENT_LHE
nominal_hepmc_shard1	$NOMINAL_HEPMC
qed_systematics_submission	$QED_SUB
qed_systematics_output	$QED_OUT
qed_spin_analysis	$SPIN_DIR
qed_particle_analysis	$PARTICLE_DIR
EOF


# ---------------------------------------------------------------------
# Verify the already-frozen recipe checksum set.
# ---------------------------------------------------------------------

require_file \
  "$RECIPE/RECIPE_SHA256SUMS.txt"

(
    cd "$RECIPE"

    sha256sum -c \
      RECIPE_SHA256SUMS.txt
) \
> "$BUILD/validation/RECIPE_SHA256_VERIFY.txt"

pass "EXISTING_RECIPE_SHA256"


# ---------------------------------------------------------------------
# Verify the Phase12B pre-submission frozen inputs.
# ---------------------------------------------------------------------

require_file \
  "$P12B_SUB/records/PHASE12B_PRE_SUBMISSION_FREEZE.sha256"

sha256sum -c \
  "$P12B_SUB/records/PHASE12B_PRE_SUBMISSION_FREEZE.sha256" \
> "$BUILD/validation/PHASE12B_PRE_SUBMISSION_FREEZE_VERIFY.txt"

pass "PHASE12B_PRE_SUBMISSION_FREEZE"


# ---------------------------------------------------------------------
# Find and verify the formal Phase-12 final gate record.
# ---------------------------------------------------------------------

FINAL_GATE=$(
    grep -RIl \
      --include='*.txt' \
      'PHASE12_PRODUCTION=PASS' \
      "$P12_SUB" \
      "$P12B_SUB" \
      2>/dev/null \
    | head -1 \
    || true
)

[[ -n "$FINAL_GATE" ]] \
  || die "could not locate PHASE12_PRODUCTION=PASS record"

for token in \
    PHASE12_PRODUCTION=PASS \
    PHASE12A_CLOSEOUT=PASS \
    PHASE12B_EFFECTIVE_CONDOR_GATE=PASS \
    PHASE12B_METADATA_PREFLIGHT_GATE=PASS \
    PHASE12B_1M_METADATA_HEPMC_GATE=PASS \
    PHASE12B_1M_HISTORY_PRESENCE_GATE=PASS

do
    grep -qx "$token" "$FINAL_GATE" \
      || die "missing final gate token: $token"
done

cp -p \
  "$FINAL_GATE" \
  "$BUILD/validation/PHASE12_FINAL_GATE_STATUS.txt"

printf '%s\n' "$FINAL_GATE" \
  > "$BUILD/provenance/PHASE12_FINAL_GATE_SOURCE.txt"

pass "PHASE12_FINAL_GATE"


# ---------------------------------------------------------------------
# Locate/copy aggregate production validation if available.
# ---------------------------------------------------------------------

AGGREGATE_GATE=$(
    grep -RIl \
      --include='*.txt' \
      'PHASE12B_1M_METADATA_HEPMC_GATE=PASS' \
      "$P12B_SUB" \
      2>/dev/null \
    | grep -v 'PHASE12_FINAL_GATE_STATUS.txt' \
    | head -1 \
    || true
)

if [[ -n "$AGGREGATE_GATE" ]]; then

    cp -p \
      "$AGGREGATE_GATE" \
      "$BUILD/validation/PHASE12B_1M_AGGREGATE_VALIDATION.txt"

    printf '%s\n' "$AGGREGATE_GATE" \
      > "$BUILD/provenance/PHASE12B_AGGREGATE_SOURCE.txt"

fi


# ---------------------------------------------------------------------
# Verify QED technical + physics qualification.
# ---------------------------------------------------------------------

grep -q \
  'QED_SYSTEMATICS_VALIDATION=PASS' \
  "$QED_SUB/validation/qed_systematics_validation.txt" \
  || die "QED technical validation is not PASS"

grep -q \
  'QED_PARTICLE_CONTENT_ANALYSIS=PASS' \
  "$QED_SUB/analysis/qed_particle_content_analysis.log" \
  || die "QED particle-content validation is not PASS"

grep -q \
  'QED_SPIN_LEPTON_ANALYSIS_V3=PASS' \
  "$QED_SUB/analysis/qed_spin_lepton_25k_v3.log" \
  || die "QED spin/lepton validation is not PASS"

grep -q \
  'PROMPT_SELECTOR=PASS' \
  "$QED_SUB/analysis/qed_spin_lepton_25k_v3.log" \
  || die "prompt selector is not PASS"

grep -q \
  'HARD_SPIN_COMMON_LHE=PASS' \
  "$QED_SUB/analysis/qed_spin_lepton_25k_v3.log" \
  || die "hard-spin common-LHE check is not PASS"

grep -q \
  'PAIRING=PASS' \
  "$QED_SUB/analysis/qed_spin_lepton_25k_v3.log" \
  || die "QED event pairing is not PASS"

cp -p \
  "$QED_SUB/validation/qed_systematics_validation.txt" \
  "$BUILD/validation/QED_SYSTEMATICS_VALIDATION.txt"

pass "QED_FINAL_QUALIFICATION"


# ---------------------------------------------------------------------
# Check recipe/worker for symlinks.
#
# A future reproduction capsule should not silently depend on unknown
# external symlink targets.
# ---------------------------------------------------------------------

find "$RECIPE" \
  -type l \
  -printf '%p -> %l\n' \
  > "$BUILD/provenance/RECIPE_SYMLINKS.txt"

find "$CANONICAL_SHOWER_WORKER" \
  -type l \
  -printf '%p -> %l\n' \
  > "$BUILD/provenance/CANONICAL_WORKER_SYMLINKS.txt"

RECIPE_SYMLINKS=$(
    wc -l \
      < "$BUILD/provenance/RECIPE_SYMLINKS.txt"
)

WORKER_SYMLINKS=$(
    wc -l \
      < "$BUILD/provenance/CANONICAL_WORKER_SYMLINKS.txt"
)

echo "RECIPE_SYMLINK_COUNT=$RECIPE_SYMLINKS"
echo "CANONICAL_WORKER_SYMLINK_COUNT=$WORKER_SYMLINKS"

if [[ "$RECIPE_SYMLINKS" -ne 0 ]] \
   || [[ "$WORKER_SYMLINKS" -ne 0 ]]
then
    die \
      "recipe/worker contains symlinks; resolve portability before formal freeze"
fi

pass "REPRODUCTION_CAPSULE_SYMLINK_GATE"


# ---------------------------------------------------------------------
# Full raw-LHE + final-HepMC integrity manifest.
#
# This reads the production data but does not rerun any generation.
# ---------------------------------------------------------------------

python3 - \
  "$P12B_MANIFEST" \
  "$PARENT_LHE" \
  "$P12B_OUT/hepmc3/$SAMPLE_ID" \
  "$BUILD/manifests" \
  "$EXPECTED_PARENT_LHE_SHA256" \
<<'PY'
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path


manifest_path = Path(sys.argv[1])
parent_lhe = Path(sys.argv[2])
hepmc_dir = Path(sys.argv[3])
outdir = Path(sys.argv[4])
expected_parent_sha = sys.argv[5]

outdir.mkdir(
    parents=True,
    exist_ok=True,
)


def digest_and_count(path: Path, mode: str):
    digest = hashlib.sha256()
    count = 0
    size = 0

    with path.open("rb") as stream:
        for line in stream:
            digest.update(line)
            size += len(line)

            if mode == "lhe":
                if line.lstrip().startswith(b"<event>"):
                    count += 1

            elif mode == "hepmc":
                if line.startswith(b"E "):
                    count += 1

            else:
                raise ValueError(mode)

    return (
        digest.hexdigest(),
        size,
        count,
    )


# ================================================================
# Worker manifest contract
#
# Authoritative normalized Phase12B schema:
#
#   proc
#   shard_id
#   input_lhe
#   input_sha256
#   start
#   stop
#   pythia_seed
#
# Hard-generation seed is not a separate manifest column. It is
# encoded in the immutable input-LHE filename and is independently
# validated below.
# ================================================================

import re

with manifest_path.open(
    newline="",
) as stream:

    reader = csv.DictReader(
        stream,
        delimiter="\t",
    )

    fieldnames = (
        reader.fieldnames
        or []
    )

    rows = [
        row
        for row in reader
        if row
    ]


required_columns = [
    "proc",
    "shard_id",
    "input_lhe",
    "input_sha256",
    "start",
    "stop",
    "pythia_seed",
]

missing_columns = [
    column
    for column in required_columns
    if column not in fieldnames
]

if missing_columns:
    raise SystemExit(
        "worker manifest missing required columns: "
        f"{missing_columns}; "
        f"actual columns={fieldnames}"
    )


if len(rows) != 40:
    raise SystemExit(
        f"worker manifest rows != 40: {len(rows)}"
    )


hard_seed_pattern = re.compile(
    r"_seed(?P<seed>[0-9]+)\.lhe$"
)


hard_manifest_rows = []


for i, row in enumerate(rows):

    proc = int(
        row["proc"]
    )

    shard = (
        row["shard_id"]
    )

    input_path = Path(
        row["input_lhe"]
    )

    expected_sha = (
        row["input_sha256"]
    )

    start = int(
        row["start"]
    )

    stop = int(
        row["stop"]
    )

    pythia_seed = int(
        row["pythia_seed"]
    )

    nevents = (
        stop - start
    )


    # ------------------------------------------------------------
    # Deterministic row/shard/range contract
    # ------------------------------------------------------------

    expected_shard = (
        f"P12_1M_{i + 1:04d}"
    )

    expected_start = (
        i * 25000
    )

    expected_stop = (
        (i + 1) * 25000
    )

    expected_pythia_seed = (
        812100001 + i
    )

    expected_hard_seed = (
        412100001 + i
    )


    if proc != i:
        raise SystemExit(
            f"proc mismatch row={i}: "
            f"{proc} != {i}"
        )


    if shard != expected_shard:
        raise SystemExit(
            f"shard mismatch row={i}: "
            f"{shard} != {expected_shard}"
        )


    if start != expected_start:
        raise SystemExit(
            f"source start mismatch for {shard}: "
            f"{start} != {expected_start}"
        )


    if stop != expected_stop:
        raise SystemExit(
            f"source stop mismatch for {shard}: "
            f"{stop} != {expected_stop}"
        )


    if nevents != 25000:
        raise SystemExit(
            f"event-range size mismatch for {shard}: "
            f"{nevents} != 25000"
        )


    if pythia_seed != expected_pythia_seed:
        raise SystemExit(
            f"PYTHIA seed mismatch for {shard}: "
            f"{pythia_seed} != "
            f"{expected_pythia_seed}"
        )


    # ------------------------------------------------------------
    # Hard seed from immutable source-LHE filename
    # ------------------------------------------------------------

    match = hard_seed_pattern.search(
        input_path.name
    )

    if match is None:
        raise SystemExit(
            f"cannot recover hard-generation seed "
            f"from LHE filename: {input_path.name}"
        )


    hard_seed = int(
        match.group(
            "seed"
        )
    )


    if hard_seed != expected_hard_seed:
        raise SystemExit(
            f"hard-generation seed mismatch for {shard}: "
            f"{hard_seed} != "
            f"{expected_hard_seed}"
        )


    # ------------------------------------------------------------
    # Input file + SHA256 + event-count validation
    # ------------------------------------------------------------

    if not input_path.is_file():
        raise SystemExit(
            f"missing hard LHE shard: "
            f"{input_path}"
        )


    actual_sha, size, actual_events = (
        digest_and_count(
            input_path,
            "lhe",
        )
    )


    if actual_sha != expected_sha:
        raise SystemExit(
            f"hard LHE checksum mismatch: {shard}\n"
            f"expected={expected_sha}\n"
            f"actual={actual_sha}"
        )


    if actual_events != nevents:
        raise SystemExit(
            f"hard LHE event-count mismatch: "
            f"{shard}: "
            f"{actual_events} != {nevents}"
        )


    hard_manifest_rows.append(
        {
            "proc": proc,
            "shard": shard,
            "source_start": start,
            "source_stop": stop,
            "events": actual_events,
            "hard_seed": hard_seed,
            "pythia_seed": pythia_seed,
            "bytes": size,
            "sha256": actual_sha,
            "path": str(
                input_path
            ),
        }
    )


# ------------------------------------------------------------
# Campaign-wide deterministic seed/range validation
# ------------------------------------------------------------

if [
    row["hard_seed"]
    for row in hard_manifest_rows
] != list(
    range(
        412100001,
        412100041,
    )
):
    raise SystemExit(
        "hard-generation seed namespace is not "
        "exactly 412100001..412100040"
    )


if [
    row["pythia_seed"]
    for row in hard_manifest_rows
] != list(
    range(
        812100001,
        812100041,
    )
):
    raise SystemExit(
        "PYTHIA seed namespace is not "
        "exactly 812100001..812100040"
    )


if sum(
    row["events"]
    for row in hard_manifest_rows
) != 1_000_000:
    raise SystemExit(
        "hard-shard event total is not 1,000,000"
    )


hard_tsv = (
    outdir
    / "HARD_LHE_SHARDS_SHA256.tsv"
)


with hard_tsv.open(
    "w",
    newline="",
) as stream:

    writer = csv.DictWriter(
        stream,
        delimiter="\t",
        fieldnames=list(
            hard_manifest_rows[0].keys()
        ),
    )

    writer.writeheader()

    writer.writerows(
        hard_manifest_rows
    )


(
    outdir
    / "WORKER_MANIFEST_SCHEMA.txt"
).write_text(
    "\n".join(
        [
            "schema=phase12b_worker_manifest_v1",
            "columns="
            + ",".join(
                required_columns
            ),
            "rows=40",
            "events_per_shard=25000",
            "hard_seed_source=input_lhe_filename",
            "hard_seed_first=412100001",
            "hard_seed_last=412100040",
            "pythia_seed_first=812100001",
            "pythia_seed_last=812100040",
            "WORKER_MANIFEST_SCHEMA_GATE=PASS",
            "",
        ]
    )
)


# ================================================================
# Merged parent LHE
# ================================================================

parent_sha, parent_size, parent_events = (
    digest_and_count(
        parent_lhe,
        "lhe",
    )
)

if parent_sha != expected_parent_sha:
    raise SystemExit(
        "merged parent LHE checksum mismatch\n"
        f"expected={expected_parent_sha}\n"
        f"actual={parent_sha}"
    )

if parent_events != 1_000_000:
    raise SystemExit(
        f"merged parent LHE event count = {parent_events}"
    )

(
    outdir
    / "PARENT_LHE_SHA256.txt"
).write_text(
    f"{parent_sha}  {parent_lhe}\n"
)

(
    outdir
    / "PARENT_LHE_SUMMARY.txt"
).write_text(
    "\n".join(
        [
            f"path={parent_lhe}",
            f"bytes={parent_size}",
            f"events={parent_events}",
            f"sha256={parent_sha}",
            "",
        ]
    )
)


# ================================================================
# Final HepMC shards
# ================================================================

hepmc_paths = sorted(
    hepmc_dir.glob(
        "*.hepmc3"
    )
)

if len(hepmc_paths) != 40:
    raise SystemExit(
        f"final HepMC file count != 40: {len(hepmc_paths)}"
    )


hepmc_rows = []
total_hepmc_events = 0

for path in hepmc_paths:

    sha, size, events = (
        digest_and_count(
            path,
            "hepmc",
        )
    )

    if events != 25000:
        raise SystemExit(
            f"HepMC event count mismatch: "
            f"{path.name} -> {events}"
        )

    total_hepmc_events += events

    hepmc_rows.append(
        {
            "file": path.name,
            "events": events,
            "bytes": size,
            "sha256": sha,
            "path": str(path),
        }
    )


if total_hepmc_events != 1_000_000:
    raise SystemExit(
        f"total HepMC events = {total_hepmc_events}"
    )


hepmc_tsv = (
    outdir
    / "FINAL_HEPMC_SHARDS_SHA256.tsv"
)

with hepmc_tsv.open(
    "w",
    newline="",
) as stream:

    writer = csv.DictWriter(
        stream,
        delimiter="\t",
        fieldnames=list(
            hepmc_rows[0].keys()
        ),
    )

    writer.writeheader()
    writer.writerows(
        hepmc_rows
    )


summary = [
    "PHASE 12 DATA-INTEGRITY SUMMARY",
    "================================",
    "",
    "hard_shards=40",
    "hard_events=1000000",
    "hard_seed_first=412100001",
    "hard_seed_last=412100040",
    "pythia_seed_first=812100001",
    "pythia_seed_last=812100040",
    f"parent_lhe_events={parent_events}",
    f"parent_lhe_sha256={parent_sha}",
    "hepmc_shards=40",
    f"hepmc_events={total_hepmc_events}",
    "",
    "HARD_LHE_MANIFEST_GATE=PASS",
    "HARD_SEED_NAMESPACE_GATE=PASS",
    "PYTHIA_SEED_NAMESPACE_GATE=PASS",
    "PARENT_LHE_INTEGRITY_GATE=PASS",
    "FINAL_HEPMC_COUNT_GATE=PASS",
    "",
]

(
    outdir
    / "DATA_INTEGRITY_SUMMARY.txt"
).write_text(
    "\n".join(summary)
)

print(
    "\n".join(summary)
)
PY

pass "FULL_DATA_INTEGRITY_MANIFEST"


# ---------------------------------------------------------------------
# Independently reproduce the nominal-vs-G0H0 physics-record test.
#
# Exclude HepMC A attribute records. Campaign/shard identifier changes
# then cannot fake a physics difference.
# ---------------------------------------------------------------------

NOMINAL_PHYSICS_SHA=$(
    awk '$1 != "A"' \
      "$NOMINAL_HEPMC" \
    | sha256sum \
    | awk '{print $1}'
)

G0H0_PHYSICS_SHA=$(
    awk '$1 != "A"' \
      "$G0H0_HEPMC" \
    | sha256sum \
    | awk '{print $1}'
)

{
    echo "NOMINAL_HEPMC=$NOMINAL_HEPMC"
    echo "G0H0_HEPMC=$G0H0_HEPMC"
    echo
    echo "NOMINAL_PHYSICS_SHA256=$NOMINAL_PHYSICS_SHA"
    echo "G0H0_PHYSICS_SHA256=$G0H0_PHYSICS_SHA"
} \
> "$BUILD/validation/NOMINAL_REPRODUCTION_CHECK.txt"

[[ "$NOMINAL_PHYSICS_SHA" == "$G0H0_PHYSICS_SHA" ]] \
  || die "nominal physics record != controlled G0_H0 rerun"

[[ "$NOMINAL_PHYSICS_SHA" == "$EXPECTED_NOMINAL_PHYSICS_SHA256" ]] \
  || die "nominal physics hash does not match established reference"

cat >> \
  "$BUILD/validation/NOMINAL_REPRODUCTION_CHECK.txt" \
<<EOF

PHYSICS_RECORDS_BYTE_IDENTICAL=PASS
NOMINAL_REPRODUCTION=PASS
EOF

pass "NOMINAL_REPRODUCTION"


# ---------------------------------------------------------------------
# Freeze small, authoritative analysis products.
# ---------------------------------------------------------------------

cp -p \
  "$QED_SUB/analysis/analyze_qed_particle_content.py" \
  "$BUILD/reference/scripts/"

cp -p \
  "$QED_SUB/analysis/analyze_qed_spin_lepton_systematics_v3.py" \
  "$BUILD/reference/scripts/"

if [[ -f "$QED_SUB/analysis/audit_prompt_lepton_graph.py" ]]; then
    cp -p \
      "$QED_SUB/analysis/audit_prompt_lepton_graph.py" \
      "$BUILD/reference/scripts/"
fi

cp -p \
  "$QED_SUB/validate_qed_systematics.py" \
  "$BUILD/reference/scripts/"

cp -p \
  "$QED_SUB/qed_systematics_manifest.tsv" \
  "$BUILD/reference/"

for path in \
    "$PARTICLE_DIR"/qed_particle_content_summary.csv \
    "$PARTICLE_DIR"/qed_particle_content_paired_differences.csv \
    "$PARTICLE_DIR"/qed_particle_content_factorial_contrasts.csv \
    "$PARTICLE_DIR"/qed_particle_content_report.json

do
    require_file "$path"
    cp -p \
      "$path" \
      "$BUILD/reference/qed_particle_content/"
done

for path in \
    "$SPIN_DIR"/spin15_coefficients.csv \
    "$SPIN_DIR"/spin15_paired_differences.csv \
    "$SPIN_DIR"/spin15_factorial_contrasts.csv \
    "$SPIN_DIR"/scalar_observable_summary.csv \
    "$SPIN_DIR"/scalar_paired_differences.csv \
    "$SPIN_DIR"/scalar_factorial_contrasts.csv \
    "$SPIN_DIR"/prompt_selector_summary.csv \
    "$SPIN_DIR"/spin_lepton_systematics_report.json

do
    require_file "$path"
    cp -p \
      "$path" \
      "$BUILD/reference/qed_spin15/"
done

if [[ -f "$REPO/configs/pythia/level_a.cmnd" ]]; then
    cp -p \
      "$REPO/configs/pythia/level_a.cmnd" \
      "$BUILD/reference/cards/"
fi

cp -p \
  "$P12B_MANIFEST" \
  "$BUILD/reference/"

cp -p \
  "$P12B_SUB/run_phase12b_25k.sh" \
  "$BUILD/reference/scripts/"

cp -p \
  "$P12B_SUB/phase12b_40x25k.sub" \
  "$BUILD/reference/"


# ---------------------------------------------------------------------
# Numerical 2x2 QED/Spin-15 closeout summary.
# ---------------------------------------------------------------------

python3 - \
  "$SPIN_DIR/spin15_factorial_contrasts.csv" \
  "$BUILD/validation/QED_SPIN15_FACTORIAL_SUMMARY.txt" \
<<'PY'
import csv
import sys
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

rows = list(
    csv.DictReader(
        source.open()
    )
)

representations = [
    "bare",
    "dressed_all",
    "dressed_prompt",
]

contrasts = [
    "gamma_main_effect",
    "hadron_qed_main_effect",
    "gamma_x_hadron_interaction",
]

lines = [
    "QED 2x2 SPIN-15 FACTORIAL CLOSEOUT",
    "=================================",
    "",
]

for representation in representations:

    lines.append(
        f"representation={representation}"
    )

    for contrast in contrasts:

        subset = [
            row
            for row in rows
            if (
                row["representation"]
                == representation
                and row["contrast"]
                == contrast
            )
        ]

        if not subset:
            raise SystemExit(
                f"missing rows: "
                f"{representation} {contrast}"
            )

        worst = max(
            subset,
            key=lambda row: abs(
                float(row["z"])
            ),
        )

        lines.append(
            "  "
            f"{contrast}: "
            f"max_abs_z="
            f"{abs(float(worst['z'])):.6f} "
            f"coefficient={worst['coefficient']} "
            f"effect={float(worst['effect']):+.9g} "
            f"stderr={float(worst['standard_error']):.9g}"
        )

    lines.append("")

lines.extend(
    [
        "Decision:",
        "  G0_H0 remains the qualified nominal PYTHIA policy.",
        "  G1_H0 is retained as the gamma-conversion systematic.",
        "  G0_H1 is retained as the HadronLevel-QED systematic.",
        "  G1_H1 is retained as the combined-QED systematic.",
        "  No 1M regeneration is required from this study.",
        "",
        "QED_SPIN15_CLOSEOUT=PASS",
        "",
    ]
)

target.write_text(
    "\n".join(lines)
)

print(
    "\n".join(lines)
)
PY


# ---------------------------------------------------------------------
# Formal machine-readable production lock.
# ---------------------------------------------------------------------

export REPO
export BASE
export P12
export SAMPLE_ID
export RECIPE_ID
export RECIPE
export P12_SUB
export P12B_SUB
export P12B_OUT
export CANONICAL_SHOWER_WORKER
export PARENT_LHE
export QED_SUB
export QED_OUT
export EXPECTED_PARENT_LHE_SHA256

python3 - \
  "$BUILD/PRODUCTION_LOCK.json" \
<<'PY'
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


target = Path(sys.argv[1])


def env(name):
    return os.environ[name]


try:
    closeout_git_head = subprocess.check_output(
        [
            "git",
            "-C",
            env("REPO"),
            "rev-parse",
            "HEAD",
        ],
        text=True,
    ).strip()
except Exception:
    closeout_git_head = None


payload = {
    "schema_version": 1,
    "status": "FROZEN_AND_QUALIFIED",
    "freeze_time_utc": (
        datetime.now(
            timezone.utc
        ).isoformat()
    ),

    "recipe": {
        "recipe_id": env("RECIPE_ID"),
        "physics_recipe_path": env("RECIPE"),
        "canonical_future_shower_worker": (
            env("CANONICAL_SHOWER_WORKER")
        ),
        "implementation_note": (
            "The final 1M production is valid. "
            "For future productions, use the "
            "v1p0p1_string_join worker revision as "
            "the canonical shower implementation."
        ),
    },

    "process": {
        "collider": "e+e-",
        "sqrt_s_GeV": 365.0,
        "beam_configuration": "LR100",
        "signal_definition": (
            "WT-restricted resonant full six-fermion"
        ),
        "representative_process": (
            "e1,E1 => b,bbar,E1,n1,e2,N2"
        ),
        "decay_channel": "e+ nu_e mu- anti-nu_mu b bbar",
        "matrix_element_order": "LO",
    },

    "hard_generation": {
        "generator": "WHIZARD",
        "qualified_version": "3.1.8",
        "integration_backend": "VAMP2",
        "rng_mode": "rng_stream",
        "balancing": "VAMP simple balancing",
        "grid": "S0",
        "grid_policy": (
            "one predetermined frozen qualified grid"
        ),
        "mpi_ranks_per_job": 1,
        "omp_threads": 1,
        "events_per_shard": 25000,
        "production_shards": 40,
        "production_events": 1000000,
        "hard_seed_first": 412100001,
        "hard_seed_last": 412100040,
        "grid_independence_note": (
            "The integration grid is an importance-sampling "
            "map, not a source of event statistical independence. "
            "Independent generation seeds provide independent "
            "event draws after the frozen grid was qualified "
            "against independent integration replicas, "
            "over-integration, and single-vs-multi-grid controls."
        ),
    },

    "preparation": {
        "canonical_isr_normalization": True,
        "history_preserving_serializer": True,
        "strict_topology_validation": True,
        "synthetic_W_insertion": False,
        "synthetic_resonance_insertion": False,
        "particle_add_remove_policy": "none",
    },

    "shower": {
        "generator": "PYTHIA8",
        "qualified_version": "8.315",
        "hepmc3_version": "3.3.1",
        "pythia_seed_first": 812100001,
        "pythia_seed_last": 812100040,

        "settings": {
            "Beams:frameType": 4,
            "PartonLevel:ISR": False,
            "PartonLevel:FSR": True,
            "PartonLevel:MPI": False,
            "HadronLevel:Hadronize": True,
            "HadronLevel:Decay": True,
            "ProcessLevel:resonanceDecays": False,
            "6:mayDecay": False,
            "TimeShower:QEDshowerByL": True,
            "TimeShower:QEDshowerByQ": True,
            "SpaceShower:QEDshowerByL": False,
            "TimeShower:QEDshowerByGamma": False,
            "HadronLevel:QED": False,
        },

        "physics_interpretation": {
            "incoming_lepton_ISR": (
                "provided by WHIZARD and retained"
            ),
            "pythia_ISR": (
                "disabled to avoid ISR double counting"
            ),
            "prompt_final_state_QED_FSR": (
                "enabled for leptons and quarks"
            ),
            "top_decay_in_pythia": False,
        },
    },

    "production_result": {
        "sample_id": env("SAMPLE_ID"),
        "output_root": env("P12"),
        "parent_lhe": env("PARENT_LHE"),
        "parent_lhe_sha256": (
            env("EXPECTED_PARENT_LHE_SHA256")
        ),
        "requested_events": 1000000,
        "accepted_events": 1000000,
        "failed_events": 0,
        "bad_weight_events": 0,
        "unknown_pythia_errors": 0,
        "known_recoverable_error_occurrences": 109,
        "hadron_level_retries": 37,
        "me_weight_above_ps_occurrences": 48368,
        "historical_string_join_occurrences": 2,
        "history_presence_mismatches": 0,
    },

    "qed_systematics": {
        "status": "PASS",
        "nominal": "G0_H0",
        "G0_H0": {
            "QEDshowerByGamma": False,
            "HadronLevel_QED": False,
        },
        "G1_H0": {
            "QEDshowerByGamma": True,
            "HadronLevel_QED": False,
        },
        "G0_H1": {
            "QEDshowerByGamma": False,
            "HadronLevel_QED": True,
        },
        "G1_H1": {
            "QEDshowerByGamma": True,
            "HadronLevel_QED": True,
        },
        "decision": (
            "retain G0_H0 as nominal; retain other "
            "configurations as generator-systematic variations; "
            "no 1M regeneration required"
        ),
    },

    "paths": {
        "hard_submission": env("P12_SUB"),
        "shower_submission": env("P12B_SUB"),
        "shower_output": env("P12B_OUT"),
        "qed_submission": env("QED_SUB"),
        "qed_output": env("QED_OUT"),
    },

    "software_provenance_note": (
        "The current generic setup_lxplus.sh may resolve a "
        "different WHIZARD version. Production qualification "
        "belongs to WHIZARD 3.1.8 and the frozen production "
        "environment/snapshots, not to whatever 'latest' "
        "currently resolves to."
    ),

    "closeout_repository_head": (
        closeout_git_head
    ),
}

target.write_text(
    json.dumps(
        payload,
        indent=2,
        sort_keys=True,
    )
    + "\n"
)
PY


# ---------------------------------------------------------------------
# Human-readable recipe contract
# ---------------------------------------------------------------------

cat > "$BUILD/FUTURE_PRODUCTION_CONTRACT.md" <<'EOF'
# WT_A07F3_S0_exactchain_v1p0p1 production contract

## Status

This recipe is the qualified Phase-12 LO production recipe for

- e+ e- collisions at sqrt(s) = 365 GeV,
- LR100 beam configuration,
- WT-restricted full six-fermion
  e+ e- -> b bbar e+ nu_e mu- anti-nu_mu,
- WHIZARD hard generation followed by PYTHIA8 shower/hadronization.

The Phase-12 1M sample is frozen and must not be silently modified.

## Hard generation

Qualified hard-generation conditions:

- WHIZARD 3.1.8.
- LO matrix element.
- VAMP2.
- rng_stream.
- VAMP simple balancing.
- predetermined qualified S0 grid.
- one MPI rank per generation job.
- OMP_NUM_THREADS=1.
- 25,000 hard events per production shard.

The S0 grid is an importance-sampling representation of the same fixed
integrand. Event independence comes from independent generation RNG seeds,
not from regenerating an integration grid for each shard.

Do not reintegrate per production shard.

For additional statistics with unchanged physics, reuse the qualified grid
and use a new, disjoint hard-event seed namespace.

## Resonance/history contract

The sample is a WT-restricted full-six-fermion sample.

Serialized resonance presence is not required to be identical event by event.
The validated record can contain different explicit top/W history-presence
classes.

The preparation chain must:

1. perform canonical ISR normalization;
2. preserve existing resonance/history information;
3. perform strict topology validation;
4. never synthesize W bosons;
5. never add/remove hard-process particles simply to regularize history.

## PYTHIA contract

Canonical nominal policy:

- WHIZARD ISR retained.
- PYTHIA ISR OFF.
- PYTHIA FSR ON.
- MPI OFF.
- hadronization ON.
- unstable-particle decays ON.
- PYTHIA hard-process resonance decays OFF.
- top decay OFF (`6:mayDecay=off`).
- `TimeShower:QEDshowerByL=on`.
- `TimeShower:QEDshowerByQ=on`.
- `SpaceShower:QEDshowerByL=off`.
- `TimeShower:QEDshowerByGamma=off`.
- `HadronLevel:QED=off`.

Qualified PYTHIA version: 8.315.
Qualified HepMC3 version: 3.3.1.

For future production, use the frozen
`frozen_exact_worker_v1p0p1_string_join`
worker implementation.

The two historical string-joining occurrences in the original 1M campaign
were recoverable and did not invalidate the sample. The corrected worker is
the canonical future implementation.

## QED systematic decision

The controlled same-hard-event 2x2 study tested:

- G0_H0: gamma conversion OFF, hadron QED OFF — nominal;
- G1_H0: gamma conversion ON, hadron QED OFF;
- G0_H1: gamma conversion OFF, hadron QED ON;
- G1_H1: both ON.

The hard spin representation is identical by construction across all four
samples. No statistically compelling Spin-15 bias requiring a production
change was observed.

Therefore G0_H0 remains the nominal configuration.

The three other configurations are retained as generator-systematic
variations.

## Changes that DO NOT automatically require grid requalification

If the physics definition and software recipe are unchanged:

- increasing event count;
- changing number of output shards;
- changing production bookkeeping/tag;
- using new independent generation and PYTHIA seeds.

These still require normal production smoke tests and validation.

## Changes that DO require a new qualification

At minimum:

- center-of-mass energy;
- beam polarization/helicity definition;
- process/final-state definition;
- resonance restrictions;
- matrix-element oer, including LO -> NLO;
- NLO/PS matching prescription;
- integration prescription;
- materially different WHIZARD version;
- materially different PYTHIA version;
- ISR/FSR ownership;
- top-decay ownership;
- nominal QED shower policy;
- history-serialization algorithm;
- any change that alters event weights or the hard integrand.

Do not call such a campaign `WT_A07F3_S0_exactchain_v1p0p1`.
Create and qualify a new recipe identifier.

## Required future-production validation

Every production using this recipe should retain:

- exact recipe checksum;
- exact software/environment record;
- grid/workspace checksum;
- shard manifest;
- event ranges;
- hard RNG seeds;
- PYTHIA RNG seeds;
- input LHE checksums;
- output HepMC checksums;
- accepted/failed event counts;
- bad-weight count;
- known and unknown PYTHIA-error accounting;
- preparation/history validation;
- final production gate.

No shard should be selected because it has the "best" stochastic behavior.
Predetermined seed/grid choices must be preserved.
EOF


# ---------------------------------------------------------------------
# Human-readable closeout README
# ---------------------------------------------------------------------

cat > "$BUILD/README.md" <<EOF
# Phase 12 production closeout

## Final status

\`\`\`
PHASE12_PRODUCTION=PASS
RECIPE=$RECIPE_ID
NOMINAL_QED_POLICY=G0_H0
PRODUCTION_EVENTS=1000000
\`\`\`

This directory is the authoritative closeout record for the qualified
365 GeV LR100 WT-restricted full-six-fermion WHIZARD+PYTHIA production.

## Authoritative production

\`\`\`
$P12
\`\`\`

## Physics recipe

\`\`\`
$RECIPE
\`\`\`

## Canonical future PYTHIA worker

\`\`\`
$CANONICAL_SHOWER_WORKER
\`\`\`

The corrected v1p0p1 string-join worker supersedes the original worker
implementation for future production. This does not invalidate the existing
1M sample.

## Contents

- \`PRODUCTION_LOCK.json\` — machine-readable physics/software lock.
- \`FUTURE_PRODUCTION_CONTRACT.md\` — rules for reuse.
- \`SOURCE_POINTERS.tsv\` — authoritative source locations.
- \`manifests/\` — complete hard-LHE and final-HepMC SHA256 manifests.
- \`validation/\` — final production and QED validation evidence.
- \`reference/\` — small authoritative cards/scripts/numerical QED products.
- \`provenance/\` — closeout repository/environment state.
- \`tools/\` — integrity revalidation utility.

## Important version distinction

The production was qualified using WHIZARD 3.1.8.

A later interactive Key4HEP environment may resolve WHIZARD 3.1.5 or another
version. That later environment is not the production provenance.

Future exact-recipe production must use the qualified frozen environment/
software combination or undergo an explicit software-version requalification.

## Data immutability

The large EOS production files are not duplicated here.

Their exact content is frozen through SHA256 manifests.

The separate EOS reproduction capsule contains the closeout records plus the
frozen recipe and canonical corrected shower worker.
EOF


# ---------------------------------------------------------------------
# Full-data verifier to keep with the closeout.
# ---------------------------------------------------------------------

cat > "$BUILD/tools/verify_frozen_data.py" <<'PY'
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def digest(path: Path) -> str:

    h = hashlib.sha256()

    with path.open("rb") as stream:

        while True:

            block = stream.read(
         * 1024
            )

            if not block:
                break

            h.update(block)

    return h.hexdigest()


def verify_tsv(path: Path) -> int:

    with path.open() as stream:

        rows = list(
            csv.DictReader(
                stream,
                delimiter="\t",
            )
        )

    failures = 0

    for row in rows:

        source = Path(
            row["path"]
        )

        expected = (
            row["sha256"]
        )

        if not source.is_file():

            print(
                f"MISSING {source}"
            )

            failures += 1
            continue

        actual = digest(
            source
        )

        if actual != expected:

            print(
                f"FAIL {source}"
            )

            print(
                f"  expected={expected}"
            )

            print(
                f"  actual  ={actual}"
            )

            failures += 1

        else:

            print(
                f"PASS {source}"
            )

    return failures


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "closeout_dir",
        type=Path,
    )

    args = parser.parse_args()

    root = (
        args.closeout_dir.resolve()
    )

    failures = 0

    for name in [
        "HARD_LHE_SHARDS_SHA256.tsv",
        "FINAL_HEPMC_SHARDS_SHA256.tsv",
    ]:

        path = (
            root
            / "manifests"
            / name
        )

        if not path.is_file():
            raise SystemExit(
                f"missing manifest: {path}"
            )

        failures += verify_tsv(
            path
        )

    parent_summary = (
        root
        / "manifests"
        / "PARENT_LHE_SUMMARY.txt"
    )

    values = {}

    for line in parent_summary.read_text().splitlines():

        if "=" not in line:
            continue

        key, value = (
            line.split(
                "=",
                1,
            )
        )

        values[key] = value

    parent = Path(
        values["path"]
    )

    expected = (
        values["sha256"]
    )

    actual = digest(
        parent
    )

    if actual != expected:

        print(
            f"FAIL {parent}"
        )

        failures += 1

    else:

        print(
            f"PASS {parent}"
        )

    if failures:

        raise SystemExit(
            f"FROZEN_DATA_VERIFY=FAIL failures={failures}"
        )

    print(
        "FROZEN_DATA_VERIFY=PASS"
    )


if __name__ == "__main__":
    main()
PY

chmod +x \
  "$BUILD/tools/verify_frozen_data.py"


# ---------------------------------------------------------------------
# Hash every small file in the closeout itself.
# ---------------------------------------------------------------------

(
    cd "$BUILD"

    find . \
      -type f \
      ! -name 'CLOSEOUT_SHA256SUMS.txt' \
      -print0 \
    | sort -z \
    | xargs -0 sha256sum
) \
> "$BUILD/CLOSEOUT_SHA256SUMS.txt"


# Verify before publishing.
(
    cd "$BUILD"

    sha256sum -c \
      CLOSEOUT_SHA256SUMS.txt \
      >/dev/null
)

pass "CLOSEOUT_INTERNAL_SHA256"


# ---------------------------------------------------------------------
# Publish repo-side closeout atomically.
# ---------------------------------------------------------------------

mkdir -p \
  "$FREEZE_ROOT"

mv \
  "$BUILD" \
  "$FREEZE"

pass "REPO_CLOSEOUT_PUBLISHED"


# ---------------------------------------------------------------------
# Make a self-contained reproduction capsule on EOS.
#
# This contains:
#   - formal closeout
#   - original qualified recipe freeze
#   - corrected canonical shower worker
# ---------------------------------------------------------------------

mkdir -p \
  "$EOS_FREEZE"

CAPSULE_STAGE=$(
    mktemp -d \
      /tmp/phase12_reproduction_capsule.XXXXXX
)

trap \
  'rm -rf "$CAPSULE_STAGE"' \
  EXIT

mkdir -p \
  "$CAPSULE_STAGE"

cp -a \
  "$FREEZE" \
  "$CAPSULE_STAGE/closeout"

cp -a \
  "$RECIPE" \
  "$CAPSULE_STAGE/qualified_recipe"

cp -a \
  "$CANONICAL_SHOWER_WORKER" \
  "$CAPSULE_STAGE/canonical_shower_worker"

CAPSULE="$EOS_FREEZE/${RECIPE_ID}_reproduction_capsule.tar.gz"

tar -C \
  "$CAPSULE_STAGE" \
  -czf \
  "$CAPSULE" \
  .

sha256sum \
  "$CAPSULE" \
  > "$EOS_FREEZE/${RECIPE_ID}_reproduction_capsule.tar.gz.sha256"

pass "EOS_REPRODUCTION_CAPSULE"


# ---------------------------------------------------------------------
# Immutable pointers / marker records.
# ---------------------------------------------------------------------

cat > "$BASE/AUTHORITATIVE_PHASE12_PRODUCTION.txt" <<EOF
PHASE12_PRODUCTION=FROZEN

RECIPE_ID=$RECIPE_ID

PRODUCTION_ROOT=$P12

CLOSEOUT_ROOT=$FREEZE

EOS_CLOSEOUT_ROOT=$EOS_FREEZE

REPRODUCTION_CAPSULE=$CAPSULE

CANONICAL_FUTURE_SHOWER_WORKER=$CANONICAL_SHOWER_WORKER

WHIZARD_QUALIFIED_VERSION=3.1.8
PYTHIA_QUALIFIED_VERSION=8.315
HEPMC3_QUALIFIED_VERSION=3.3.1

NOMINAL_QED_POLICY=G0_H0
EOF

cat > "$P12/PRODUCTION_FROZEN.txt" <<EOF
PHASE12_PRODUCTION=FROZEN
RECIPE_ID=$RECIPE_ID
CLOSEOUT_ROOT=$FREEZE
EOS_CLOSEOUT_ROOT=$EOS_FREEZE
REPRODUCTION_CAPSULE=$CAPSULE
EOF


# ---------------------------------------------------------------------
# Final quick verification
# ---------------------------------------------------------------------

(
    cd "$FREEZE"

    sha256sum -c \
      CLOSEOUT_SHA256SUMS.txt \
      >/dev/null
)

sha256sum -c \
  "$EOS_FREEZE/${RECIPE_ID}_reproduction_capsule.tar.gz.sha256" \
  >/dev/null


echo
echo "================================================================"
echo "PHASE 12 FINAL FREEZE RESULT"
echo "================================================================"

echo "PHASE12_FINAL_FREEZE=PASS"
echo
echo "RECIPE_ID=$RECIPE_ID"
echo "PRODUCTION_ROOT=$P12"
echo "CLOSEOUT_ROOT=$FREEZE"
echo "EOS_CLOSEOUT_ROOT=$EOS_FREEZE"
echo "REPRODUCTION_CAPSULE=$CAPSULE"
echo
echo "PARENT_LHE_SHA256=$EXPECTED_PARENT_LHE_SHA256"
echo "NOMINAL_PHYSICS_SHA256=$NOMINAL_PHYSICS_SHA"
echo
echo "CANONICAL_FUTURE_SHOWER_WORKER=$CANONICAL_SHOWER_WORKER"
echo
echo "NEXT_STAGE=FCCANALYSES_INTEGRATION"
echo "================================================================"
