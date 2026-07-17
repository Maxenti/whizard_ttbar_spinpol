#!/usr/bin/env bash
#
# Build and validate the complete 15-observable ttbar polarization/spin package
# for the 10k-per-sample production qualification.
#
# Preconditions:
#   1. SC and ISO authoritative LHE manifests exist.
#   2. SC and ISO shower jobs have completed.
#   3. collect_showering.py has produced hepmc3_merged/*.hepmc3.
#
# The gate builds four matched ntuple datasets:
#   lhe_sc, hepmc_sc, lhe_iso, hepmc_iso
# and produces all 15 distributions for every sample plus coefficient and gate
# tables.

set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
SC_CONFIG=${SC_CONFIG:-$REPO/configs/qis/qualification_500GeV_ISR_sc_v1.yaml}
ISO_CONFIG=${ISO_CONFIG:-$REPO/configs/qis/qualification_500GeV_ISR_iso_v1.yaml}
SC_PRODUCTION_CONFIG=${SC_PRODUCTION_CONFIG:-$REPO/configs/production/production_500GeV_ISR_sc_v1.csv}
ISO_PRODUCTION_CONFIG=${ISO_PRODUCTION_CONFIG:-$REPO/configs/production/production_500GeV_ISR_iso_validation_v1.csv}
MAX_EVENTS=${MAX_EVENTS:-10000}
STRICT_PHYSICS=${STRICT_PHYSICS:-1}
FORCE=${FORCE:-0}
PLOT_FORMATS=${PLOT_FORMATS:-"png pdf"}

read_yaml_value() {
  local config=$1
  local expression=$2
  python3 - "$config" "$expression" <<'PY'
import sys
from pathlib import Path
import yaml

path = Path(sys.argv[1])
keys = sys.argv[2].split(".")
payload = yaml.safe_load(path.read_text())
value = payload
for key in keys:
    value = value[key]
print(value)
PY
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -d $REPO ]] || die "repository does not exist: $REPO"
[[ -f $SC_CONFIG ]] || die "missing SC QIS config: $SC_CONFIG"
[[ -f $ISO_CONFIG ]] || die "missing ISO QIS config: $ISO_CONFIG"
[[ -f $SC_PRODUCTION_CONFIG ]] || die "missing SC production config: $SC_PRODUCTION_CONFIG"
[[ -f $ISO_PRODUCTION_CONFIG ]] || die "missing ISO production config: $ISO_PRODUCTION_CONFIG"
(( MAX_EVENTS > 0 )) || die "MAX_EVENTS must be positive"

SC_MANIFEST=${SC_MANIFEST:-$(read_yaml_value "$SC_CONFIG" campaign.source_manifest)}
ISO_MANIFEST=${ISO_MANIFEST:-$(read_yaml_value "$ISO_CONFIG" campaign.source_manifest)}
SC_QIS_ROOT=$(read_yaml_value "$SC_CONFIG" campaign.output_root)
ISO_QIS_ROOT=$(read_yaml_value "$ISO_CONFIG" campaign.output_root)
SC_HEPMC_ROOT=${SC_HEPMC_ROOT:-$SC_QIS_ROOT/shower/hepmc3_merged}
ISO_HEPMC_ROOT=${ISO_HEPMC_ROOT:-$ISO_QIS_ROOT/shower/hepmc3_merged}
OUT=${OUT:-/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/spin15_gate_10k_v1}

