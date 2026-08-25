#!/usr/bin/env bash

set -Eeuo pipefail

###############################################################################
# Phase-10 closeout
#
# Purpose:
#   Preserve the successful 365 GeV direct-full6f Phase-10 qualification
#   campaign without modifying or duplicating the large LHE payload.
#
# This script:
#   - verifies the expected 74 successful shards / 740000 events;
#   - hashes every successful LHE;
#   - records metadata/config hashes;
#   - snapshots all quality-audit products;
#   - archives the failed unpolarized shard_0018 diagnostics;
#   - records Condor history where available;
#   - writes an explicit QUALIFICATION_ONLY status;
#   - records repository provenance.
#
# It does NOT:
#   - delete anything;
#   - move LHE files;
#   - chmod LHE files;
#   - attempt to regenerate shard_0018.
###############################################################################

export REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"
export CAMPAIGN_ID="${CAMPAIGN_ID:-full6f_365gev_ee_ttbar_spinpol_v1}"
export PRODUCTION_ID="${PRODUCTION_ID:-phase10_production_v1}"

cd "$REPO"

source "$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh"

export PROD_ROOT="/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/$CAMPAIGN_ID/$PRODUCTION_ID"

export EOS_CLOSEOUT="$PROD_ROOT/closeout"
export REPO_CLOSEOUT="$REPO/campaigns/$CAMPAIGN_ID/phase10B_closeout"

export QUALITY_DIR="$PROD_ROOT/quality_audit"

mkdir -p \
  "$EOS_CLOSEOUT" \
  "$EOS_CLOSEOUT/audits" \
  "$EOS_CLOSEOUT/failed_shard_diagnostics" \
  "$EOS_CLOSEOUT/provenance" \
  "$REPO_CLOSEOUT"

###############################################################################
# Locate authoritative latest audits.
###############################################################################

latest_file() {
  local directory="$1"
  local pattern="$2"

  find "$directory" \
    -maxdepth 1 \
    -type f \
    -name "$pattern" \
    -printf '%T@ %p\n' \
    | sort -nr \
    | sed -n '1s/^[^ ]* //p'
}

QUALITY_CSV="$(
  latest_file \
    "$QUALITY_DIR" \
    'full6f_whizard_quality_*.csv'
)"

QUALITY_JSON="$(
  latest_file \
    "$QUALITY_DIR" \
    'full6f_whizard_quality_*.json'
)"

WEIGHT_CSV="$(
  latest_file \
    "$QUALITY_DIR" \
    'full6f_lhe_weight_audit_*.csv'
)"

for required in \
  "$QUALITY_CSV" \
  "$QUALITY_JSON" \
  "$WEIGHT_CSV"
do
  if [[ -z "$required" || ! -s "$required" ]]; then
    echo "ERROR: missing required Phase-10 audit product: $required" >&2
    exit 1
  fi
done

echo "QUALITY_CSV=$QUALITY_CSV"
echo "QUALITY_JSON=$QUALITY_JSON"
echo "WEIGHT_CSV=$WEIGHT_CSV"

###############################################################################
# Build immutable-by-checksum logical manifest.
###############################################################################

MANIFEST="$EOS_CLOSEOUT/successful_lhe_manifest.tsv"
SUMMARY_JSON="$EOS_CLOSEOUT/phase10_closeout_summary.json"

python3 - \
  "$PROD_ROOT" \
  "$MANIFEST" \
  "$SUMMARY_JSON" <<'PY'
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


prod_root = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
summary_path = Path(sys.argv[3])

expected_shards = {
    "f6f365_ee_LR100_epmum": 25,
    "f6f365_ee_RL100_epmum": 25,
    "f6f365_ee_unpol_epmum": 24,
}

