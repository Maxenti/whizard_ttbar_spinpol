#!/usr/bin/env bash
# Ordered driver for the sharded 10k-per-sample shower + Spin-15 gate.
set -euo pipefail

REPO=${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}
SC_QIS_CONFIG=${SC_QIS_CONFIG:-$REPO/configs/qis/qualification_500GeV_ISR_sc_v1.yaml}
ISO_QIS_CONFIG=${ISO_QIS_CONFIG:-$REPO/configs/qis/qualification_500GeV_ISR_iso_v1.yaml}
ISO_PRODUCTION_CONFIG=${ISO_PRODUCTION_CONFIG:-$REPO/configs/production/production_500GeV_ISR_iso_validation_v1.csv}
SHOWER_TOTAL_JOBS=${SHOWER_TOTAL_JOBS:-160}
SHOWER_TOTAL_EVENTS_PER_SAMPLE=${SHOWER_TOTAL_EVENTS_PER_SAMPLE:-10000}
SHOWER_SHARD_MODE=${SHOWER_SHARD_MODE:-resume}
SHOWER_SUBMIT_MODE=${SHOWER_SUBMIT_MODE:-resume}
SHOWER_REQUEST_CPUS=${SHOWER_REQUEST_CPUS:-1}
SHOWER_REQUEST_MEMORY_MB=${SHOWER_REQUEST_MEMORY_MB:-1000}
SHOWER_REQUEST_DISK_GB=${SHOWER_REQUEST_DISK_GB:-2}
SHOWER_JOB_FLAVOUR=${SHOWER_JOB_FLAVOUR:-workday}

