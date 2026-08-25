#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"

RECIPE_ID="${RECIPE_ID:-WT_A07F3_S0_exactchain_v1p0p1}"

BASE_PHASE12_TAG="${BASE_PHASE12_TAG:-phase12-WT_A07F3_S0-exactchain-v1p0p1-frozen}"

QUAL_ROOT="$REPO/phase12_production_v1/qualification_capsules"

FINAL="$QUAL_ROOT/$RECIPE_ID"

BUILD="${FINAL}.build.$$"

MAX_NORMAL_BYTES=$((5 * 1024 * 1024))
MAX_DIAGNOSTIC_BYTES=$((1 * 1024 * 1024))
MAX_CAPSULE_BYTES=$((200 * 1024 * 1024))

CAMPAIGN_ROOT="$REPO/campaigns/full6f_365gev_ee_ttbar_spinpol_v1"

PHASE10="$CAMPAIGN_ROOT/phase10A_production_definition"

PHASE11A="$CAMPAIGN_ROOT/phase11A_integration_qualification"

PHASE11_MPI="$CAMPAIGN_ROOT/phase11_mpi_integration_qualification_v1"

MPI_QUAL="$REPO/mpi_qualification"

P11_GRID_REUSE="$REPO/phase11_grid_reuse_validation_v1"

P11_READY="$REPO/phase11_production_readiness_v1"

P11_DIAGNOSTICS="$REPO/phase11_diagnostics"

P12_CLOSEOUT="$REPO/phase12_production_v1/production_closeout_v1/$RECIPE_ID"

P12_RECIPE="$REPO/phase12_production_v1/frozen_recipe_capsules/$RECIPE_ID"

cleanup() {
    rm -rf -- "$BUILD"
}

trap cleanup EXIT


banner() {
    echo
    echo "================================================================"
    echo "$*"
    echo "================================================================"
}


banner "PHASE 10/11 QUALIFICATION CAPSULE — PREFLIGHT"


test -d "$REPO/.git"

for required in \
    "$PHASE10" \
    "$PHASE11A" \
    "$PHASE11_MPI" \
    "$MPI_QUAL" \
    "$P11_GRID_REUSE" \
    "$P11_READY" \
    "$P12_CLOSEOUT" \
    "$P12_RECIPE"
do
    if [[ ! -d "$required" ]]; then
        echo "ERROR: required directory missing:"
        echo "  $required"
        exit 1
    fi
done

echo "REQUIRED_PHASE_ROOTS=PASS"


BASE_COMMIT=$(
    git -C "$REPO" rev-list \
        -n 1 \
        "$BASE_PHASE12_TAG"
)

HEAD_COMMIT=$(
    git -C "$REPO" rev-parse HEAD
)

if [[ "$HEAD_COMMIT" != "$BASE_COMMIT" ]]; then
    echo "ERROR: HEAD is not the frozen Phase-12 production commit."
    echo "BASE_COMMIT=$BASE_COMMIT"
    echo "HEAD_COMMIT=$HEAD_COMMIT"
    exit 1
fi

echo "BASE_PHASE12_COMMIT=$BASE_COMMIT"
echo "HEAD_MATCHES_BASE_PHASE12=PASS"


if [[ -e "$FINAL" ]]; then
    echo "ERROR: final qualification capsule already exists:"
    echo "  $FINAL"
    exit 1
fi


mkdir -p \
    "$BUILD/qualification_sources" \
    "$BUILD/repo_support" \
    "$BUILD/provenance" \
    "$BUILD/tools"


SOURCE_MANIFEST="$BUILD/SOURCE_FILE_MANIFEST.tsv"

TREE_SUMMARY="$BUILD/SOURCE_TREE_SUMMARY.tsv"

EXTERNAL_POINTERS="$BUILD/EXTERNAL_ARTIFACT_POINTERS.tsv"


printf \
'category\tsource_path\tcapsule_path\tbytes\tsha256\tmaterialized_symlink\n' \
    > "$SOURCE_MANIFEST"

printf \
'category\tsource_root\tcopied_files\tcopied_bytes\tskipped_files\n' \
    > "$TREE_SUMMARY"

