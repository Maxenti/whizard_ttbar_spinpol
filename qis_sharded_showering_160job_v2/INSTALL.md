# Install and run the 160-job sharded shower gate

Repository:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

## 1. Back up current files

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP="$PWD/backups/qis_sharded_showering_v2_${STAMP}"
mkdir -p "$BACKUP"

tar -czf "$BACKUP/pre_sharded_showering_files.tar.gz" \
  condor/qis/pythia_shower.sub \
  configs/qis/qualification_500GeV_ISR_iso_v1.yaml \
  configs/qis/qualification_500GeV_ISR_sc_v1.yaml \
  scripts/qis/run_next_production_gate.sh \
  scripts/qis/run_spin15_qualification_gate.sh \
  scripts/showering/augment_shower_metadata.py \
  scripts/showering/collect_showering.py \
  scripts/showering/run_pythia_shard.sh \
  scripts/showering/submit_showering.py \
  scripts/showering/validate_showering.py
```

## 2. Apply the patch

```bash
patch --dry-run -p1 < qis_sharded_showering_160job_v2.patch
patch -p1 < qis_sharded_showering_160job_v2.patch
```

If the patch does not match, copy the complete `overlay/` tree onto the
repository root with `cp -a overlay/. .` after preserving the backup.

## 3. Permissions and static validation

```bash
chmod +x \
  scripts/qis/run_next_production_gate.sh \
  scripts/qis/run_spin15_qualification_gate.sh \
  scripts/showering/prepare_lhe_shards.py \
  scripts/showering/run_pythia_shard.sh \
  scripts/showering/smoke_test_sharded_worker.sh \
  scripts/showering/submit_showering.py \
  scripts/showering/augment_shower_metadata.py \
  scripts/showering/validate_showering.py \
  scripts/showering/collect_showering.py

python3 -m py_compile \
  scripts/showering/prepare_lhe_shards.py \
  scripts/showering/submit_showering.py \
  scripts/showering/augment_shower_metadata.py \
  scripts/showering/validate_showering.py \
  scripts/showering/collect_showering.py

bash -n \
  scripts/showering/run_pythia_shard.sh \
  scripts/showering/smoke_test_sharded_worker.sh \
  scripts/qis/run_next_production_gate.sh \
  scripts/qis/run_spin15_qualification_gate.sh
```

## 4. Fresh-terminal environment

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
export REPO="$PWD"
export PYTHONDONTWRITEBYTECODE=1
export GATE="$REPO/scripts/qis/run_next_production_gate.sh"
export SHOWER_TOTAL_JOBS=160
export SHOWER_TOTAL_EVENTS_PER_SAMPLE=10000
export SHOWER_SHARD_MODE=resume
export SHOWER_SUBMIT_MODE=resume
source "$REPO/setup_lxplus.sh"
```

## 5. Preflight and plan

```bash
"$GATE" preflight
"$GATE" plan-showers
```

Expected plan:

```text
Total samples:        16
Requested total jobs: 160
Jobs per sample:      10
SC jobs:              80
ISO jobs:             80
Events per sample:    10000
Events per job:       1000..1000
```

## 6. Create deterministic input shards

```bash
"$GATE" prepare-shower-shards
"$GATE" status
```

Expected:

```text
SC input LHE shards:  80
ISO input LHE shards: 80
```

The splitter reads only the first 10,000 source events per sample.  It does not
scan or copy the unused tail of the 100,000-event SC files.

## 7. Full one-event worker smoke test

```bash
"$GATE" smoke-sharded-worker
```

Do not submit the 160 jobs unless this prints `SHARDED WORKER SMOKE PASS`.

## 8. Remove the old monolithic attempts

Only after Steps 5--7 pass:

```bash
condor_rm 16583671
condor_rm 16583672
```

The sharded v2 configs use new EOS output roots, so old partial products are
not mixed with the new campaign.

## 9. Submit 160 jobs

```bash
"$GATE" submit-showers
```

Expected: two clusters with 80 jobs each.  Each job requests:

```text
1 CPU
1000 MB memory
2 GB disk
workday flavour
```

## 10. After completion

```bash
"$GATE" validate-showers
"$GATE" collect-showers
"$GATE" status
"$GATE" spin15
```

The strict validator counts actual HepMC events with `pyhepmc`, checks exact
source ranges and checksums, verifies unique seeds, and requires exactly 10,000
merged events per sample.