[[ -f $SC_MANIFEST ]] || die "missing SC manifest: $SC_MANIFEST"
[[ -f $ISO_MANIFEST ]] || die "missing ISO manifest: $ISO_MANIFEST"
[[ -d $SC_HEPMC_ROOT ]] || die "missing SC merged HepMC directory: $SC_HEPMC_ROOT"
[[ -d $ISO_HEPMC_ROOT ]] || die "missing ISO merged HepMC directory: $ISO_HEPMC_ROOT"
[[ $OUT == /eos/* || $OUT == /tmp/* ]] || die "OUT must be on EOS or under /tmp"

if [[ -e $OUT ]]; then
  if [[ $FORCE == 1 ]]; then
    rm -rf "$OUT"
  else
    die "output exists: $OUT; set FORCE=1 to replace"
  fi
fi

mkdir -p \
  "$OUT/ntuples/lhe_sc" \
  "$OUT/ntuples/hepmc_sc" \
  "$OUT/ntuples/lhe_iso" \
  "$OUT/ntuples/hepmc_iso" \
  "$OUT/spin15" \
  "$OUT/gate" \
  "$OUT/provenance"

export PYTHONDONTWRITEBYTECODE=1

TABLE_OPTIONS=(--no-root)
if ! python3 - <<'PY' >/dev/null 2>&1
import pyarrow
PY
then
  echo "WARNING: pyarrow is unavailable; writing CSV only."
  TABLE_OPTIONS+=(--no-parquet)
fi

run_ntuples() {
  local label=$1
  local config=$2
  local manifest=$3
  local input_format=$4
  local output_dir=$5
  local input_root=${6:-}

  echo
  echo "======================================================================"
  echo "NTUPLES: $label"
  echo "======================================================================"

  command=(
    python3 "$REPO/scripts/qis/make_qis_ntuples.py"
    --config "$config"
    --manifest "$manifest"
    --input-format "$input_format"
    --output-dir "$output_dir"
    --max-events "$MAX_EVENTS"
    "${TABLE_OPTIONS[@]}"
  )
  if [[ -n $input_root ]]; then
    command+=(--input-root "$input_root")
  fi
  "${command[@]}" | tee "$OUT/provenance/ntuples_${label}.log"
}

run_ntuples lhe_sc "$SC_CONFIG" "$SC_MANIFEST" lhe \
  "$OUT/ntuples/lhe_sc"
run_ntuples hepmc_sc "$SC_CONFIG" "$SC_MANIFEST" hepmc3 \
  "$OUT/ntuples/hepmc_sc" "$SC_HEPMC_ROOT"
run_ntuples lhe_iso "$ISO_CONFIG" "$ISO_MANIFEST" lhe \
  "$OUT/ntuples/lhe_iso"
run_ntuples hepmc_iso "$ISO_CONFIG" "$ISO_MANIFEST" hepmc3 \
  "$OUT/ntuples/hepmc_iso" "$ISO_HEPMC_ROOT"

read -r -a FORMAT_ARGS <<<"$PLOT_FORMATS"

python3 "$REPO/scripts/qis/plot_spin15_distributions.py" \
  --dataset "lhe_sc=$OUT/ntuples/lhe_sc" \
  --dataset "hepmc_sc=$OUT/ntuples/hepmc_sc" \
  --dataset "lhe_iso=$OUT/ntuples/lhe_iso" \
  --dataset "hepmc_iso=$OUT/ntuples/hepmc_iso" \
  --output-dir "$OUT/spin15" \
  --bins 40 \
  --formats "${FORMAT_ARGS[@]}" \
  --strict \
  2>&1 | tee "$OUT/provenance/plot_spin15.log"

VALIDATOR_ARGS=(
  python3 "$REPO/scripts/qis/validate_spin15_gate.py"
  --coefficients "$OUT/spin15/spin15_coefficients.csv"
  --output-dir "$OUT/gate"
  --production-config "$SC_PRODUCTION_CONFIG"
  --production-config "$ISO_PRODUCTION_CONFIG"
)
if [[ $STRICT_PHYSICS == 1 ]]; then
  VALIDATOR_ARGS+=(--strict-physics)
fi
"${VALIDATOR_ARGS[@]}" 2>&1 | tee "$OUT/provenance/validate_spin15.log"

cp -a \
  "$SC_CONFIG" \
  "$ISO_CONFIG" \
  "$SC_PRODUCTION_CONFIG" \
  "$ISO_PRODUCTION_CONFIG" \
  "$REPO/scripts/qis/plot_spin15_distributions.py" \
  "$REPO/scripts/qis/validate_spin15_gate.py" \
  "$REPO/scripts/qis/run_spin15_qualification_gate.sh" \
  "$OUT/provenance/"

find "$OUT" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > "$OUT/provenance/SHA256SUMS.txt"

cat <<EOF

SPIN15 QUALIFICATION PRODUCTS
  Root:          $OUT
  Distributions: $OUT/spin15/per_sample
  Coefficients:  $OUT/spin15/spin15_coefficients.csv
  Gate report:   $OUT/gate/spin15_gate_report.md
  Gate JSON:     $OUT/gate/spin15_gate_summary.json
EOF
