#!/usr/bin/env bash
# Ordered driver for the 10k-per-sample shower + Spin-15 qualification gate.
#
# This script intentionally uses explicit phases because HTCondor jobs complete
# asynchronously.  Run one phase, wait for jobs to finish, then run the next.

set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
SC_QIS_CONFIG=${SC_QIS_CONFIG:-$REPO/configs/qis/qualification_500GeV_ISR_sc_v1.yaml}
ISO_QIS_CONFIG=${ISO_QIS_CONFIG:-$REPO/configs/qis/qualification_500GeV_ISR_iso_v1.yaml}
ISO_PRODUCTION_CONFIG=${ISO_PRODUCTION_CONFIG:-$REPO/configs/production/production_500GeV_ISR_iso_validation_v1.csv}

usage() {
  cat <<'USAGE'
Usage: run_next_production_gate.sh PHASE

Phases:
  preflight               Check software, configs, and authoritative manifests.
  submit-iso-production   Submit the matched 8x10k isotropic WHIZARD controls.
  collect-iso-production  Validate and merge completed isotropic WHIZARD jobs.
  submit-showers          Submit SC and ISO 10k explicit-W v3 shower jobs.
  validate-showers        Strictly validate SC and ISO shower products.
  collect-showers         Merge SC and ISO HepMC products by sample.
  spin15                  Build distributions and run the strict Spin-15 gate.
  status                  Print expected paths and current file counts.

The script never waits for Condor jobs.  Use condor_q between submission and
collection/validation phases.
USAGE
}

[[ $# -eq 1 ]] || { usage >&2; exit 2; }
PHASE=$1
cd "$REPO"

read_yaml_value() {
  python3 - "$1" "$2" <<'PY'
import sys
from pathlib import Path
import yaml
value = yaml.safe_load(Path(sys.argv[1]).read_text())
for key in sys.argv[2].split('.'):
    value = value[key]
print(value)
PY
}

SC_MANIFEST=$(read_yaml_value "$SC_QIS_CONFIG" campaign.source_manifest)
ISO_MANIFEST=$(read_yaml_value "$ISO_QIS_CONFIG" campaign.source_manifest)
SC_ROOT=$(read_yaml_value "$SC_QIS_CONFIG" campaign.output_root)
ISO_ROOT=$(read_yaml_value "$ISO_QIS_CONFIG" campaign.output_root)

case "$PHASE" in
  preflight)
    source setup_lxplus.sh
    [[ -x build/qis_lhe_to_hepmc3 ]] || {
      echo "ERROR: build/qis_lhe_to_hepmc3 is missing; run scripts/qis/build_qis.sh" >&2
      exit 1
    }
    for path in \
      "$SC_QIS_CONFIG" \
      "$ISO_QIS_CONFIG" \
      "$ISO_PRODUCTION_CONFIG" \
      scripts/showering/canonicalize_whizard_lhe_for_pythia.py \
      scripts/showering/insert_explicit_w_resonances.py \
      scripts/showering/augment_shower_metadata.py \
      scripts/qis/plot_spin15_distributions.py \
      scripts/qis/validate_spin15_gate.py; do
      [[ -r $path ]] || { echo "ERROR: missing $path" >&2; exit 1; }
    done
    [[ -f $SC_MANIFEST ]] || {
      echo "ERROR: missing SC manifest: $SC_MANIFEST" >&2
      exit 1
    }
    if [[ -f $ISO_MANIFEST ]]; then
      echo "ISO manifest: present"
    else
      echo "ISO manifest: not present yet"
      echo "Next phase: submit-iso-production"
    fi
    python3 -m pytest -q \
      tests/qis/test_spin15_observables.py \
      tests/qis/test_lhe_smoke.py
    echo "PREFLIGHT PASS"
    ;;

  submit-iso-production)
    source setup_lxplus.sh
    python3 scripts/production/submit_production.py \
      --config "$ISO_PRODUCTION_CONFIG" \
      --submit
    ;;

  collect-iso-production)
    source setup_lxplus.sh
    python3 scripts/production/validate_production_outputs.py \
      --config "$ISO_PRODUCTION_CONFIG" \
      --stage final \
      --scan-events 0 \
      --strict
    python3 scripts/production/collect_production.py \
      --config "$ISO_PRODUCTION_CONFIG" \
      --source final \
      --merge \
      --overwrite
    python3 scripts/production/make_production_manifest.py \
      --config "$ISO_PRODUCTION_CONFIG"
    [[ -f $ISO_MANIFEST ]] || {
      echo "ERROR: ISO manifest was not created: $ISO_MANIFEST" >&2
      exit 1
    }
    ;;

  submit-showers)
    source setup_lxplus.sh
    [[ -f $SC_MANIFEST ]] || { echo "ERROR: missing $SC_MANIFEST" >&2; exit 1; }
    [[ -f $ISO_MANIFEST ]] || { echo "ERROR: missing $ISO_MANIFEST" >&2; exit 1; }
    python3 scripts/showering/submit_showering.py \
      --config "$SC_QIS_CONFIG" \
      --submit
    python3 scripts/showering/submit_showering.py \
      --config "$ISO_QIS_CONFIG" \
      --submit
    ;;

  validate-showers)
    source setup_lxplus.sh
    python3 scripts/showering/validate_showering.py \
      --config "$SC_QIS_CONFIG" \
      --strict \
      --checksums
    python3 scripts/showering/validate_showering.py \
      --config "$ISO_QIS_CONFIG" \
      --strict \
      --checksums
    ;;

  collect-showers)
    source setup_lxplus.sh
    python3 scripts/showering/collect_showering.py \
      --config "$SC_QIS_CONFIG" \
      --overwrite
    python3 scripts/showering/collect_showering.py \
      --config "$ISO_QIS_CONFIG" \
      --overwrite
    ;;

  spin15)
    source setup_lxplus.sh
    REPO="$REPO" \
    SC_CONFIG="$SC_QIS_CONFIG" \
    ISO_CONFIG="$ISO_QIS_CONFIG" \
    STRICT_PHYSICS=1 \
      scripts/qis/run_spin15_qualification_gate.sh
    ;;

  status)
    cat <<EOF
SC manifest:
  $SC_MANIFEST
ISO manifest:
  $ISO_MANIFEST
SC shower root:
  $SC_ROOT/shower
ISO shower root:
  $ISO_ROOT/shower
EOF
    for label in SC ISO; do
      root=$SC_ROOT
      [[ $label == ISO ]] && root=$ISO_ROOT
      echo
      echo "$label counts"
      find "$root/shower/hepmc3" -name '*.hepmc3' 2>/dev/null | wc -l | xargs echo "  shower files:"
      find "$root/shower/metadata" -name '*.json' 2>/dev/null | wc -l | xargs echo "  metadata files:"
      find "$root/shower/hepmc3_merged" -name '*.hepmc3' 2>/dev/null | wc -l | xargs echo "  merged files:"
    done
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