usage() {
  cat <<'USAGE'
Usage: run_next_production_gate.sh PHASE

Phases:
  preflight               Check software, configs, manifests, and sharding tests.
  submit-iso-production   Submit the matched isotropic WHIZARD controls.
  collect-iso-production  Validate/finalize/merge isotropic WHIZARD output.
  plan-showers            Print the global job and event-shard plan.
  prepare-shower-shards   Create disjoint LHE shards; read only requested events.
  smoke-sharded-worker    Run one full 1-event local worker smoke test.
  submit-showers          Submit all prepared SC and ISO shower shards.
  validate-showers        Strictly validate every shard and aggregate counts.
  collect-showers         Merge validated HepMC shards by sample.
  spin15                  Build distributions and run the strict Spin-15 gate.
  status                  Print paths, expected counts, and current products.

Adjustable environment variables:
  SHOWER_TOTAL_JOBS=160
      Total SC+ISO Condor jobs.  Must be divisible by the number of selected
      samples.  With 16 samples, 160 means 10 jobs/sample and 1000 events/job.

  SHOWER_TOTAL_EVENTS_PER_SAMPLE=10000
      Total disjoint source events selected for each sample.

  SHOWER_SHARD_MODE=resume|force
      Resume/revalidate existing deterministic input shards, or rebuild them.

  SHOWER_SUBMIT_MODE=resume|force
      Submit only missing/invalid outputs, or replace all shard outputs.

  SHOWER_REQUEST_CPUS=1
  SHOWER_REQUEST_MEMORY_MB=1000
  SHOWER_REQUEST_DISK_GB=2
  SHOWER_JOB_FLAVOUR=workday
      Explicit per-shard HTCondor resources.  These values are passed on every
      submission and therefore override stale configuration or shell defaults.
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

calculate_shower_plan() {
  local assignments
  assignments=$(python3 - \
    "$SC_MANIFEST" \
    "$ISO_MANIFEST" \
    "$SHOWER_TOTAL_JOBS" \
    "$SHOWER_TOTAL_EVENTS_PER_SAMPLE" <<'PY'
import csv
import shlex
import sys
from pathlib import Path

sc_manifest = Path(sys.argv[1])
iso_manifest = Path(sys.argv[2])
total_jobs = int(sys.argv[3])
events_per_sample = int(sys.argv[4])

def count_samples(path: Path) -> int:
    if not path.is_file():
        raise SystemExit(f"missing manifest: {path}")
    with path.open(newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("status") == "success"]
    if not rows:
        raise SystemExit(f"no successful samples in {path}")
    ids = {row["sample_id"] for row in rows}
    if len(ids) != len(rows):
        raise SystemExit(f"duplicate sample rows in {path}")
    return len(ids)

sc_samples = count_samples(sc_manifest)
iso_samples = count_samples(iso_manifest)
total_samples = sc_samples + iso_samples
if total_jobs <= 0:
    raise SystemExit("SHOWER_TOTAL_JOBS must be positive")
if events_per_sample <= 0:
    raise SystemExit("SHOWER_TOTAL_EVENTS_PER_SAMPLE must be positive")
if total_jobs % total_samples:
    raise SystemExit(
        f"SHOWER_TOTAL_JOBS={total_jobs} is not divisible by "
        f"the {total_samples} selected samples"
    )
jobs_per_sample = total_jobs // total_samples
if jobs_per_sample > events_per_sample:
    raise SystemExit(
        f"jobs_per_sample={jobs_per_sample} exceeds events_per_sample={events_per_sample}"
    )
values = {
    "SC_SAMPLES": sc_samples,
    "ISO_SAMPLES": iso_samples,
    "TOTAL_SAMPLES": total_samples,
    "JOBS_PER_SAMPLE": jobs_per_sample,
    "SC_JOBS": sc_samples * jobs_per_sample,
    "ISO_JOBS": iso_samples * jobs_per_sample,
    "EVENTS_PER_SAMPLE": events_per_sample,
    "EVENTS_PER_JOB_MIN": events_per_sample // jobs_per_sample,
    "EVENTS_PER_JOB_MAX": (events_per_sample + jobs_per_sample - 1) // jobs_per_sample,
}
for key, value in values.items():
    print(f"{key}={shlex.quote(str(value))}")
PY
)
  eval "$assignments"
}

print_shower_plan() {
  calculate_shower_plan
  cat <<EOF
SHARDED SHOWER PLAN
  Total samples:            $TOTAL_SAMPLES
  SC samples:               $SC_SAMPLES
  ISO samples:              $ISO_SAMPLES
  Requested total jobs:     $SHOWER_TOTAL_JOBS
  Jobs per sample:          $JOBS_PER_SAMPLE
  SC jobs:                  $SC_JOBS
  ISO jobs:                 $ISO_JOBS
  Events per sample:        $EVENTS_PER_SAMPLE
  Events per job:           $EVENTS_PER_JOB_MIN..$EVENTS_PER_JOB_MAX
  Per-job CPUs:             $SHOWER_REQUEST_CPUS
  Per-job memory MB:        $SHOWER_REQUEST_MEMORY_MB
  Per-job disk GB:          $SHOWER_REQUEST_DISK_GB
  Job flavour:              $SHOWER_JOB_FLAVOUR
  SC output root:           $SC_ROOT/shower
  ISO output root:          $ISO_ROOT/shower
EOF
}

mode_argument() {
  case "$1" in
    resume) echo --resume;;
    force) echo --force;;
    *) echo "ERROR: mode must be resume or force, got $1" >&2; return 2;;
  esac
}

