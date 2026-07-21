#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
QUALIFICATION_ROOT=${QUALIFICATION_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/spin15_gate_10k_sharded_v2}
CONFIG=${CONFIG:-$REPO/configs/qis/paper_spin_500GeV.yaml}
OUTPUT_ROOT=${OUTPUT_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/paper_spin/paper_spin_500GeV_$(date -u +%Y%m%dT%H%M%SZ)}

cd "$REPO"
source "$REPO/setup_lxplus.sh"

mkdir -p "$OUTPUT_ROOT/provenance"

python3 scripts/qis/preflight_paper_spin.py \
  --qualification-root "$QUALIFICATION_ROOT" \
  --output-root "$OUTPUT_ROOT" \
  --config "$CONFIG" \
  | tee "$OUTPUT_ROOT/provenance/preflight.json"

python3 scripts/qis/snapshot_spin15_baseline.py \
  --root "$QUALIFICATION_ROOT" \
  --output "$OUTPUT_ROOT/provenance/baseline_before.json"

python3 scripts/qis/run_paper_spin_closure.py synthetic \
  --events "${SYNTHETIC_EVENTS:-200000}" \
  --seed "${SYNTHETIC_SEED:-20260721}" \
  --output "$OUTPUT_ROOT/synthetic_closure.json"

python3 scripts/qis/run_paper_spin_analysis.py \
  --qualification-root "$QUALIFICATION_ROOT" \
  --output-root "$OUTPUT_ROOT" \
  --config "$CONFIG"

python3 scripts/qis/validate_paper_spin.py \
  --analysis-root "$OUTPUT_ROOT" \
  --config "$CONFIG" \
  --synthetic-closure "$OUTPUT_ROOT/synthetic_closure.json" \
  --output "$OUTPUT_ROOT/paper_spin_validation.json"

python3 scripts/qis/snapshot_spin15_baseline.py \
  --root "$QUALIFICATION_ROOT" \
  --output "$OUTPUT_ROOT/provenance/baseline_before.json" \
  --verify

find "$OUTPUT_ROOT" \
  -type f \
  ! -path "$OUTPUT_ROOT/provenance/SHA256SUMS.txt" \
  -print0 | sort -z | xargs -0 sha256sum \
  > "$OUTPUT_ROOT/provenance/SHA256SUMS.txt"

printf 'Paper-grade spin analysis complete:\n  %s\n' "$OUTPUT_ROOT"