printf \
'category\tsource_path\tbytes\treason\n' \
    > "$EXTERNAL_POINTERS"


is_backup_or_cache() {

    local rel="$1"

    case "$rel" in

        *"/__pycache__/"*|\
        __pycache__/*|\
        *.pyc|\
        *.pyo|\
        *.swp|\
        *~|\
        *.bak|\
        *.before_*|\
        *".build."*|\
        */.git/*)

            return 0
            ;;

    esac

    return 1
}


is_large_mc_or_package() {

    local rel="$1"

    case "$rel" in

        *.lhe|\
        *.lhe.gz|\
        *.hepmc|\
        *.hepmc2|\
        *.hepmc3|\
        *.root|\
        *.tar|\
        *.tar.gz|\
        *.tgz|\
        *.zip|\
        *.onnx|\
        *.so|\
        *.a|\
        *.o|\
        *.pcm|\
        core.*)

            return 0
            ;;

    esac

    return 1
}


important_external_pointer() {

    local rel="$1"

    case "$rel" in

        *S0*|\
        *grid*|\
        *Grid*|\
        *workspace*|\
        *Workspace*|\
        *manifest*|\
        *Manifest*|\
        *closeout*|\
        *Closeout*|\
        *validation*|\
        *Validation*|\
        *rehearsal*|\
        *Rehearsal*|\
        *100k*|\
        *B0*|\
        *B1*|\
        *B2*|\
        *C0*)

            return 0
            ;;

    esac

    return 1
}


copy_one() {

    local category="$1"
    local src="$2"
    local dst_rel="$3"

    local dst="$BUILD/$dst_rel"

    local materialized=0

    if [[ -L "$src" ]]; then
        materialized=1
    fi

    local size

    size=$(
        stat -Lc '%s' "$src"
    )

    mkdir -p \
        "$(dirname "$dst")"

    cp -L -p \
        "$src" \
        "$dst"

    local sha

    sha=$(
        sha256sum "$dst" \
        | awk '{print $1}'
    )

    printf \
'%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$category" \
        "$src" \
        "$dst_rel" \
        "$size" \
        "$sha" \
        "$materialized" \
        >> "$SOURCE_MANIFEST"
}


copy_tree_curated() {

    local category="$1"
    local root="$2"
    local dst_prefix="$3"
    local mode="${4:-normal}"

    local max_bytes="$MAX_NORMAL_BYTES"

    if [[ "$mode" == "diagnostic" ]]; then
        max_bytes="$MAX_DIAGNOSTIC_BYTES"
    fi

    local copied=0
    local skipped=0
    local copied_bytes=0

    while IFS= read -r -d '' src
    do

        local rel

        rel="${src#"$root"/}"

        if is_backup_or_cache "$rel"; then
            skipped=$((skipped + 1))
            continue
        fi

        local size

        size=$(
            stat -Lc '%s' "$src" \
            2>/dev/null \
            || echo 0
        )

        if is_large_mc_or_package "$rel"; then

            skipped=$((skipped + 1))

            if important_external_pointer "$rel"; then
                printf \
'%s\t%s\t%s\tlarge-MC-or-package\n' \
                    "$category" \
                    "$src" \
                    "$size" \
                    >> "$EXTERNAL_POINTERS"
            fi

            continue
        fi

        if (( size > max_bytes )); then

            skipped=$((skipped + 1))

            if important_external_pointer "$rel"; then
                printf \
'%s\t%s\t%s\tabove-Git-capsule-size-threshold\n' \
                    "$category" \
                    "$src" \
                    "$size" \
                    >> "$EXTERNAL_POINTERS"
            fi

            continue
        fi

        copy_one \
            "$category" \
            "$src" \
            "$dst_prefix/$rel"

        copied=$((copied + 1))
        copied_bytes=$((copied_bytes + size))

    done < <(
        find "$root" \
            \( -type f -o -type l \) \
            -print0 \
        | sort -z
    )

    printf \
'%s\t%s\t%s\t%s\t%s\n' \
        "$category" \
        "$root" \
        "$copied" \
        "$copied_bytes" \
        "$skipped" \
        >> "$TREE_SUMMARY"

    echo \
        "COPIED_TREE category=$category files=$copied bytes=$copied_bytes skipped=$skipped"
}


banner "COPYING AUTHORITATIVE QUALIFICATION TREES"


copy_tree_curated \
    "phase10A_production_definition" \
    "$PHASE10" \
    "qualification_sources/phase10A_production_definition"


copy_tree_curated \
    "phase11A_integration_qualification" \
    "$PHASE11A" \
    "qualification_sources/phase11A_integration_qualification"


copy_tree_curated \
    "phase11_mpi_integration_qualification" \
    "$PHASE11_MPI" \
    "qualification_sources/phase11_mpi_integration_qualification_v1"


copy_tree_curated \
    "mpi_qualification" \
    "$MPI_QUAL" \
    "qualification_sources/mpi_qualification"


copy_tree_curated \
    "phase11_grid_reuse_validation" \
    "$P11_GRID_REUSE" \
    "qualification_sources/phase11_grid_reuse_validation_v1"


copy_tree_curated \
    "phase11_production_readiness" \
    "$P11_READY" \
    "qualification_sources/phase11_production_readiness_v1"


if [[ -d "$P11_DIAGNOSTICS" ]]; then

    copy_tree_curated \
        "phase11_historical_diagnostics" \
        "$P11_DIAGNOSTICS" \
        "qualification_sources/phase11_historical_diagnostics" \
        "diagnostic"

fi


banner "COPYING QUALIFIED MPI PROVENANCE"


for prov in \
    "$REPO/provenance/phase11_mpi_worker_qualified_20260811T210006Z" \
    "$REPO/provenance/phase11_mpi_worker_pre_smoke_20260811T194828Z" \
    "$REPO/provenance/phase11_mpi_rank_merge_pre_regression_20260811T202402Z"
do

    if [[ -d "$prov" ]]; then

        label=$(
            basename "$prov"
        )

        copy_tree_curated \
            "provenance_$label" \
            "$prov" \
            "provenance/$label"

    fi

done


banner "COPYING REPOSITORY SUPPORT SOURCES"


required_support_files=(

    "scripts/production/audit_full6f_lhe_weights.py"

    "scripts/production/audit_full6f_whizard_logs.py"

    "scripts/production/build_phase11_lr_integration_qualification.py"

    "scripts/production/closeout_phase10_full6f_365gev.sh"

    "scripts/production/collect_full6f_production.py"

    "scripts/production/merge_mpi_lhe.py"

    "scripts/production/run_full6f_production_shard.sh"

    "scripts/production/run_whizard_failfast.py"

    "scripts/production/validate_phase10A_full6f_worker_replay.py"

    "scripts/condor/run_full6f_production_job.sh"

    "scripts/condor/run_full6f_production_job_encoded_iterations.sh"

    "scripts/sindarin/render_full6f_cards.py"

    "scripts/sindarin/validate_phase4_cards.py"

    "environments/setup_whizard_3p1p8_mpi_qualified.sh"
)


printf \
'path\tgit_status\n' \
    > "$BUILD/provenance/REPO_SUPPORT_GIT_STATE.tsv"


for rel in "${required_support_files[@]}"
do

    src="$REPO/$rel"

    if [[ ! -f "$src" ]]; then
        echo "ERROR: required support source missing:"
        echo "  $rel"
        exit 1
    fi

    copy_one \
        "repo_support_current" \
        "$src" \
        "repo_support/$rel"

    status=$(
        git -C "$REPO" status \
            --short \
            -- "$rel" \
        | tr '\n' ';'
    )

    printf \
'%s\t%s\n' \
        "$rel" \
        "$status" \
        >> "$BUILD/provenance/REPO_SUPPORT_GIT_STATE.tsv"

done

echo "REQUIRED_SUPPORT_FILES=PASS"


if [[ -d "$REPO/sindarin/templates/full6f_365gev_v1" ]]; then

    copy_tree_curated \
        "current_sindarin_template_support" \
        "$REPO/sindarin/templates/full6f_365gev_v1" \
        "repo_support/sindarin/templates/full6f_365gev_v1"

fi


for optional_tree in \
    "scripts/reproducibility" \
    "condor/production" \
    "condor/pilots" \
    "condor_streams"
do

    if [[ -d "$REPO/$optional_tree" ]]; then

        safe_name=$(
            echo "$optional_tree" \
            | tr '/' '_'
        )

        copy_tree_curated \
            "optional_$safe_name" \
            "$REPO/$optional_tree" \
            "repo_support/$optional_tree"

    fi

done


banner "WRITING QUALIFICATION CONTRACT"


cat > "$BUILD/QUALIFICATION_REPRODUCTION_CONTRACT.md" <<EOF
# Phase 10/11 qualification reproduction contract

Recipe ID:

\`$RECIPE_ID\`

Base production-freeze tag:

\`$BASE_PHASE12_TAG\`

Base production-freeze commit:

\`$BASE_COMMIT\`

This capsule supplements the immutable Phase-12 production freeze.

It preserves the small source/configuration/validation surface required
to understand and rerun the qualification that led to the Phase-12
production recipe. Large Monte Carlo outputs, large workspaces, and
other bulky runtime artifacts are intentionally not duplicated in Git.

The final Phase-12 production recipe and formal production data
closeout remain in:

- \`phase12_production_v1/frozen_recipe_capsules/$RECIPE_ID/\`
- \`phase12_production_v1/production_closeout_v1/$RECIPE_ID/\`

## Phase 10 — production-definition qualification

Phase 10 establishes the hard-process production contract.

The preserved evidence covers:

1. the 365 GeV full-six-fermion process definition;
2. the WT resonance-restricted signal definition;
3. beam/polarization assumptions;
4. active WHIZARD model and parameter provenance;
5. runtime card rendering;
6. seed syntax and deterministic seed handling;
7. seed replay checks;
8. representative LHE headers and init blocks;
9. production worker replay and localization checks;
10. qualification/production manifest validation.

The authoritative recovered Phase-10 evidence is under:

\`qualification_sources/phase10A_production_definition/\`

## Phase 11A — MPI/VAMP implementation qualification

This phase establishes that the selected parallel WHIZARD integration
implementation behaves correctly before using it for production
qualification.

Preserved inputs/evidence include the Phase-11A campaign tree,
MPI qualification tree, qualified-worker provenance, rank-merge
checks, worker/runtime scripts, and encoded-iteration support.

## Phase 11B — integration-prescription qualification

The qualification logic was:

- A0/A1/A2: initial independent prescription replicas;
- B0: predetermined candidate for the stronger B prescription;
- B1/B2: independent qualification replicas when B0 passes;
- C0: over-integration/saturation check;
- C1/C2: required only if C must become the qualified prescription;
- D: conditional stronger prescription if C has not saturated.

The production grid is never selected by choosing the replica with
the most attractive statistical fluctuation.

The predetermined qualified grid is S0/B0 once the complete B
prescription passes the predefined gates.

Qualification checks include:

- cross-section stability;
- reported integration uncertainty;
- integration convergence;
- generation diagnostics;
- unweighting behavior;
- excess-weight behavior;
- consistency among independent replicas.

## Phase 11C — single frozen-grid reuse validation

A single qualified frozen grid was tested against an independent
multi-grid reference.

The acceptance criterion is statistical compatibility of predefined
physics observables, not byte-for-byte histogram identity.

The qualification additionallhat generation does not mutate
or reintegrate the frozen workspace.

## Phase 11D — generation scaling

Generation throughput/resource behavior is checked at increasing shard
sizes, including the qualified 25k-event production point.

The study covers:

- events per second;
- memory behavior;
- output integrity;
- unweighting efficiency;
- excess-weight diagnostics;
- generation-rank behavior.

The Phase-12 production choice is one MPI rank per generation shard and
25k hard events per shard.

## Phase 11E — exact-chain rehearsal

An approximately 100k-event rehearsal uses the same production chain
intended for Phase 12:

WHIZARD frozen grid
-> raw LHE
-> canonical ISR normalization
-> history-preserving serializer
-> strict topology validation
-> PYTHIA
-> HepMC3

Validation RNG seeds are kept disjoint from final Phase-12 production
seeds and validation events are not reused in the final physics sample.

## Phase-12 production rule established by Phase 10/11

The qualified production architecture is:

- WHIZARD 3.1.8;
- sqrt(s) = 365 GeV;
- LR100;
- WT-restricted full-six-fermion process;
- VAMP2;
- rng_stream;
- predetermined frozen S0 grid;
- one MPI rank per generation job;
- 25k hard events per shard;
- independent hard-generation seeds;
- independent PYTHIA seeds;
- WHIZARD ISR retained;
- PYTHIA ISR disabled;
- PYTHIA FSR enabled;
- MPI disabled in PYTHIA;
- top decay ownership retained by WHIZARD;
- exact history-preserving serialization.

## Authority rule

When duplicate source files exist:

1. exact snapshots embedded in qualification campaign directories take
   precedence;
2. frozen Phase-12 recipe files take precedence for final production;
3. files under \`repo_support/\` are convenience copies of the current
   working-tree implementations and their Git state is recorded
   explicitly.

Historical failed/diagnostic experiments are context, not qualified
production recipes.

A change to process physics, beam configuration, perturbative order,
integration prescription, ISR/decay ownership, nominal PYTHIA policy,
history serialization, or materially different generator versions
requires a new qualification.
EOF


cat > "$BUILD/REPRODUCTION_ORDER.md" <<'EOF'
# Recommended qualification replay order

## 1. Phase 10

Start with:

    qualification_sources/phase10A_production_definition/

Use the preserved manifest/config/model/seed evidence to establish the
hard-process production contract.

Relevant reusable support code is under:

    repo_support/scripts/production/
    repo_support/scripts/sindarin/

## 2. Phase 11A

Replay MPI/VAMP implementation qualification using:

    qualification_sources/phase11A_integration_qualification/
    qualification_sources/phase11_mpi_integration_qualification_v1/
    qualification_sources/mpi_qualification/

Cross-check against:

    provenance/

## 3. Phase 11B

Reproduce the integration-prescription comparison in the historical
order A -> B -> C, with D conditional.

Do not select a stochastic grid after looking at which replica gives
the most favorable diagnostics.

## 4. Phase 11C

Replay frozen-grid reuse validation from:

    qualification_sources/phase11_grid_reuse_validation_v1/

Require statistical compatibility between the predetermined single-grid
sample and the independent multi-grid reference.

## 5. Phase 11D

Replay generation scaling/resource checks from the preserved
production-readiness sources.

The production target to recover is:

    one MPI rank
    25k hard events per shard

## 6. Phase 11E

Replay the exact-chain rehearsal from:

    qualificatsources/phase11_production_readiness_v1/

The rehearsal chain must match the frozen Phase-12 production chain.

## 7. Phase 12

Once qualification passes, use:

    ../../frozen_recipe_capsules/WT_A07F3_S0_exactchain_v1p0p1/

and verify output against:

    ../../production_closeout_v1/WT_A07F3_S0_exactchain_v1p0p1/
EOF


cat > "$BUILD/README.md" <<EOF
# Phase 10/11 qualification-reproduction capsule

This is the Git-resident qualification supplement for:

\`$RECIPE_ID\`

It is intended to answer not only:

> How do I run the qualified Phase-12 recipe?

but also:

> How was the integration/grid/seed/generation architecture qualified?

The immutable Phase-12 production tag is:

\`$BASE_PHASE12_TAG\`

at commit:

\`$BASE_COMMIT\`

This capsule is deliberately additive. It does not alter the original
production-freeze commit or tag.

## Main directories

- \`qualification_sources/phase10A_production_definition/\`
  - hard-process definition, runtime/model audit, seed qualification,
    LHE/worker replay evidence.

- \`qualification_sources/phase11A_integration_qualification/\`
  - initial integration qualification.

- \`qualification_sources/phase11_mpi_integration_qualification_v1/\`
  - MPI/VAMP integration qualification.

- \`qualification_sources/mpi_qualification/\`
  - MPI implementation qualification material.

- \`qualification_sources/phase11_grid_reuse_validation_v1/\`
  - predetermined single-grid versus multi-grid validation.

- \`qualification_sources/phase11_production_readiness_v1/\`
  - final production-readiness work including later Phase-11 gates.

- \`qualification_sources/phase11_historical_diagnostics/\`
  - small diagnostic/history records only; these are not authoritative
    production recipes.

- \`provenance/\`
  - qualified MPI-worker/rank-merge provenance snapshots.

- \`repo_support/\`
  - current small support scripts/configs useful to replay qualification.
    Their Git working-tree state at capsule creation is recorded.

## Large artifacts

Large LHE/HepMC/ROOT/archive/binary outputs are intentionally not copied
into Git.

Important omitted artifacts are recorded where discoverable in:

\`EXTERNAL_ARTIFACT_POINTERS.tsv\`

Paths embedded in the copied evidence are also extracted into:

\`EXTERNAL_PATH_REFERENCES.txt\`

The final qualified production grid/recipe is already frozen in the
Phase-12 recipe capsule, and the final production data are checksum
indexed by the Phase-12 closeout.

## Verification

Run:

    python3 tools/verify_qualification_capsule.py

A successful result must end with:

    QUALIFICATION_CAPSULE_VERIFY=PASS
EOF


banner "CAPTURING BUILD PROVENANCE"


{
    echo "recipe_id=$RECIPE_ID"
    echo "base_phase12_tag=$BASE_PHASE12_TAG"
    echo "base_phase12_commit=$BASE_COMMIT"
    echo "git_branch=$(git -C "$REPO" branch --show-current)"
    echo "build_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "hostname=$(hostname -f 2>/dev/null || hostname)"
    echo "user=${USER:-unknown}"
} > "$BUILD/provenance/CAPSULE_BUILD_ENVIRONMENT.txt"


git -C "$REPO" status \
    --short \
    > "$BUILD/provenance/GIT_STATUS_AT_QUALIFICATION_CAPSULE_BUILD.txt"


banner "EXTRACTING EXTERNAL PATH REFERENCES"


python3 - "$BUILD" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

pattern = re.compile(
    rb'/(?:eos|afs)/[^\s"\'<>]+'
)

paths = set()

for path in root.rglob("*"):

    if not path.is_file():
        continue

    if path.name in {
        "QUALIFICATION_CAPSULE_SHA256SUMS.txt",
        "EXTERNAL_PATH_REFERENCES.txt",
    }:
        continue

    try:
        data = path.read_bytes()
    except OSError:
        continue

    for match in pattern.findall(data):
        try:
            value = match.decode(
                "utf-8",
                errors="strict",
            )
        except UnicodeDecodeError:
            continue

        value = value.rstrip(
            ".,;:)]}"
        )

        paths.add(value)

out = root / "EXTERNAL_PATH_REFERENCES.txt"

out.write_text(
    "\n".join(
        sorted(paths)
    )
    + (
        "\n"
        if paths
        else ""
    )
)

print(
    f"EXTERNAL_PATH_REFERENCES={len(paths)}"
)
PY


banner "WRITING VERIFIER"


cat > "$BUILD/tools/verify_qualification_capsule.py" <<'PY'
#!/usr/bin/env python3

from __future__ import annotations

import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

SHA_FILE = (
    ROOT
    / "QUALIFICATION_CAPSULE_SHA256SUMS.txt"
)


REQUIRED = [

    ROOT
    / "QUALIFICATION_REPRODUCTION_CONTRACT.md",

    ROOT
    / "REPRODUCTION_ORDER.md",

    ROOT
    / "SOURCE_FILE_MANIFEST.tsv",

    ROOT
    / "SOURCE_TREE_SUMMARY.tsv",

    ROOT
    / "qualification_sources"
    / "phase10A_production_definition",

    ROOT
    / "qualification_sources"
    / "phase11A_integration_qualification",

    ROOT
    / "qualification_sources"
    / "phase11_mpi_integration_qualification_v1",

    ROOT
    / "qualification_sources"
    / "mpi_qualification",

    ROOT
    / "qualification_sources"
    / "phase11_grid_reuse_validation_v1",

    ROOT
    / "qualification_sources"
    / "phase11_production_readiness_v1",

    ROOT
    / "repo_support"
    / "scripts"
    / "production"
    / "build_phase11_lr_integration_qualification.py",

    ROOT
    / "repo_support"
    / "scripts"
    / "production"
    / "run_full6f_production_shard.sh",

    ROOT
    / "repo_support"
    / "scripts"
    / "condor"
    / "run_full6f_production_job.sh",

    ROOT
    / "repo_support"
    / "environments"
    / "setup_whizard_3p1p8_mpi_qualified.sh",
]


def sha256(path: Path) -> str:

    h = hashlib.sha256()

    with path.open("rb") as stream:

        while True:

            block = stream.read(
                1024 * 1024
            )

            if not block:
                break

            h.update(block)

    return h.hexdigest()


for path in REQUIRED:

    if not path.exists():

        raise SystemExit(
            "REQUIRED_PATH_GATE=FAIL: "
            f"{path}"
        )


print(
    "REQUIRED_PATH_GATE=PASS"
)


symlinks = [
    path
    for path in ROOT.rglob("*")
    if path.is_symlink()
]

if symlinks:

    for path in symlinks:
        print(
            f"UNEXPECTED_SYMLINK={path}"
        )

    raise SystemExit(
        "SYMLINK_GATE=FAIL"
    )


print(
    "SYMLINK_GATE=PASS"
)


if not SHA_FILE.is_file():

    raise SystemExit(
        "SHA256_MANIFEST_GATE=FAIL: "
        "manifest missing"
    )


checked = 0


for line in SHA_FILE.read_text().splitlines():

    if not line.strip():
        continue

    expected, rel = line.split(
        None,
        1,
    )

    rel = rel.strip()

    if rel.startswith("./"):
        rel = rel[2:]

    path = ROOT / rel

    if not path.is_file():

        raise SystemExit(
            "SHA256_MANIFEST_GATE=FAIL: "
            f"missing {rel}"
        )

    actual = sha256(path)

    if actual != expected:

        raise SystemExit(
            "SHA256_MANIFEST_GATE=FAIL: "
            f"{rel}\n"
            f"expected={expected}\n"
            f"actual={actual}"
        )

    checked += 1


print(
    f"SHA256_FILES_CHECKED={checked}"
)

print(
    "SHA256_MANIFEST_GATE=PASS"
)


source_manifest = (
    ROOT
    / "SOURCE_FILE_MANIFEST.tsv"
)

rows = (
    source_manifest
    .read_text()
    .splitlines()
)

if len(rows) <= 1:

    raise SystemExit(
        "SOURCE_MANIFEST_GATE=FAIL"
    )


print(
    f"SOURCE_MANIFEST_ROWS={len(rows)-1}"
)

print(
    "SOURCE_MANIFEST_GATE=PASS"
)

print(
    "QUALIFICATION_CAPSULE_VERIFY=PASS"
)
PY


chmod +x \
    "$BUILD/tools/verify_qualification_capsule.py"


banner "CAPSULE SIZE GATE"


CAPSULE_BYTES=$(
    python3 - "$BUILD" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])

print(
    sum(
        p.stat().st_size
        for p in root.rglob("*")
        if p.is_file()
    )
)
PY
)

echo "CAPSULE_BYTES=$CAPSULE_BYTES"


if (( CAPSULE_BYTES > MAX_CAPSULE_BYTES )); then

    echo "ERROR: capsule exceeds Git size budget."
    echo "MAX_CAPSULE_BYTES=$MAX_CAPSULE_BYTES"

    exit 1

fi

echo "CAPSULE_SIZE_GATE=PASS"


banner "WRITING SHA256 MANIFEST"


(
    cd "$BUILD"

    find . \
        -type f \
        ! -name 'QUALIFICATION_CAPSULE_SHA256SUMS.txt' \
        -print0 \
    | sort -z \
    | xargs -0 sha256sum

) > "$BUILD/QUALIFICATION_CAPSULE_SHA256SUMS.txt"


python3 \
    "$BUILD/tools/verify_qualification_capsule.py"


banner "PUBLISHING QUALIFICATION CAPSULE"


mkdir -p "$QUAL_ROOT"

mv \
    "$BUILD" \
    "$FINAL"

trap - EXIT


echo "QUALIFICATION_CAPSULE_PUBLISHED=PASS"

echo
echo "QUALIFICATION_CAPSULE=$FINAL"

echo
echo "NEXT=stage-and-audit-qualification-capsule"