count_matching_files() {
  local directory=$1
  local pattern=$2
  if [[ -d $directory ]]; then
    find "$directory" -type f -name "$pattern" | wc -l
  else
    echo 0
  fi
}

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
      scripts/production/make_production_sindarin.py \
      scripts/showering/prepare_lhe_shards.py \
      scripts/showering/submit_showering.py \
      scripts/showering/run_pythia_shard.sh \
      scripts/showering/canonicalize_whizard_lhe_for_pythia.py \
      scripts/showering/insert_explicit_w_resonances.py \
      scripts/showering/augment_shower_metadata.py \
      scripts/showering/validate_showering.py \
      scripts/showering/collect_showering.py \
      scripts/showering/smoke_test_sharded_worker.sh \
      scripts/qis/plot_spin15_distributions.py \
      scripts/qis/validate_spin15_gate.py; do
      [[ -r $path ]] || { echo "ERROR: missing $path" >&2; exit 1; }
    done
    [[ -f $SC_MANIFEST ]] || { echo "ERROR: missing SC manifest: $SC_MANIFEST" >&2; exit 1; }
    if [[ -f $ISO_MANIFEST ]]; then
      echo "ISO manifest: present"
    else
      echo "ISO manifest: not present yet"
      echo "Next phase: submit-iso-production"
    fi
    python3 scripts/production/make_production_sindarin.py \
      --config "$ISO_PRODUCTION_CONFIG" \
      --check
    python3 -m pytest -q \
      tests/qis/test_spin15_observables.py \
      tests/qis/test_lhe_smoke.py \
      tests/qis/test_lhe_sharding.py
    bash -n scripts/showering/run_pythia_shard.sh
    python3 -m py_compile \
      scripts/showering/prepare_lhe_shards.py \
      scripts/showering/submit_showering.py \
      scripts/showering/augment_shower_metadata.py \
      scripts/showering/validate_showering.py \
      scripts/showering/collect_showering.py
    if [[ -f $ISO_MANIFEST ]]; then
      print_shower_plan
    fi
    echo "PREFLIGHT PASS"
    ;;

  submit-iso-production)
    source setup_lxplus.sh
    python3 scripts/production/make_production_sindarin.py \
      --config "$ISO_PRODUCTION_CONFIG" \
      --output-dir "$REPO/sindarin/production" \
      --force

    python3 - "$ISO_PRODUCTION_CONFIG" "$REPO/sindarin/production" <<'PY'
import csv
import sys
from pathlib import Path

config = Path(sys.argv[1])
template_dir = Path(sys.argv[2])
failures = []
with config.open(newline="") as stream:
    rows = [
        row for row in csv.DictReader(stream)
        if row.get("enabled", "").strip().lower() in {"1", "true", "yes", "on"}
    ]
if len(rows) != 8:
    failures.append(f"expected 8 enabled ISO samples, found {len(rows)}")
for row in rows:
    sample_id = row["sample_id"].strip()
    if "_iso_" not in sample_id:
        failures.append(f"{sample_id}: sample_id is missing '_iso_'")
    if row["spin_correlated"].strip().lower() not in {"0", "false", "no", "off"}:
        failures.append(f"{sample_id}: spin_correlated must be false")
    template = template_dir / f"{sample_id}.sin.in"
    if not template.is_file():
        failures.append(f"{sample_id}: missing template {template}")
        continue
    text = template.read_text()
    for required in (
        "! META spin_mode=iso",
        "?isotropic_decay = true",
        "?diagonal_decay = false",
        "?polarized_events = true",
    ):
        if required not in text:
            failures.append(f"{sample_id}: missing {required!r}")
if failures:
    print("ISO TEMPLATE AUDIT FAILURES:", file=sys.stderr)
    for failure in failures:
        print(f"  - {failure}", file=sys.stderr)
    raise SystemExit(1)