expected_events = {
    "f6f365_ee_LR100_epmum": 250000,
    "f6f365_ee_RL100_epmum": 250000,
    "f6f365_ee_unpol_epmum": 240000,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(16 * 1024 * 1024)

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def lhe_hash_and_events(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    events = 0

    with path.open("rb") as handle:
        for line in handle:
            digest.update(line)

            if line.lstrip().startswith(b"<event"):
                events += 1

    return digest.hexdigest(), events


rows: list[dict[str, object]] = []

runs_root = prod_root / "runs"

for sample_id in sorted(expected_shards):
    subprocess_id = "epmum"
    sample_run_root = runs_root / sample_id / subprocess_id

    if not sample_run_root.is_dir():
        raise SystemExit(
            f"ERROR: missing sample run root: {sample_run_root}"
        )

    for run_dir in sorted(sample_run_root.glob("shard_*")):
        success = run_dir / "SUCCESS"

        if not success.is_file():
            continue

        shard_label = run_dir.name

        lhe = (
            prod_root
            / "lhe_raw"
            / sample_id
            / subprocess_id
            / f"{sample_id}__{subprocess_id}__{shard_label}.lhe"
        )

        metadata = run_dir / "run_metadata.json"
        integration = run_dir / "effective_common" / "integration.inc"
        process = run_dir / "effective_process.sin"

        required = [
            lhe,
            metadata,
            integration,
            process,
        ]

        for path in required:
            if not path.is_file() or path.stat().st_size <= 0:
                raise SystemExit(
                    f"ERROR: successful shard has missing/empty artifact: "
                    f"{path}"
                )

        lhe_sha256, n_events = lhe_hash_and_events(lhe)

        rows.append(
            {
                "sample_id": sample_id,
                "subprocess_id": subprocess_id,
                "shard_label": shard_label,
                "events": n_events,
                "lhe_size_bytes": lhe.stat().st_size,
                "lhe_sha256": lhe_sha256,
                "metadata_sha256": sha256_file(metadata),
                "integration_sha256": sha256_file(integration),
                "process_sha256": sha256_file(process),
                "lhe_path": str(lhe),
                "run_dir": str(run_dir),
            }
        )


counts = Counter(
    str(row["sample_id"])
    for row in rows
)

events = Counter()

for row in rows:
    events[str(row["sample_id"])] += int(row["events"])


for sample_id, expected in expected_shards.items():
    observed = counts[sample_id]

    if observed != expected:
        raise SystemExit(
            f"ERROR: {sample_id}: successful shards={observed}, "
            f"expected={expected}"
        )


for sample_id, expected in expected_events.items():
    observed = events[sample_id]

    if observed != expected:
        raise SystemExit(
            f"ERROR: {sample_id}: events={observed}, "
            f"expected={expected}"
        )


if len(rows) != 74:
    raise SystemExit(
        f"ERROR: total successful shards={len(rows)}, expected=74"
    )

total_events = sum(int(row["events"]) for row in rows)

if total_events != 740000:
    raise SystemExit(
        f"ERROR: total events={total_events}, expected=740000"
    )


manifest_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

fieldnames = list(rows[0].keys())

with manifest_path.open(
    "w",
    encoding="utf-8",
    newline="",
) as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=fieldnames,
        delimiter="\t",
    )

    writer.writeheader()
    writer.writerows(rows)


summary = {
    "campaign_id": "full6f_365gev_ee_ttbar_spinpol_v1",
    "production_id": "phase10_production_v1",
    "status": "FROZEN_QUALIFICATION_ONLY",
    "precision_production_approved": False,
    "successful_shards": len(rows),
    "successful_events": total_events,
    "samples": {
        sample_id: {
            "successful_shards": counts[sample_id],
            "successful_events": events[sample_id],
        }
        for sample_id in sorted(expected_shards)
    },
    "known_failed_or_missing_shards": [
        {
            "sample_id": "f6f365_ee_unpol_epmum",
            "subprocess_id": "epmum",
            "shard_label": "shard_0018",
            "status": "FAILED_NOT_REGENERATED",
        }
    ],
    "qualification_reason": [
        "Phase-10 uses an intentionally light integration configuration.",
        "Per-shard WHIZARD integration uncertainties are O(6-8%).",
        "Large shard-to-shard integral variation is present.",
        "Excess-weight diagnostics contain severe outliers.",
        "Stored LHE events were independently verified to have constant "
        "positive event weights.",
    ],
    "next_stage": "phase11_integration_qualification_v1",
}

summary_path.write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PHASE10_DATA_INTEGRITY=PASS")
print(f"SUCCESSFUL_SHARDS={len(rows)}")
print(f"SUCCESSFUL_EVENTS={total_events}")

for sample_id in sorted(expected_shards):
    print(
        f"{sample_id}: "
        f"shards={counts[sample_id]} "
        f"events={events[sample_id]}"
    )

print(f"WROTE_MANIFEST={manifest_path}")
print(f"WROTE_SUMMARY={summary_path}")
PY

###############################################################################
# Copy the small audit products into the explicit closeout area.
###############################################################################

cp -a \
  "$QUALITY_CSV" \
  "$QUALITY_JSON" \
  "$WEIGHT_CSV" \
  "$EOS_CLOSEOUT/audits/"

###############################################################################
# Preserve all currently available quality-audit records as one snapshot.
###############################################################################

tar -czf \
  "$EOS_CLOSEOUT/audits/phase10_quality_audit_snapshot.tar.gz" \
  -C "$PROD_ROOT" \
  quality_audit

###############################################################################
# Preserve failed shard_0018 diagnostics.
###############################################################################

FAILED_SAMPLE="f6f365_ee_unpol_epmum"
FAILED_SUBPROCESS="epmum"
FAILED_SHARD="shard_0018"

FAILED_RUN="$PROD_ROOT/runs/$FAILED_SAMPLE/$FAILED_SUBPROCESS/$FAILED_SHARD"

if [[ -d "$FAILED_RUN" ]]; then
  tar -czf \
    "$EOS_CLOSEOUT/failed_shard_diagnostics/${FAILED_SAMPLE}__${FAILED_SUBPROCESS}__${FAILED_SHARD}.tar.gz" \
    -C "$(dirname "$FAILED_RUN")" \
    "$FAILED_SHARD"
fi

if [[ -s "$FAILED_RUN/whizard_return_code.txt" ]]; then
  cp -a \
    "$FAILED_RUN/whizard_return_code.txt" \
    "$EOS_CLOSEOUT/failed_shard_diagnostics/"
fi

if [[ -s "$FAILED_RUN/console.log" ]]; then
  cp -a \
    "$FAILED_RUN/console.log" \
    "$EOS_CLOSEOUT/failed_shard_diagnostics/${FAILED_SAMPLE}__${FAILED_SHARD}__console.log"
fi

###############################################################################
# Preserve Condor recovery history where still available.
###############################################################################

{
  echo "RECORDED_UTC=$(date -u --iso-8601=seconds)"
  echo
  echo "=== condor_q 11966179 ==="
  condor_q 11966179 -long 2>&1 || true

  echo
  echo "=== condor_history 11966179 ==="
  condor_history 11966179 -long 2>&1 || true

  echo
  echo "=== condor_history 11966179.1 ==="
  condor_history 11966179.1 -limit 1 -long 2>&1 || true
} > \
  "$EOS_CLOSEOUT/failed_shard_diagnostics/condor_recovery_11966179.txt"

###############################################################################
# Record representative effective integration configuration.
###############################################################################

for spec in \
  "f6f365_ee_LR100_epmum shard_0015" \
  "f6f365_ee_RL100_epmum shard_0020" \
  "f6f365_ee_unpol_epmum shard_0006"
do
  read -r sample shard <<< "$spec"

  source_file="$PROD_ROOT/runs/$sample/epmum/$shard/effective_common/integration.inc"
  output_file="$EOS_CLOSEOUT/provenance/${sample}__${shard}__integration.inc"

  if [[ -s "$source_file" ]]; then
    cp -a "$source_file" "$output_file"
  fi
done

###############################################################################
# Repository provenance.
###############################################################################

git rev-parse HEAD \
  > "$EOS_CLOSEOUT/provenance/git_commit.txt"

git status --short \
  > "$EOS_CLOSEOUT/provenance/git_status.txt"

git diff \
  > "$EOS_CLOSEOUT/provenance/repository_diff.patch"

whizard --version \
  > "$EOS_CLOSEOUT/provenance/whizard_version.txt" \
  2>&1

pythia8-config --version \
  > "$EOS_CLOSEOUT/provenance/pythia8_version.txt"

HepMC3-config --version \
  > "$EOS_CLOSEOUT/provenance/hepmc3_version.txt"

###############################################################################
# Explicit dataset warning/label.
###############################################################################

cat > "$PROD_ROOT/PHASE10_QUALIFICATION_ONLY.md" <<'EOF'
# Phase 10 status: qualification only

Campaign:

`full6f_365gev_ee_ttbar_spinpol_v1 / phase10_production_v1`

This dataset is intentionally preserved as a generator qualification,
debugging, interface-development, and regression dataset.

It is NOT approved as the authoritative precision-production sample for:

- final cross sections,
- polarization closure,
- spin-density-matrix measurements,
- spin-correlation precision results,
- quantum-information observables,
- entanglement or steering results.

Preserved successful payload:

- LR100: 25 shards / 250000 events
- RL100: 25 shards / 250000 events
- unpolarized: 24 shards / 240000 events
- total: 74 shards / 740000 events

Known failed/missing payload:

- f6f365_ee_unpol_epmum / epmum / shard_0018

The failed shard is intentionally NOT regenerated because Phase 11 replaces
the integration strategy before precision production.

Phase-10 stored LHE event weights were audited and found to be constant and
positive. The reason the campaign is not precision-qualified is the WHIZARD
integration/unweighting quality, including large per-shard integration
uncertainties, shard-to-shard cross-section variation, and severe excess-weight
diagnostics.

Successor:

`phase11_integration_qualification_v1`
EOF

###############################################################################
# Repo-side closeout note.
###############################################################################

cp -a \
  "$PROD_ROOT/PHASE10_QUALIFICATION_ONLY.md" \
  "$REPO_CLOSEOUT/README.md"

cp -a \
  "$SUMMARY_JSON" \
  "$REPO_CLOSEOUT/phase10_closeout_summary.json"

cp -a \
  "$MANIFEST" \
  "$REPO_CLOSEOUT/successful_lhe_manifest.tsv"

sha256sum \
  "$MANIFEST" \
  "$SUMMARY_JSON" \
  "$PROD_ROOT/PHASE10_QUALIFICATION_ONLY.md" \
  > "$EOS_CLOSEOUT/CLOSEOUT_SHA256SUMS"

cp -a \
  "$EOS_CLOSEOUT/CLOSEOUT_SHA256SUMS" \
  "$REPO_CLOSEOUT/"

###############################################################################
# Final validation.
###############################################################################

test -s "$MANIFEST"
test -s "$SUMMARY_JSON"
test -s "$PROD_ROOT/PHASE10_QUALIFICATION_ONLY.md"
test -s "$EOS_CLOSEOUT/CLOSEOUT_SHA256SUMS"
test -s "$REPO_CLOSEOUT/README.md"

echo
echo "============================================================"
echo "PHASE-10 CLOSEOUT COMPLETE"
echo "============================================================"
echo "STATUS=FROZEN_QUALIFICATION_ONLY"
echo "SUCCESSFUL_SHARDS=74"
echo "SUCCESSFUL_EVENTS=740000"
echo "FAILED_SHARD=f6f365_ee_unpol_epmum/epmum/shard_0018"
echo "EOS_CLOSEOUT=$EOS_CLOSEOUT"
echo "REPO_CLOSEOUT=$REPO_CLOSEOUT"
echo "NEXT_STAGE=phase11_integration_qualification_v1"