print(f"ISO TEMPLATE AUDIT PASS: {len(rows)} templates")
PY

    python3 scripts/production/submit_production.py \
      --config "$ISO_PRODUCTION_CONFIG" \
      --template-dir "$REPO/sindarin/production" \
      --submit
    ;;

  collect-iso-production)
    source setup_lxplus.sh
    python3 scripts/production/make_production_manifest.py --config "$ISO_PRODUCTION_CONFIG"
    python3 scripts/production/validate_production_outputs.py \
      --config "$ISO_PRODUCTION_CONFIG" --stage raw --scan-events 0 --strict
    python3 scripts/production/calibrate_decay_normalization.py --config "$ISO_PRODUCTION_CONFIG"
    python3 scripts/production/finalize_forced_decay_lhe.py \
      --config "$ISO_PRODUCTION_CONFIG" --overwrite
    python3 scripts/production/make_production_manifest.py --config "$ISO_PRODUCTION_CONFIG"
    python3 scripts/production/collect_production.py \
      --config "$ISO_PRODUCTION_CONFIG" --source final --merge --overwrite
    python3 scripts/production/make_production_manifest.py --config "$ISO_PRODUCTION_CONFIG"
    python3 scripts/production/validate_production_outputs.py \
      --config "$ISO_PRODUCTION_CONFIG" --stage final --scan-events 0 \
      --require-merged --strict
    [[ -f $ISO_MANIFEST ]] || { echo "ERROR: ISO manifest was not created: $ISO_MANIFEST" >&2; exit 1; }
    echo "ISO PRODUCTION COLLECTION PASS"
    ;;

  plan-showers)
    print_shower_plan
    ;;

  prepare-shower-shards)
    source setup_lxplus.sh
    print_shower_plan
    shard_mode=$(mode_argument "$SHOWER_SHARD_MODE")
    python3 scripts/showering/prepare_lhe_shards.py \
      --config "$SC_QIS_CONFIG" \
      --jobs-per-sample "$JOBS_PER_SAMPLE" \
      --total-events-per-sample "$EVENTS_PER_SAMPLE" \
      "$shard_mode"
    python3 scripts/showering/prepare_lhe_shards.py \
      --config "$ISO_QIS_CONFIG" \
      --jobs-per-sample "$JOBS_PER_SAMPLE" \
      --total-events-per-sample "$EVENTS_PER_SAMPLE" \
      "$shard_mode"
    ;;

  smoke-sharded-worker)
    scripts/showering/smoke_test_sharded_worker.sh
    ;;

  submit-showers)
    source setup_lxplus.sh
    print_shower_plan
    submit_mode=$(mode_argument "$SHOWER_SUBMIT_MODE")
    python3 scripts/showering/submit_showering.py \
      --config "$SC_QIS_CONFIG" \
      --expected-jobs "$SC_JOBS" \
      --request-cpus "$SHOWER_REQUEST_CPUS" \
      --request-memory-mb "$SHOWER_REQUEST_MEMORY_MB" \
      --request-disk-gb "$SHOWER_REQUEST_DISK_GB" \
      --job-flavour "$SHOWER_JOB_FLAVOUR" \
      "$submit_mode" \
      --submit
    python3 scripts/showering/submit_showering.py \
      --config "$ISO_QIS_CONFIG" \
      --expected-jobs "$ISO_JOBS" \
      --request-cpus "$SHOWER_REQUEST_CPUS" \
      --request-memory-mb "$SHOWER_REQUEST_MEMORY_MB" \
      --request-disk-gb "$SHOWER_REQUEST_DISK_GB" \
      --job-flavour "$SHOWER_JOB_FLAVOUR" \
      "$submit_mode" \
      --submit
    ;;

  validate-showers)
    source setup_lxplus.sh
    python3 scripts/showering/validate_showering.py \
      --config "$SC_QIS_CONFIG" --strict --checksums
    python3 scripts/showering/validate_showering.py \
      --config "$ISO_QIS_CONFIG" --strict --checksums
    ;;

  collect-showers)
    source setup_lxplus.sh
    python3 scripts/showering/collect_showering.py \
      --config "$SC_QIS_CONFIG" --overwrite
    python3 scripts/showering/collect_showering.py \
      --config "$ISO_QIS_CONFIG" --overwrite
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
    print_shower_plan
    for label in SC ISO; do
      root=$SC_ROOT
      expected_jobs=$SC_JOBS
      [[ $label == ISO ]] && { root=$ISO_ROOT; expected_jobs=$ISO_JOBS; }
      echo
      echo "$label counts (expected shower shards: $expected_jobs)"
      echo "  input LHE shards: $(count_matching_files "$root/shower/input_shards" '*.lhe')"
      echo "  shower files:     $(count_matching_files "$root/shower/hepmc3" '*.hepmc3')"
      echo "  metadata files:   $(count_matching_files "$root/shower/metadata" '*.json')"
      echo "  merged files:     $(count_matching_files "$root/shower/hepmc3_merged" '*.hepmc3')"
    done
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
